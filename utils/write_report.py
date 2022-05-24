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
            
    def _format_equation(self, equation: str, box: bool = False, center: bool = True):
        sign = "$$" if center else "$"
        if box:
            equation = r"\boxed{ " + equation + " } "
        
        return f"{sign}{equation}{sign}" + linesep

    def write_equation(self, equation: list, box: bool = False, center: bool = True):
        with open(self.file, "a") as report:
            for eq in equation:
                report.write(self._format_equation(eq, box, center))

    def add_image(self, dir: str, scale_width: float = "100%"):
        with open(self.file, 'a') as report:
            report.write(f'<p align="center"><img src={str(dir)} width={str(scale_width)}/></p>')

    def write_dict_boundaries(self, dict_boundaries: dict, x: float):
        self.write_equation([f'x \longrightarrow {x}'], box=True, center=False)
        
        equations = [f'{force}(x \longrightarrow {x}) = {value}'
                     for force, value in list(dict_boundaries.items())[:-1]]
        equations = "$$" + ' \qquad \qquad '.join(equations) + "$$"
        
        self.write_content(f"> {equations}")
        
    
    def generate(self):
        pass
