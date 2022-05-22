import numpy as np
from pyparsing import line
import sympy as sym
from datetime import datetime
from os import linesep, path


class Writer:
    def __init__(self):
        self.file = f"reports/report_{datetime.now().strftime('%Y%d%d%H%M')}.md"
        
        if path.exists(self.file):
            with open(self.file, 'w') as report:
                report.write("")

    def add_section(self, name: str, level: int = 1):
        marker = "#" * level + " "
        with open(self.file, "a") as report:
            report.write(marker + "**" + name + "**" + linesep)

    def write_content(self, content):
        with open(self.file, "a") as report:
            report.write(content + linesep)

    def write_equation(self, equation: list):        
        with open(self.file, "a") as report:
            for eq in equation:
                report.write(f"$${eq}$${linesep}")               
            

    def add_image(self, dir: str, caption: str = ""):
        with open(self.file, 'a') as report:
            report.write(f"![{caption}]({dir}){linesep}")

    def generate(self):
        pass


if __name__ == "__main__":
    w = Writer()
    w.add_section("Test")
    w.write_content("this is a guided markdown test")
    
    eqs = [sym.latex(10 * sym.SingularityFunction(sym.Symbol('x'), -3, 1)),
           "V_{sphere} = \\frac{4}{3}\pi r^3"]
    
    w.add_section("2. LaTeX equations in Markdown", level=3)
    w.write_equation(eqs)
    
    w.add_image("../plots/plot_202221212301.jpg", "Test Beam")
