from algebraic_expression import Expression as Expr
from algebraic_expression import Term


def printB(*args, **kwargs):
    print("\033[1m")
    print(*args, **kwargs)
    print("\033[0m", end="")


def checker(output, correct, *, print_correct=True):
    if correct not in (any, output):
        print(f"\u001b[31mWrong: {output} != {correct}\u001b[0m\n")
        raise Exception("Incorrect")
    elif print_correct:
        print(f"Correct: {output}")


# BASIC MATH OPERATIONS
printB("expression addition")
checker(Expr("3xy+4x-7") + Expr("3xy-6x"), Expr("6xy-2x-7"))
checker(Expr("6x+7") + Expr("4x+6y+xy"), Expr("10x+xy+6y+7"))
checker(Expr("x+y+z") + Expr("x-y+z"), Expr("2x+2z"))
checker(Expr("6xyz+2xy") + Expr("-8xyz"), Expr("-2xyz+2xy"))
checker(Expr("3x+5") + Expr("5x-2"), Expr("8x+3"))
checker(Expr("-x-3") + Expr("3x+8"), Expr("2x+5"))

printB("to negative")
checker(-Expr("-3x**5+9y+z"), Expr("3x**5-9y-z"))
checker(-Expr("6x**5+10y+7z-2"), Expr("-6x**5-10y-7z+2"))

printB("expression subtraction")
# x-y = x+(-y)
checker(Expr("5x+5") - Expr("2x+2"), Expr("3x+3"))
checker(Expr("-5v-2") - Expr("4v+2"), Expr("-9v-4"))

printB("distribute")
checker(Expr("3x+6").distribute(Expr("2x-2")), [Expr("6x**2+12x"), Expr("-6x-12")])
checker(Expr("2x-2").distribute(Expr("3x+6")), [Expr("6x**2-6x"), Expr("12x-12")])

printB("expression multiplication")
checker(Expr("3x+6") * Expr("2x-2"), Expr("6x**2+6x-12"))
checker(Expr("3a+5b") * Expr("5a-7b"), Expr("15a**2+4ab-35b**2"))
checker(Expr("5x**2-6x+9") * Expr("2x+3"), Expr("10x**3+3x**2+27"))

printB("expression division")
checker(Expr("8x**2y**3") / Expr("-2xy"), Expr("-4xy**2"))
checker(Expr("35x**3yz**2") / Expr("-7xyz"), Expr("-5x**2z"))
checker(Expr("-25x**4y**3+30x**2y**5") / Expr("-5x**2y"), Expr("5x**2y**2-6y**4"))

printB("display")
expr1 = Expr("8x**3y+6x**2+3y+z")
checker(str(expr1), "8x**3y+6x**2+3y+z")
checker(expr1.str_plus(), "8x**3y+6x**2+3y+z")
checker(expr1.str_plus(sep=" "), "8x**3y +6x**2 +3y +z")
checker(expr1.str_plus(braces=True), "(8x**3y+6x**2+3y+z)")
checker(expr1.str_plus(plus=True), "+8x**3y+6x**2+3y+z")
checker(expr1.str_plus(braces=True, plus=True), "+(8x**3y+6x**2+3y+z)")
checker(expr1.str_plus(html=True), "8x<sup>3</sup>y+6x<sup>2</sup>+3y+z")
checker(expr1, Expr(str(expr1)))
checker(repr(expr1), "Expression(terms=("
                     "Term(coefficient=8, bases_exponents={'x': 3, 'y': 1}), "
                     "Term(coefficient=6, bases_exponents={'x': 2}), "
                     "Term(coefficient=3, bases_exponents={'y': 1}), "
                     "Term(coefficient=1, bases_exponents={'z': 1})"
                     "))")
print(expr1.str_equation())

printB("getting")
checker(type(expr1[0]), Term)
checker(type(expr1[0:2]), Expr)
checker(expr1[0], Term("8x**3y"))
checker(expr1[0:2], Expr("8x**3y+6x**2"))
for index, term in enumerate(expr1):
    checker(term, expr1[index], print_correct=False)

checker(Term("6x**2") in expr1, True)
checker(Expr("8x**3y+6x**2+3y+z") == expr1, True)
checker(Expr("8x**3y+6x**2+4y+z") == expr1, False)
checker(Expr("8x**3y+6x**2+3y+z") != expr1, False)
checker(Expr("8x**3y+6x**3+3y+z") != expr1, True)

checker(hash(expr1), any)
checker(len(expr1), 4)

printB("quadratic equation")
checker(Expr("x**2+5x+6").quadratic_equation(), {-2, -3})
checker(Expr("2x**2-4x-30").quadratic_equation(round_to=3), {5, -3})
checker(Expr("-x**2-6x+8").quadratic_equation(round_to=3), {-7.123, 1.123})

printB("greatest common facter")
checker(Expr("10x**2+15x+65").gcf(), Term("5"))
checker(Expr("14x**2+7xy+28x").gcf(), Term("7x"))
checker(Expr("14x**3y+7x**2y**2+28x**2y").gcf(), Term("7x**2y"))

expr1 = Expr("6x**3yz+4x**2y**2+12x**2z")
expr1_gcf = expr1.gcf()
expr2 = expr1 / expr1_gcf
checker(expr2 * expr1_gcf, expr1)
