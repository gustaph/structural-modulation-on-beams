import numpy as np
from pyparsing import line
import sympy as sym
from datetime import datetime
from os import linesep, path


class Writer:
    def __init__(self):
        self.file = f"reports/report_{datetime.now().strftime('%Y%d%d%H%M')}.md"
        self._write_header()

    def _write_header(self):
        with open(self.file, 'w') as report:
            report.write("<h1 align='center'>Report: Structural Modeling by Descontinuous Functions</h1>" + linesep + "---" + linesep)

    def write_eq_equations(self):
        x = sym.Symbol("x")
        q, V, M = sym.Function("q")(x), sym.Function("V")(x), sym.Function("M")(x)
    
        eq_q = sym.Eq(q, M.diff(x, x))
        eq_V = sym.Eq(V, sym.Integral(q))
        eq_M = sym.Eq(M, sym.Integral(sym.Integral(q)))
        
        self.write_equation([sym.latex(eq_q) + "; \qquad " + sym.latex(eq_V) + "; \qquad " + sym.latex(eq_M)], box=True)

    def add_section(self, name: str, level: int = 1):
        marker = "#" * level + " "
        with open(self.file, "a") as report:
            report.write(marker + "**" + name + "**" + linesep)

    def write_content(self, content):
        with open(self.file, "a") as report:
            report.write(content + linesep)

    def write_equation(self, equation: list, box: bool = False):
        with open(self.file, "a") as report:
            for eq in equation:
                if box:
                    eq = r"\boxed{" + eq + "}"
                report.write(f"$${eq}$${linesep}")

    def add_image(self, dir: str, caption: str = "", scale_width="100%"):
        with open(self.file, 'a') as report:
            report.write(f'<p align="center"><img src={str(dir)} width={str(scale_width)}/></p>')

    def generate(self):
        pass
