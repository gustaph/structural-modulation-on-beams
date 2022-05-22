from beam import Beam
import numpy as np
import sympy as sym
from support import Support, SupportTypes
from load import Load, LoadTypes

from utils.write_report import Writer


BOUNDARY_CONDITIONS = {
    SupportTypes.fixed: {
        "M": "?",
        "V": "?",
        "N": "?"
    },
    SupportTypes.roller: {
        "M": 0.0,
        "V": "?",
        "N": "?"
    },
    SupportTypes.pinned: {
        "M": "?",
        "V": 0.0,
        "N": 0.0
    },
    "free": {
        "M": 0.0,
        "V": 0.0,
        "N": "?"
    }
}


LOAD_STEP_EQUATIONS = {
    LoadTypes.centered: lambda p, _, a: p * sym.SingularityFunction(sym.Symbol('x'), a, -1),
    LoadTypes.uniformlyDistributed: lambda p, _, a: p * sym.SingularityFunction(sym.Symbol('x'), a, 0),
    LoadTypes.uniformlyVarying: lambda p, b, a: (p/b) * sym.SingularityFunction(sym.Symbol('x'), a, 1)
}


class Model:
    def __init__(self, beam):
        self.writer = Writer()
        self.beam = beam
        self.q, self.M, self.V = self._define_equations()

    def _define_equations(self):
        
        x = sym.Symbol("x")
        q = sym.Function("q")(x)
        V = sym.Function("V")(x)
        M = sym.Function("M")(x)
        
        functions = 0.0
        for load in self.beam.loads:
            end = 0.0 if load.end is None else load.end
            functions += LOAD_STEP_EQUATIONS[load.category](sym.Rational(str(load.magnitude)),
                                                         sym.Rational(str(np.abs(end - load.start))),
                                                         sym.Rational(str(load.start)))
            
        q = sym.Eq(q, functions)
        V = sym.dsolve(sym.Eq(V.diff(x), functions))
        M = sym.dsolve(sym.Eq(M.diff(x, x), functions))
        
        return q, M, V
    
    def solve(self):
        
        # Variables & Functions
        x, c1, c2 = sym.symbols("x C(1:3)")
        symbolic_q, symbolic_V, symbolic_M = sym.Function("q"), sym.Function("V"), sym.Function("M")
        
        self.writer.add_section("1. Mechanical behavior", level=2)
        beam_loads = ", ".join(["**" + load.category.value.upper() + "**"
                                for load in self.beam.loads])
        self.writer.write_content("Beam with loads: " + beam_loads + ".")
        self.writer.write_content("Considering the differential equations of equilibrium:")
        self.writer.write_eq_equations()
        self.writer.write_content("Thus,")
        self.writer.write_equation([
            f"{sym.latex(sym.Eq(symbolic_q(x), symbolic_M(x).diff(x, x)))} \longrightarrow {sym.latex(self.q)}"
        ])
        
        self.writer.add_section("2. Boundary conditions", level=2)
        for index, support in enumerate(self.beam.supports.values()):
            self.writer.add_section(f"2.{index + 1}. {support.category.value.upper()}", level=4)
            

if __name__ == '__main__':
    b = Beam(0.5)
    b.add_load(Load(-1000, LoadTypes.centered, 0.3))
    
    model = Model(b)
    model.solve()
    
    # w.add_section("Equations for Beam(0.5, Load(1000, LoadTypes.centered, 0.3))")
    # w.write_equation([sym.latex(model.M),
    #                   sym.latex(model.V),
    #                   sym.latex(model.q)])