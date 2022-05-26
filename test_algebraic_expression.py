from re import S
from algebraic_expression import Expression as Expr
from algebraic_expression import Term

import unittest


class TestExpression(unittest.TestCase):
    def test_init(self):
        self.assertEqual(Expr("13x**2+2"), Expr(terms=[Term("13x**2"), Term("2")]))
        self.assertEqual(Expr("5x**2y**2-20y"), Expr(terms=[Term("5x**2y**2"), Term("-20y")]))
        self.assertEqual(Expr("4x**3+1", terms=[Term("3x**2"), Term("-2x")]), Expr("4x**3+3x**2-2x+1"))

    def test_add(self):
        self.assertEqual(Expr("3xy+4x-7") + Expr("3xy-6x"), Expr("6xy-2x-7"))
        self.assertEqual(Expr("6x+7") + Expr("4x+6y+xy"), Expr("10x+xy+6y+7"))
        self.assertEqual(Expr("x+y+z") + Expr("x-y+z"), Expr("2x+2z"))
        self.assertEqual(Expr("6xyz+2xy") + Expr("-8xyz"), Expr("-2xyz+2xy"))
        self.assertEqual(Expr("3x+5") + Expr("5x-2"), Expr("8x+3"))
        self.assertEqual(Expr("-x-3") + Expr("3x+8"), Expr("2x+5"))

    def test_negative(self):
        self.assertEqual(-Expr("-3x**5+9y+z"), Expr("3x**5-9y-z"))
        self.assertEqual(-Expr("6x**5+10y+7z-2"), Expr("-6x**5-10y-7z+2"))

    def test_subtraction(self):
        # x-y = x+(-y)
        self.assertEqual(Expr("5x+5") - Expr("2x+2"), Expr("3x+3"))
        self.assertEqual(Expr("-5v-2") - Expr("4v+2"), Expr("-9v-4"))

    def test_distribute(self):
        self.assertEqual(Expr("3x+6").distribute(Expr("2x-2")), [Expr("6x**2+12x"), Expr("-6x-12")])
        self.assertEqual(Expr("2x-2").distribute(Expr("3x+6")), [Expr("6x**2-6x"), Expr("12x-12")])

    def test_multiplication(self):
        self.assertEqual(Expr("3x+6") * Expr("2x-2"), Expr("6x**2+6x-12"))
        self.assertEqual(Expr("3a+5b") * Expr("5a-7b"), Expr("15a**2+4ab-35b**2"))
        self.assertEqual(Expr("5x**2-6x+9") * Expr("2x+3"), Expr("10x**3+3x**2+27"))

    def test_division(self):
        self.assertEqual(Expr("8x**2y**3") / Expr("-2xy"), Expr("-4xy**2"))
        self.assertEqual(Expr("35x**3yz**2") / Expr("-7xyz"), Expr("-5x**2z"))
        self.assertEqual(Expr("-25x**4y**3+30x**2y**5") / Expr("-5x**2y"), Expr("5x**2y**2-6y**4"))

    def test_display(self):
        expr1 = Expr("8x**3y+6x**2+3y+z")
        self.assertEqual(str(expr1), "8x**3y+6x**2+3y+z")
        self.assertEqual(expr1.str_plus(), "8x**3y+6x**2+3y+z")
        self.assertEqual(expr1.str_plus(sep=" "), "8x**3y +6x**2 +3y +z")
        self.assertEqual(expr1.str_plus(braces=True), "(8x**3y+6x**2+3y+z)")
        self.assertEqual(expr1.str_plus(plus=True), "+8x**3y+6x**2+3y+z")
        self.assertEqual(expr1.str_plus(braces=True, plus=True), "+(8x**3y+6x**2+3y+z)")
        self.assertEqual(expr1.str_plus(html=True), "8x<sup>3</sup>y+6x<sup>2</sup>+3y+z")

        self.assertEqual(expr1, Expr(str(expr1)))
        
        self.assertEqual(repr(expr1), "Expression(terms=("
                                      "Term(coefficient=8, bases_exponents={'x': 3, 'y': 1}), "
                                      "Term(coefficient=6, bases_exponents={'x': 2}), "
                                      "Term(coefficient=3, bases_exponents={'y': 1}), "
                                      "Term(coefficient=1, bases_exponents={'z': 1})"
                                      "))")

    def test_getting(self):
        expr1 = Expr("8x**3y+6x**2+3y+z")
        self.assertIsInstance(expr1[0], Term)
        self.assertIsInstance(expr1[0:2], Expr)

        self.assertEqual(expr1[0], Term("8x**3y"))
        self.assertEqual(expr1[0:2], Expr("8x**3y+6x**2"))

        for index, term in enumerate(expr1):
            self.assertEqual(term, expr1[index])

        self.assertEqual(len(expr1), 4)
        self.assertTrue(Term("6x**2") in expr1)

        self.assertTrue(Expr("8x**3y+6x**2+3y+z") == expr1)
        self.assertTrue(Expr("8x**3y+6x**3+3y+z") != expr1)

        self.assertFalse(Expr("8x**3y+6x**2+4y+z") == expr1)
        self.assertFalse(Expr("8x**3y+6x**2+3y+z") != expr1)

        self.assertIsNotNone(hash(expr1), any)

    def test_quadratic_equation(self):
        self.assertEqual(Expr("x**2+5x+6").quadratic_equation(), {-2, -3})
        self.assertEqual(Expr("2x**2-4x-30").quadratic_equation(round_to=3), {5, -3})
        self.assertEqual(Expr("-x**2-6x+8").quadratic_equation(round_to=3), {-7.123, 1.123})

    def test_greatest_common_facter(self):
        self.assertEqual(Expr("10x**2+15x+65").gcf, Term("5"))
        self.assertEqual(Expr("-10x**3-15x**2-65x").gcf, Term("5x"))
        self.assertEqual(Expr("14x**2+7xy+28x").gcf, Term("7x"))
        self.assertEqual(Expr("14x**3y+7x**2y**2+28x**2y").gcf, Term("7x**2y"))

        expr1 = Expr("6x**3yz+4x**2y**2+12x**2z")
        expr1_gcf = expr1.gcf
        expr2 = expr1 / expr1_gcf
        self.assertEqual(expr2 * expr1_gcf, expr1)


if __name__ == '__main__':
    unittest.main()
