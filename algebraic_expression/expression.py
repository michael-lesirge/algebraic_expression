from algebraic_expression import Term
from algebraic_expression.utils import safe_int, gcd, min_common_num, sqrt


def parse_expression(user_input: str) -> list[Term]:
    """
    spits an input into each section and converts it to term
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
    simplfy = True
    sort = True

    def __init__(self, value="", *, terms=None, combine_terms=simplfy, sort=sort):
        # terms = list(terms or ())
        if terms:
            terms = [Term(term) for term in terms]
        else:
            terms = []

        if isinstance(value, str):
            terms.extend(parse_expression(value))
        elif isinstance(value, (int, float)):
            terms.append(Term(value))
        else:
            raise Exception(f"invalid type {type(value)} for Expression")

        if combine_terms:
            # combines all terms with same bases/exsponents
            # example: combine_like_terms([6x**2, 3x, 6x, 3]) = [6x**2, 9x, 3]
            terms = combine_like_terms(terms)

        if sort:
            # sorts list of terms into standard form
            terms = order(terms)

        # Expressions are imutable
        self.__str_cache = None
        self.terms: tuple[Term] = tuple(terms)

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

        for term in self.terms:
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
        final = ""
        for term in self.terms:
            if plus:
                final += "+"
            final += "(" + term.str_equation() + ")"
            plus = True
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
            return Expression(terms=list(map(other, self.terms)))
        elif isinstance(other, (Term, int, float)):
            return Expression(terms=[(term * other) for term in self.terms])
        elif isinstance(other, Expression):
            return list(map(self.distribute, other.terms))
        return NotImplemented

    @property
    def gcf(self) -> Term:
        """
        returns the greatest common factor of all terms
        if first_neg is true then the gcf will cancel the first negative out
        """
        if len(self.terms) == 0:
            return Term()

        coefficients = [val.coefficient for val in self.terms]

        gc_coefficient = gcd(*coefficients)

        return Term(coefficient=gc_coefficient,
                    bases_exponents=min_common_num([val.bases_exponents for val in self.terms]))


    @property
    def is_quadratic_equation(self):
        """
        check if expression is quadractic equation: Ax**2+Bx+C
        """
        if (len(self) != 3) or (len(self[0].bases) != 1):
            return False
        var = self[0].bases[0]
        return self[0].bases_exponents == {var: 2} and self[1].bases_exponents == {var: 1} and self[2].bases_exponents == {}


    def quadratic_equation(self, *, round_to=None) -> set[float, float]:
        """
        runs quadratic equation expression's coefficients

        Ax**2+Bx+C

        A, B, C	= constants, where a ≠ 0
        x = unknown

        x = (-B ± sqrt(B^2 - 4AC) / 2A
        """
        if not self.is_quadratic_equation:
            raise Expression("Expression must be quadratic eqution")

        a, b, c = [term.coefficient for term in self.terms]

        left = (-b)
        right = (sqrt((b ** 2) - (4 * a * c)))
        div = (2 * a)

        lr_p = (left + right)
        lr_m = (left - right)

        left_div = (lr_p / div)
        right_div = (lr_m / div)
        
        if round_to:
            left_div = round(left_div, round_to)
            right_div =round(right_div, round_to)
        return {left_div, right_div}

    def __contains__(self, item) -> bool:
        """
        checks if terms is in expression
        """
        return item in self.terms

    def __bool__(self) -> bool:
        return bool(self.terms)

    def __add__(self, other) -> "Expression":
        if isinstance(other, (int, float)):
            other = Term(other)

        if isinstance(other, Term):
            new = list(self.terms)
            for index, term in enumerate(new):
                if other.same_bases_and_exponents(term):
                    new[index] = term + other
                    return Expression(terms=new)
            return Expression(terms=(new + [other]))

        elif isinstance(other, Expression):
            return sum(other.terms, start=self)
        return NotImplemented

    def __radd__(self, other):
        return self + other

    def __sub__(self, other) -> "Expression":
        return self + (-other)

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            other = Term(other)
        elif isinstance(other, Term):
            other = Expression(terms=[other])
        return other - self

    def __mul__(self, other) -> "Expression":
        """
        multiplication is just the sum of other disputed to self or the other way around
        """
        if isinstance(other, (int, float, Term)):
            return self.distribute(other)
        if isinstance(other, Expression):
            return sum(other.distribute(self), start=Expression())
        return NotImplemented

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            other = Term(other)
        if isinstance(other, Term):
            return Expression(terms=[safe_int(term / other) for term in self.terms])
        elif isinstance(other, Expression):
            if len(other) == 1:
                return self / other[0]
            # TODO
            # We did not do this in math class
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            other = Term(other)
        elif isinstance(other, Term):
            other = Expression(terms=[other])
        return other / self

    def __hash__(self):
        return hash(self.terms)

    def __iter__(self):
        return iter(self.terms)

    def __neg__(self):
        return self * -1

    def __pow__(self, power, modulo=None) -> "Expression":
        if modulo:
            return NotImplemented
        current = self
        for _ in range(power - 1):
            current *= self
        return current

    def __eq__(self, other) -> bool:
        if isinstance(other, Expression):
            return self.terms == other.terms
        return False

    def __ne__(self, other) -> bool:
        if isinstance(other, Expression):
            return self.terms != other.terms
        return True

    def __getitem__(self, key: int | slice):
        if isinstance(key, int):
            return self.terms[key]
        elif isinstance(key, slice):
            return Expression(terms=self.terms[key])
        return NotImplemented

    def __len__(self) -> int:
        return len(self.terms)

    def __str__(self) -> str:
        if self.__str_cache is None:
            self.__str_cache = self.str_plus()
        return self.__str_cache

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(terms={self.terms})"


def order(terms: list[Term]) -> list[Term]:
    letters = {}
    for term in terms:
        key_list = term.bases
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
