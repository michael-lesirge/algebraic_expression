from algebraic_expression.utils import safe_int, sort_dict, sum_dict, subtract_dict


def parse_term(user_input: str) -> tuple[int, dict]:
    """
    parses a term into its coefficient and its bases+exponents
    """
    if user_input in ["", " "]:
        return 0, {}
    exponents_mapper = {"coefficient": ""}
    last = "coefficient"
    for char in user_input:
        if char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            exponents_mapper[char] = ""
            last = char
        elif char in ".-0123456789":
            exponents_mapper[last] += char

    exponents = {}
    for key, value in exponents_mapper.items():
        if value in ["", " "]:
            exponents[key] = 1
        elif value == "-":
            exponents[key] = -1
        else:
            exponents[key] = safe_int(value)

    coefficient = exponents["coefficient"]
    del exponents["coefficient"]

    return coefficient, exponents


class Term:
    __slots__ = ("coefficient", "bases_exponents", "__str_cache")

    def __init__(self, value: str or int = "0", *, coefficient=None, bases_exponents=None):
        if isinstance(value, int):
            self.coefficient = value
            self.bases_exponents = {}
        elif (coefficient is not None) or (bases_exponents is not None):
            if coefficient is None:
                coefficient = 1
            if bases_exponents is None:
                bases_exponents = {}
            self.coefficient, self.bases_exponents = coefficient, bases_exponents
        else:
            self.coefficient, self.bases_exponents = parse_term(value)

        self.bases_exponents = dict(filter(lambda x: x[1] not in [0, float("-inf")], self.bases_exponents.items()))
        self.bases_exponents = sort_dict(self.bases_exponents)

        self.__str_cache = {}

    def str_plus(self, *, plus=False, **kwargs):
        """
        gives options for how you want string to look
        plus adds a plus sign at beginning if there is no negative sign
        kwargs go to superscript function. def superscript(html=False, up_symbol="**"):
        """
        set_kwargs = tuple(kwargs.items())
        if set_kwargs not in self.__str_cache:
            final = []
            if self.coefficient == -1:
                final.append("-")
            elif self.coefficient != 1 or len(self.bases_exponents) == 0:
                final.append(str(self.coefficient))

            for key, value in self.bases_exponents.items():
                final.append(key)
                if value != 1:
                    final.append(superscript(value, **kwargs))
            self.__str_cache[set_kwargs] = ''.join(final)

        result = self.__str_cache[set_kwargs]

        if plus and result[0] != '-':
            result = '+' + result

        return result

    def str_equation(self, *, plus=False) -> str:
        """
        returns an equation of itself that could be run by python interpret with eval
        """
        result = str(self.coefficient)
        for base, exponent in self.bases_exponents.items():
            result += "*" + "(" + base + "**" + str(exponent) + ")"

        if plus and result[0] != '-':
            result = '+' + result

        return result

    def var_equals(self, variables: dict[str: int]) -> int:
        """
        variables must contain all variables that are in equation
        runs the equation with eval
        """
        return eval(self.str_equation(), variables)

    def same_bases(self, other) -> bool:
        """
        returns true if 2 terms have the same bases
        """
        if isinstance(other, Term):
            return set(self.bases_exponents.keys()) == set(other.bases_exponents.keys())
        return False

    def same_bases_and_exponents(self, other) -> bool:
        """
        returns true if 2 terms have the same bases and exponents
        """
        if isinstance(other, Term):
            return self.bases_exponents == other.bases_exponents
        return False

    def copy(self):
        return Term(coefficient=self.coefficient, bases_exponents=self.bases_exponents.copy())

    def is_zero_term(self) -> bool:
        """
        returns if the coefficient is zero
        """
        return self.coefficient == 0

    def __add__(self, other):
        if isinstance(other, Term):
            if self.same_bases_and_exponents(other):
                return Term(coefficient=self.coefficient + other.coefficient, bases_exponents=self.bases_exponents)
            else:
                raise Exception(f"No way to add {self} and {other} due to lack of matching bases and exponents. ")
        elif isinstance(other, int):
            return Term(coefficient=self.coefficient + other, bases_exponents=self.bases_exponents)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Term):
            if self.same_bases_and_exponents(other):
                return Term(coefficient=self.coefficient - other.coefficient, bases_exponents=self.bases_exponents)
            else:
                raise Exception(f"No way to subtract {self} and {other} due to lack of matching bases and exponents. ")
        elif isinstance(other, int):
            return Term(coefficient=self.coefficient - other, bases_exponents=self.bases_exponents)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, int):
            other = Term(str(other))
        if isinstance(other, Term):
            return Term(coefficient=self.coefficient * other.coefficient,
                        bases_exponents=sum_dict(self.bases_exponents, other.bases_exponents))
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, int):
            other = Term(str(other))

        if isinstance(other, Term):
            return Term(coefficient=safe_int(self.coefficient / other.coefficient),
                        bases_exponents=subtract_dict(self.bases_exponents, other.bases_exponents))

        return NotImplemented

    def __neg__(self):
        return self * -1

    def __eq__(self, other):
        if isinstance(other, Term):
            return self.coefficient == other.coefficient and self.bases_exponents == other.bases_exponents
        return False

    def __ne__(self, other):
        if isinstance(other, Term):
            return self.coefficient != other.coefficient or self.bases_exponents != other.bases_exponents
        return True

    def __contains__(self, item) -> bool:
        return item in self.bases_exponents

    def __repr__(self):
        return f"Term(coefficient={self.coefficient}, bases_exponents={self.bases_exponents})"

    def __int__(self):
        return self.coefficient

    def __float__(self):
        return float(self.coefficient)

    def __str__(self):
        return self.str_plus()


def superscript(value, html=False, up_symbol="**") -> str:
    """
    returns a superscript version of an exponent
    """
    if html:
        return '<sup>' + str(value) + '</sup>'
    return up_symbol + str(value)
