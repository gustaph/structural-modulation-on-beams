from typing import List, Tuple
from beam import Beam
import numpy as np
import sympy as sym
from support import Support, SupportTypes
from load import Load, LoadTypes
from utils.write_report import Writer
from collections import ChainMap


BOUNDARY_CONDITIONS = {
    SupportTypes.fixed: {
        "M": "?",
        "V": "?"
    },
    SupportTypes.roller: {
        "M": "?",
        "V": 0.0
    },
    SupportTypes.pinned: {
        "M": 0.0,
        "V": "?"
    },
    "free": {
        "M": 0.0,
        "V": 0.0
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
    
    def _get_best_position(self, conditions: List[Tuple[int, dict]]):
        """
        [(position, {'M': 'Value', 'V': 'Value'}), ...]
        
        * Conditions:
            1) Two equal forces equals zero at different positions.
                - [M(x->0):0; M(x->L):0] or [V(x->0):0; V(x->L):0]
            2) Two differente forces equals zero at the same position
                - [M(x->0):0; V(x->L):0] or [M(x->L):0; V(x->0):0]
                
        * Returns:
            [position, [[force: 0.0], [force: 0.0], ...]]
        """
        
        valid_forces = conditions[0][1].keys()
        matrix_bounds = np.array([bounds for cond in conditions for bounds in cond[1].items()])
        positions = np.array([position[0] for position in conditions])
        
        auxiliar_f = lambda matrix: matrix[0] & matrix[1]
        result = np.zeros((len(valid_forces), matrix_bounds.shape[0]), dtype=bool)

        for index, force in enumerate(valid_forces):
            condition = np.transpose(matrix_bounds == [force, "0.0"])
            result[index, :] = auxiliar_f(condition)

        count_valid = np.sum(result, axis=1) # [M, V]
        if np.sum(count_valid) <= 1: return [None, None]
        
        indices_M = np.argwhere(np.transpose(result[0]))[:2]
        indices_V = np.argwhere(np.transpose(result[1]))[:2]
        indices_pos_M = (np.squeeze(indices_M) / positions.shape[0]).astype(int)
        indices_pos_V = (np.squeeze(indices_V) / positions.shape[0]).astype(int)
        
        if count_valid[0] == 0:
            return positions[indices_pos_V], np.squeeze(matrix_bounds[indices_V])

        if count_valid[1] == 0:
            return positions[indices_pos_M], np.squeeze(matrix_bounds[indices_M])
        
        print("AOOOBAAAA")
        indices = np.unique(np.array([indices_pos_M, indices_pos_V]))
        values = np.sort([
            np.squeeze(matrix_bounds[indices_M][0]),
            np.squeeze(matrix_bounds[indices_V][0])
        ], axis=0)[::-1]
        return positions[indices], values
        
    def solve_for_force(self, force:str, equations:dict, position:int, subs={}):
        x = sym.Symbol("x")
        equation = equations[force]
        force = sym.Function(force)(x)
        result = {}
        
        force_at_pos = equation.subs(dict(ChainMap({x: position}, subs)))
        variables = list(force_at_pos.atoms(sym.Symbol))
        
        for var in variables:
            result[var] = sym.solve(force_at_pos.args[1], var, rational=False)[0]
            
        if len(result) > 0:
            with sym.evaluate(False):
                self.writer.write_equation([
                    f"{sym.latex(equation.subs(dict(ChainMap({x: position}, subs))))} = {sym.latex(0.0)}"
                ])
            self.writer.write_equation([f"{sym.latex(force_at_pos.args[1])} = 0.0"])
            
            for var, value in result.items():
                self.writer.write_equation([f"{sym.latex(sym.Eq(var, value))}"], box=True)
        
        return result
    
    def solve(self):
        
        # Variables & Functions
        x, c1, c2 = sym.symbols("x C(1:3)")
        symbolic_q, symbolic_V, symbolic_M = sym.symbols("q V M", cls=sym.Function)
        symbolic_q = symbolic_q(x)
        symbolic_V = symbolic_V(x)
        symbolic_M = symbolic_M(x)
        
        beam_plot_fname = self.beam.draw(save=True)
        self.writer.add_image("../" + beam_plot_fname, scale_width="90%")
        self.writer.write_content(" ")
        
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
        
        position_conditions = []
        for index, support in enumerate(self.beam.supports.values()):
            self.writer.add_section(f"2.{index + 1}. {support.category.value.upper()}({support.position})", level=4)
            
            conditions = BOUNDARY_CONDITIONS[support.category]
            position_conditions.append((support.position, conditions))
            self.writer.write_dict_boundaries(conditions, support.position if support.position != self.beam.L else "L")

        if not self.beam.supports.__contains__(self.beam.L):
            position_conditions.append((self.beam.L, BOUNDARY_CONDITIONS["free"]))
            
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
        
        v_x = sym.dsolve(sym.Eq(v_diff, self.q.args[1]), rational=False) # V(x)
        self.writer.write_equation([f"{sym.latex(symbolic_M.diff(x))} = {sym.latex(v_x)}"], box=True)
        self.writer.write_content("---")
        
        self.writer.write_equation([
            f"{sym.latex(sym.Eq(m_diff_2, symbolic_V))}{arrow}{sym.latex(sym.Eq(sym.Integral(m_diff_2, x), sym.Integral(symbolic_V, x)))}",
            f"\Rightarrow {sym.latex(sym.Eq(m_diff_2, v_x.args[1]))}",
            f"\Rightarrow {sym.latex(sym.Eq(sym.Integral(m_diff_2, x), sym.expand(sym.Integral(v_x.args[1], x))))}"
        ])
        
        m_x = sym.dsolve(sym.Eq(symbolic_M.diff(x), v_x.args[1]), rational=False) # M(x)
        self.writer.write_equation([sym.latex(m_x)], box=True)
        self.writer.write_content("---")
        
        equations = {"M": m_x, "V": v_x}
        
        best_positions, bounds = self._get_best_position(position_conditions)
        print("best_positions", best_positions)
        print("bounds\n", bounds)
        
        constants = {}
        for position in best_positions:
            for bound in bounds:
                self.writer.write_dict_boundaries({bound[0]: bound[1]}, "L" if position == self.beam.L else position)
                constants.update(self.solve_for_force(bound[0], equations, position, constants))
            
        print(constants)
        
        self.writer.add_section("4. Model plot", level=2)
        # TODO
            

if __name__ == '__main__':
    # b = Beam(5.0)
    # b.remove_support(0.0)
    # b.add_support(Support(0.0, SupportTypes.pinned))
    # b.add_support(Support(5.0, SupportTypes.pinned))
    # b.add_load(Load(-100, LoadTypes.uniformlyDistributed, 2, end=5))
    
    b = Beam(0.5)
    b.add_load(Load(-1000, LoadTypes.centered, 0.3))
    
    # b.draw(False)
    
    model = Model(b)
    model.solve()