from .utils import safe_int, sort_dict, sum_dict, subtract_dict


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
    """
    single term in expression
    """
    __slots__ = ("coefficient", "bases_exponents", "_str_cache")

    def __init__(self, value=None, *, coefficient: float = 0, bases_exponents: dict[str: int or float] = None):
        """
        example:
        coefficient = 4
        bases_exponents = {'x': 2}
        output = Term(4x**2)
        """
        if isinstance(value, Term):
            self.coefficient, self.bases_exponents, self._str_cache = value.coefficient, value.bases_exponents, value._str_cache
        else:
            self.coefficient = coefficient
            self.bases_exponents = bases_exponents or dict()
            
            if isinstance(value, (int, float)):
                self.coefficient = value
            elif isinstance(value, str):
                self.coefficient, self.bases_exponents = parse_term(value)
            elif value is not None:
                raise Exception(f"invalid type {type(value)} for Expression")

            self.bases_exponents = dict(filter(lambda x: x[1]!=0, self.bases_exponents.items()))
            self.bases_exponents = sort_dict(self.bases_exponents)

            self._str_cache = None

    def str_plus(self, *, plus=False, html=False, up_symbol="**", **kwargs):
        """
        gives options for how you want string to look
        """
        final = []
        if self.coefficient == -1:
            final.append("-")
        elif self.coefficient != 1 or len(self.bases_exponents) == 0:
            final.append(str(self.coefficient))

        for key, value in self.bases_exponents.items():
            final.append(key)
            if value != 1:
                final.append(superscript(value, html=html, up_symbol=up_symbol, **kwargs))
        result = ''.join(final)

        if plus and result[0] != '-':
            result = '+' + result

        return result

    @property
    def bases(self) -> list:
        return list(self.bases_exponents.keys())

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
        return isinstance(other, Term) and (set(self.bases_exponents.keys()) == set(other.bases_exponents.keys()))


    def same_bases_and_exponents(self, other) -> bool:
        """
        returns true if 2 terms have the same bases and exponents
        """
        return isinstance(other, Term) and (self.bases_exponents == other.bases_exponents)

    def is_zero_term(self) -> bool:
        return self.coefficient == 0

    def __add__(self, other):
        if isinstance(other, Term):
            if self.same_bases_and_exponents(other):
                return Term(coefficient=self.coefficient + other.coefficient, bases_exponents=self.bases_exponents)
            else:
                raise Exception(f"No way to add {self} and {other} due to lack of matching bases and exponents. ")
        elif isinstance(other, (int, float)):
            return Term(coefficient=self.coefficient + other, bases_exponents=self.bases_exponents)
        return NotImplemented

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, Term):
            if self.same_bases_and_exponents(other):
                return Term(coefficient=self.coefficient - other.coefficient, bases_exponents=self.bases_exponents)
            else:
                raise Exception(f"No way to subtract {self} and {other} due to lack of matching bases and exponents. ")
        elif isinstance(other, (int, float)):
            return Term(coefficient=self.coefficient - other, bases_exponents=self.bases_exponents)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Term(other) - self
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            other = Term(str(other))
        if isinstance(other, Term):
            return Term(coefficient=self.coefficient * other.coefficient,
                        bases_exponents=sum_dict(self.bases_exponents, other.bases_exponents))
        return NotImplemented

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            other = Term(str(other))

        if isinstance(other, Term):
            return Term(coefficient=safe_int(self.coefficient / other.coefficient),
                        bases_exponents=subtract_dict(self.bases_exponents, other.bases_exponents))

        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return Term(other) / self
        return NotImplemented

    def __hash__(self):
        return hash((hash(self.coefficient), hash(tuple(self.bases_exponents.items()))))

    def __neg__(self):
        return -1 * self

    def __eq__(self, other):
        return isinstance(other, Term) and (self.coefficient == other.coefficient and self.bases_exponents == other.bases_exponents)

    def __ne__(self, other):
        return (not isinstance(other, Term)) or (self.coefficient != other.coefficient or self.bases_exponents != other.bases_exponents)

    def __len__(self):
        return len(self.bases)

    def __contains__(self, item):
        return item in self.bases

    def __repr__(self):
        return f"{self.__class__.__name__}(coefficient={self.coefficient}, bases_exponents={self.bases_exponents})"

    def __int__(self):
        return int(self.coefficient)

    def __float__(self):
        return float(self.coefficient)

    def __str__(self):
        if self._str_cache is None:
            self._str_cache = self.str_plus()
        return self._str_cache


def superscript(value, html=False, up_symbol="**", ending="", html_tag="sup") -> str:
    """
    returns a superscript version of an exponent
    """
    if html:
        return f"<{html_tag}>{value}</{html_tag}>" + ending
    return up_symbol + str(value) + ending
