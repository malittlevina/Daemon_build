from core.module import Module
import sympy
import math

class Calculator(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.history = []

    def initialize(self):
        self.kernel.log("Calculator", "Initialized (SymPy engine).")

    def start(self):
        pass

    def stop(self):
        pass

    def calculate(self, expression):
        """Evaluate a mathematical expression numerically."""
        try:
            # Use sympy.sympify to parse, then evalf for number
            expr = sympy.sympify(expression)
            result = expr.evalf()
            self.history.append(f"{expression} = {result}")
            self.kernel.log("Calculator", f"Calculated: {expression} = {result}")
            return str(result)
        except Exception as e:
            self.kernel.log("Calculator", f"Error calculating '{expression}': {e}", level="error")
            return f"Error: {e}"

    def solve(self, equation_str):
        """Solve an algebraic equation (e.g., 'x**2 - 4'). Assumes = 0 if no =."""
        try:
            # Handle "2x + 5 = 10" format by moving right side to left
            if "=" in equation_str:
                left, right = equation_str.split("=")
                eq = sympy.sympify(left) - sympy.sympify(right)
            else:
                eq = sympy.sympify(equation_str)

            # Find variables
            symbols = eq.free_symbols
            if not symbols:
                return "No variables found to solve."

            solutions = sympy.solve(eq, symbols)
            self.history.append(f"Solved {equation_str}: {solutions}")
            self.kernel.log("Calculator", f"Solved: {equation_str} -> {solutions}")
            return f"Solutions: {solutions}"

        except Exception as e:
            self.kernel.log("Calculator", f"Error solving '{equation_str}': {e}", level="error")
            return f"Error: {e}"

    def get_history(self):
        return self.history
