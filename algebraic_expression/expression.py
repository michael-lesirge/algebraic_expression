from algebraic_expression import Term
from algebraic_expression.utils import safe_int, gcd, min_common_num, mul_add, sqrt


def parse_expression(user_input: str) -> list["Term"]:
    """
    spits an input into each term and converts it to term
    """
    updated_input = ""
    swapper = {"+": " ", "-": " -"}

    last = None
    for char in user_input:
        if last in ["*", "^"]:
            updated_input += char
        else:
            updated_input += swapper.get(char, char)
        last = char
    return [Term(term) for term in updated_input.split(" ") if term not in ("", " ")]


class Expression:
    """
    algebraic expression class
    contains a list of terms
    """
    pre_sorted = False

    def __init__(self, value="", *, terms=None, combine_terms=True, sort=not pre_sorted):
        terms = terms or list()

        if isinstance(value, str):
            terms.extend(parse_expression(value))
        elif isinstance(value, int):
            terms.append(Term(value))

        if combine_terms:
            # combines like terms
            terms = combine_like_terms(terms)

        if sort:
            # sorts list of terms into standard form
            terms = order(terms)

        self._terms: tuple[Term] = tuple(terms)

    def str_plus(self, *, plus=False, braces=False, sep="", html=False, up_symbol="**", **kwargs):
        """
        gives options for how you want string to look
        plus adds a plus sign at beginning if there is no negative sign
        html replace x**n with x<sup>n</sup> for displaying on webpages
        """

        final = []
        if braces:
            if plus:
                final.append("+")
                plus = False
            final.append("(")

        for term in self._terms:
            final.append(term.str_plus(plus=plus, html=html, up_symbol=up_symbol, **kwargs))
            plus = True

        if braces:
            final.append(")")

        final = sep.join(final)
        return final

    def str_equation(self, *, plus=False) -> str:
        """
        returns an equation of itself that could be run by python
        """
        first = not plus
        final = ""
        for term in self._terms:
            if not first:
                final += "+"
            final += "(" + term.str_equation(plus=(not first)) + ")"
            first = False
        return final

    def var_equals(self, variables: dict[str: int]) -> int:
        """
        variables dict must contain all variables that are in equation
        runs the equation with eval and returns answer
        """
        return eval(self.str_equation(), variables)

    def distribute(self, other) -> "Expression" or list["Expression"]:
        """
        distributes other to all values in self
        if it is a function it runs it on all values
        """
        if callable(other):
            return Expression(terms=list(map(other, self._terms)))
        elif isinstance(other, (Term, int)):
            return Expression(terms=[(term * other) for term in self._terms])
        elif isinstance(other, Expression):
            return list(map(self.distribute, other._terms))
        return NotImplemented

    def gcf(self, first_neg=False) -> Term:
        """
        returns the greatest common factor of all terms
        if first_neg is true then the gcf will cancel the first negative out
        """
        if len(self._terms) == 0:
            return Term()

        coefficients = [val.coefficient for val in self._terms]

        gc_coefficient = gcd(*coefficients)

        if all([i < 1 for i in coefficients]):
            gc_coefficient *= -1
        elif first_neg and self._terms[0].coefficient < 0:
            gc_coefficient *= -1

        return Term(coefficient=gc_coefficient,
                    bases_exponents=min_common_num([val.bases_exponents for val in self._terms]))

    def quadratic_equation(self, *, show_steps=False, round_to=None):
        """
        runs quadratic equation expression's coefficients
        """
        a, b, c = tuple(map(int, self._terms))

        left = (-1 * b)
        right = safe_int(sqrt((b ** 2) - (4 * a * c)), round_to=round_to)
        div = (2 * a)

        lr_p = (left + right)
        lr_m = (left - right)

        left_div = safe_int(lr_p / div, round_to=round_to)
        right_div = safe_int(lr_m / div, round_to=round_to)

        if show_steps:
            print(lr_p, "/", div, " | ", lr_m, "/", div, sep="")

        return {left_div, right_div}

    def __contains__(self, item) -> bool:
        """
        checks if terms is in expression
        """
        return item in self._terms

    def __add__(self, other) -> "Expression":
        if isinstance(other, int):
            other = Term(other)

        if isinstance(other, Term):
            new = list(self._terms)
            for index, term in enumerate(new):
                if other.same_bases_and_exponents(term):
                    new[index] = term + other
                    return Expression(terms=new)
            return Expression(terms=(new + [other]))

        elif isinstance(other, Expression):
            return sum(other._terms, start=self)
        return NotImplemented

    def __sub__(self, other) -> "Expression":
        return self + (-other)

    def __mul__(self, other) -> "Expression":
        """
        multiplication is just the sum of other disputed to self or the other way around
        """
        if isinstance(other, (int, Term)):
            return self.distribute(other)
        if isinstance(other, Expression):
            return sum(other.distribute(self), start=Expression())
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, int):
            other = Term(other)

        if isinstance(other, Term):
            return Expression(terms=[safe_int(term / other) for term in self._terms])
        elif isinstance(other, Expression):
            return sum([safe_int(self / other_term) for other_term in other._terms],
                       start=Expression())
        return NotImplemented

    def __hash__(self):
        return hash(tuple(self._terms))

    def __iter__(self):
        return iter(self._terms)

    def __neg__(self):
        return self * -1

    def __pow__(self, power, modulo=None) -> "Expression":
        if modulo:
            return NotImplemented
        current = self
        for i in range(power - 1):
            current *= self
        return current

    def __eq__(self, other) -> bool:
        if isinstance(other, Expression):
            return self._terms == other._terms
        return False

    def __ne__(self, other) -> bool:
        if isinstance(other, Expression):
            return self._terms != other._terms
        return True

    def __getitem__(self, key) -> Term or "Expression":
        if isinstance(key, int):
            return self._terms[key]
        elif isinstance(key, slice):
            return Expression(terms=self._terms[key])
        return NotImplemented

    def __len__(self) -> int:
        return len(self._terms)

    def __str__(self) -> str:
        return self.str_plus()

    def __repr__(self) -> str:
        return f"Expression(terms={self._terms})"


def order(terms: list[Term]) -> list[Term]:
    letters = {}
    for term in terms:
        key_list = term.get_bases()
        if key_list:
            key = key_list[0]
        else:
            key = '~'
        letters[key] = letters.get(key, []) + [term]
    new = []
    for letter in sorted(letters.keys()):
        new.extend(sorted(letters[letter],
                          key=lambda lterm: lterm.bases_exponents[letter] if letter != '~' else lterm.coefficient,
                          reverse=True))
    return new


def combine_like_terms(terms: list["Term"]) -> list["Term"]:
    """
    combines like terms
    """
    d = {}
    new = []
    i = 0
    for term in terms:
        hash_dict = tuple(term.bases_exponents.items())
        if hash_dict in d:
            new[d[hash_dict]] += term
        elif not term.is_zero_term():
            new.append(term)
            d[hash_dict] = i
            i += 1

    return new
