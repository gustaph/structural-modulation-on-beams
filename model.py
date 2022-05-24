from typing import Tuple
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
    
    def _get_best_position(self, model_data: Tuple[dict]):
        """
        [(position, support, boundaries), (...), ...]
        """
        
        values = [list(position[2].values()) for position in model_data]
        index = np.argmax([np.sum(np.array(module) != "?") for module in values])
        return model_data[index][0], model_data[index][1]
    
    def solve(self):
        
        # Variables & Functions
        x, c1, c2 = sym.symbols("x C(1:3)")
        # symbolic_q, symbolic_V, symbolic_M = sym.Function("q")(x), sym.Function("V")(x), sym.Function("M")(x)
        symbolic_q = sym.Function("q")(x)
        symbolic_V = sym.Function("V")(x)
        symbolic_M = sym.Function("M")(x)
        
        beam_plot_fname = self.beam.draw(save=True)
        self.writer.add_image("../" + beam_plot_fname, scale_width="90%")
        
        self.writer.add_section("1. Mechanical behavior", level=2)
        beam_loads = ", ".join(["**" + load.category.value.upper() + "**"
                                for load in self.beam.loads])
        self.writer.write_content("Beam with load(s): " + beam_loads + ".")
        self.writer.write_content("Considering the differential equations of equilibrium:")
        self.writer.write_eq_equations()
        self.writer.write_content("Thus,")
        self.writer.write_equation([
            f"{sym.latex(sym.Eq(symbolic_q, symbolic_M.diff(x, x)))} \longrightarrow {sym.latex(self.q)}"
        ])
        
        self.writer.add_section("2. Boundary conditions", level=2)
        
        model_boundaries = []
        for index, support in enumerate(self.beam.supports.values()):
            self.writer.add_section(f"2.{index + 1}. {support.category.value.upper()}", level=4)
            
            for position in (0.0, "L"):
                support = self.beam.supports.get(position, None) # support at `position`
                support = support.category if support is not None else "free"
                boundaries = BOUNDARY_CONDITIONS[support]
                model_boundaries.append((position, support, boundaries))
                self.writer.write_dict_boundaries(boundaries, position)
            
        self.writer.add_section("3. Apply boundary conditions", level=2)
        
        m_diff = symbolic_M.diff(x, x)
        m_diff_2 = symbolic_M.diff(x)
        v_diff = symbolic_V.diff(x)
        arrow = " \longrightarrow "
        
        self.writer.write_equation([
            f"{sym.latex(sym.Eq(m_diff, symbolic_q))}{arrow}{sym.latex(sym.Eq(sym.Integral(m_diff, x), sym.Integral(symbolic_q, x)))}",
            f"\Rightarrow {sym.latex(sym.Eq(m_diff, self.q.args[1]))}",
            f"\Rightarrow {sym.latex(sym.Eq(sym.Integral(m_diff, x), sym.Integral(self.q.args[1], x)))}"
        ])
        
        v_x = sym.dsolve(sym.Eq(v_diff, self.q.args[1])) # V(x)
        self.writer.write_equation([f"{sym.latex(symbolic_M.diff(x))} = {sym.latex(v_x)}"], box=True)
        self.writer.write_content("---")
        
        self.writer.write_equation([
            f"{sym.latex(sym.Eq(m_diff_2, symbolic_V))}{arrow}{sym.latex(sym.Eq(sym.Integral(m_diff_2, x), sym.Integral(symbolic_V, x)))}",
            f"\Rightarrow {sym.latex(sym.Eq(m_diff_2, v_x.args[1]))}",
            f"\Rightarrow {sym.latex(sym.Eq(sym.Integral(m_diff_2, x), sym.expand(sym.Integral(v_x.args[1], x))))}"
        ])
        
        m_x = sym.dsolve(sym.Eq(symbolic_M.diff(x), v_x.args[1])) # M(x)
        self.writer.write_equation([sym.latex(m_x)], box=True)
        self.writer.write_content("---")
        
        best_position, support_type = self._get_best_position(model_boundaries)
        self.writer.write_dict_boundaries(BOUNDARY_CONDITIONS[support_type], best_position)
        position = self.beam.L if best_position == "L" else best_position
        
        vx_at_bp = v_x.subs(x, position) # V(x) at best position
        c1_value = sym.solve(vx_at_bp.args[1], c1)[0]
        
        mx_at_bp = m_x.subs({x: position, c1: c1_value}) # M(x) at best position
        c2_value = sym.solve(mx_at_bp.args[1], c2)[0]
        
        with sym.evaluate(False):
            self.writer.write_equation([
                f"{sym.latex(v_x.subs(x, position))} = {BOUNDARY_CONDITIONS[support_type]['V']}"
            ])
        self.writer.write_equation([f"\Rightarrow {sym.latex(vx_at_bp)}"])
        self.writer.write_equation([f"{sym.latex(sym.Eq(c1, c1_value))}"], box=True)
        
        with sym.evaluate(False):
            self.writer.write_equation([
                f"{sym.latex(m_x.subs({x: position, c1: c1_value}))} = {BOUNDARY_CONDITIONS[support_type]['M']}"
            ])
        self.writer.write_equation([f"\Rightarrow {sym.latex(mx_at_bp)}"])
        self.writer.write_equation([f"{sym.latex(sym.Eq(c2, c2_value))}"], box=True)
        
        self.writer.add_section("4. Model plot", level=2)
        # TODO
            

if __name__ == '__main__':
    b = Beam(7.0)
    
    b.remove_support(0.0)
    
    b.add_support(Support(0.0, SupportTypes.pinned))
    b.add_support(Support(7.0, SupportTypes.pinned))
    
    b.add_load(Load(-100, LoadTypes.uniformlyDistributed, 2, end=7))
    
    # b.draw(False)
    
    model = Model(b)
    model.solve()