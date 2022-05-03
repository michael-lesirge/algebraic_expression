from algebraic_expression import _Term as Term
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

    return [Term(term) for term in updated_input.split(" ")]


class Expression:
    def __init__(self, value="", *, terms=None, _combine=True):
        self._terms: list[Term]

        if terms is None:
            self._terms = parse_expression(value)
        else:
            self._terms = terms

        if _combine:
            # this filters out all zero-terms, combines like terms, and sorts terms into standard form
            self._terms = combine_like_terms(self._terms)
        self._terms.sort(key=term_sort_key, reverse=True)

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
        variables: dict must contain all variables that are in equation
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
        if first_neg is true then the grf will cancel the negative out
        """
        if len(self._terms) == 0:
            return Term()

        coefficients = [int(val) for val in self._terms]

        gc_coefficient = gcd(*coefficients)

        if all([i < 1 for i in coefficients]):
            gc_coefficient *= -1

        elif first_neg and self._terms[0].coefficient < 0:
            gc_coefficient *= -1

        return Term(coefficient=gc_coefficient,
                    bases_exponents=min_common_num([val.bases_exponents for val in self._terms]))

    def simplifying(self) -> tuple["Expression", tuple["Expression", "Expression"]]:
        """
        returns simplified (according to math class) version of expression
        """
        expression = self.copy()

        gcf = expression.gcf()
        expression /= gcf

        if len(expression) == 2:
            expression = Expression(terms=expression[0] + [Term()] + expression[1], _combine=False)

        if len(expression) == 3:
            split = mul_add(int(expression[0] * expression[2]), int(expression[1]))
            if split is None:
                raise Exception("Expression could not be simplified")

            x1, x2 = split

            expression = Expression(
                terms=[expression._terms[0]] +
                      [Term(coefficient=x1, bases_exponents=expression[1].bases_exponents),
                       Term(coefficient=x2, bases_exponents=expression[1].bases_exponents)] + [expression[2]],
                _combine=False
            )

        if len(expression) == 4:
            left, right = expression[0:2], expression[2:4]

            left_gcf, right_gcf = left.gcf(first_neg=True), right.gcf(first_neg=True)

            left /= left_gcf
            right /= right_gcf

            if left != right:
                raise Exception("left and right do not match")

            return Expression(terms=[gcf]), (left, Expression(terms=[left_gcf, right_gcf]))

    def copy(self) -> "Expression":
        """
        makes copy of expression
        """
        return Expression(terms=[term.copy() for term in self._terms])

    def combine_like_terms(self, *others):
        combined = Expression()
        for term in self._terms:
            combined += term

        for other in others:
            if isinstance(other, int):
                other = Term(other)

            if isinstance(other, Term):
                combined += other
            elif isinstance(other, Expression):
                combined += other

        return combined

    def is_standard_form(self) -> bool:
        """
        returns if expression is in standard form
        """
        for index, term in enumerate(self._terms):
            if len(term.bases_exponents) == 0:
                if 0 == len(self._terms) - 1:
                    return False
            elif term.bases_exponents[min(term.bases_exponents)] != (len(self._terms) - 1) - index:
                return False
        return True

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
        return item in self._terms

    def __add__(self, other) -> "Expression":
        if isinstance(other, int):
            other = Term(other)

        if isinstance(other, Term):
            new = self._terms.copy()
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
        if isinstance(other, int):
            other = Term(other)

        if isinstance(other, Term):
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
            return sum([safe_int(self / other_term) for other_term in other._terms], start=Expression())
        return NotImplemented

    def __hash__(self):
        return hash(tuple(self._terms))

    def __neg__(self):
        return self * -1

    def __pow__(self, power, modulo=None) -> "Expression":
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


def term_sort_key(term: "Term") -> int:
    """
    used as a key for sorting terms in expressions into standard form
    """
    if term.bases_exponents == {}:
        return -1
    first = min(term.bases_exponents.keys())
    return term.bases_exponents[first]


def combine_like_terms(terms: list["Term"], remove_zero_terms=True) -> list["Term"]:
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
        elif not (term.is_zero_term() and remove_zero_terms):
            new.append(term)
            d[hash_dict] = i
            i += 1

    return new
