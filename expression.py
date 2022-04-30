from calcs.expression_exponents import Term
from calcs.expression_exponents.utils import safe_int, gcd, min_common_num, mul_add, combine_like_terms


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
    def __init__(self, value="", *, terms=None):
        self.terms: list[Term]

        if terms is None:
            self.terms = parse_expression(value)
        else:
            self.terms = terms

        self.terms = combine_like_terms(self.terms)
        self.terms.sort(key=term_sort_key, reverse=True)

    def str_plus(self, plus=False, braces=False, sep="", **kwargs):
        """
        gives options for how you want string to look
        plus adds a plus sign at beginning if there is no negative sign
        kwargs go to superscript function. def superscript(html=False, up_symbol="**"):
        """
        final = []
        first = not plus
        for term in self.terms:
            final.append(term.str_plus(plus=(not first), **kwargs))
            first = False

        final = sep.join(final)
        if braces:
            final = "(" + final + ")"
        return final

    def str_equation(self, plus=False) -> str:
        """
        returns an equation of itself that could be run by python interpret with eval
        """
        first = not plus
        final = ""
        for term in self.terms:
            if not first:
                final += "+"
            final += "(" + term.str_equation(plus=(not first)) + ")"
            first = False
        return final

    def var_equals(self, variables: dict[str: int]) -> int:
        """
        variables: dict must contain all variables that are in equation
        runs the equation with eval
        """
        return eval(self.str_equation(), variables)

    def distribute(self, other) -> "Expression" or list["Expression"]:
        """
        distributes other to all values in self
        if it is a function it runs it on all values
        """
        if callable(other):
            return Expression(terms=list(map(other, self.terms)))
        elif isinstance(other, (Term, int)):
            return Expression(terms=[(term * other) for term in self.terms])
        elif isinstance(other, Expression):
            return list(map(self.distribute, other.terms))
        return NotImplemented

    def gcf(self, first_neg=False) -> Term:
        """
        returns the greatest common factor of all terms
        if first_neg is true then the grf will cancel the negative out
        """
        if len(self.terms) == 0:
            return Term()

        coefficients = [val.coefficient for val in self.terms]

        gc_coefficient = gcd(*coefficients)

        if all([i < 1 for i in coefficients]):
            gc_coefficient *= -1

        if first_neg and self.terms[0].coefficient < 0:
            gc_coefficient *= -1

        return Term(coefficient=gc_coefficient,
                    bases_exponents=min_common_num([val.bases_exponents for val in self.terms]))

    def simplifying(self) -> tuple[Term, tuple["Expression", "Expression"]]:
        """
        returns simplified (according to math class) version of expression
        """
        expression = self.copy()

        gcf = expression.gcf()
        expression /= gcf

        if len(expression) == 2:
            expression = Expression(terms=expression[0] + [Term()] + expression[1])

        if len(expression) == 3:
            split = mul_add(expression[0] * expression[2], expression[1])

            if split is None:
                raise Exception("Expression could not be simplified")

            x1, x2 = split
            expression = Expression(
                terms=[expression.terms[0]] +
                      [Term(coefficient=x1, bases_exponents=expression[1].bases_exponents),
                       Term(coefficient=x2, bases_exponents=expression[1].bases_exponents)] + [expression[2]]
            )

        if len(expression) == 4:
            left, right = expression[0:2], expression[2:4]

            left_gcf, right_gcf = left.gcf(first_neg=True), right.gcf(first_neg=True)

            left /= left_gcf
            right /= right_gcf

            if left != right:
                raise Exception("left and right do not match")

            return gcf, (left, Expression(terms=[left_gcf, right_gcf]))

    def copy(self) -> "Expression":
        """
        makes copy of expression
        """
        return Expression(terms=[term.copy() for term in self.terms])

    def combine_like_terms(self, *others):
        combined = Expression()
        for term in self.terms:
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
        for index, term in enumerate(self.terms):
            if len(term.bases_exponents) == 0:
                if 0 == len(self.terms) - 1:
                    return False
            elif term.bases_exponents[min(term.bases_exponents)] != (len(self.terms) - 1) - index:
                return False
        return True

    def quadratic_equation(self):
        """
        runs quadratic equation expression's coefficients
        """
        if len(self) != 3:
            raise IndexError("len of self must be 3")

        a, b, c = self[0].coefficient, self[1].coefficient, self[2].coefficient

        left = (-1 * b)
        right = ((b ** 2) - (4 * a * c)) ** 0.5

        div = (2 * a)

        return {safe_int((left + right) / div), safe_int((left - right) / div)}

    def __contains__(self, item) -> bool:
        return item in self.terms

    def __add__(self, other) -> "Expression":
        if isinstance(other, int):
            other = Term(other)

        if isinstance(other, Term):
            new = self.terms.copy()
            for index, term in enumerate(new):
                if other.same_bases_and_exponents(term):
                    new[index] = term + other
                    return Expression(terms=new)
            return Expression(terms=(new + [other]))

        elif isinstance(other, Expression):
            return sum(other.terms, start=self)
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
            return Expression(terms=[term / other for term in self.terms])
        elif isinstance(other, Expression):
            return sum([(self / other_term) for other_term in other.terms], start=Expression())
        return NotImplemented

    def __neg__(self):
        return self * -1

    def __pow__(self, power, modulo=None) -> "Expression":
        current = self
        for i in range(power - 1):
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

    def __getitem__(self, key) -> Term or "Expression":
        if isinstance(key, int):
            return self.terms[key]
        elif isinstance(key, slice):
            return Expression(terms=self.terms[key])
        return NotImplemented

    def __len__(self) -> int:
        return len(self.terms)

    def __str__(self) -> str:
        return self.str_plus()

    def __repr__(self) -> str:
        return f"Expression(terms={self.terms})"


def term_sort_key(term: "Term") -> int:
    """
    used as a key for sorting terms in expressions
    """
    if term.bases_exponents == {}:
        return -1
    first = min(term.bases_exponents.keys())
    return term.bases_exponents[first]
