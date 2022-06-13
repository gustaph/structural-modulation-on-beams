from .support import SupportTypes
from .load import LoadTypes
from .write_report import Writer
from .plot_beam import Plot

import numpy as np
import sympy as sym
from collections import ChainMap

BOUNDARY_CONDITIONS = {
    SupportTypes.fixed: {
        "M": "?",
        "V": "?"
    },
    SupportTypes.roller: {
        "M": 0.0,
        "V": "?"
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
    LoadTypes.uniformlyVarying: lambda p, b, a: (p / b) * sym.SingularityFunction(sym.Symbol('x'), a, 1)
}


class Model:
    def __init__(self, beam, bound_conds=None, app=False):
        if bound_conds is None:
            bound_conds = BOUNDARY_CONDITIONS

        self.writer = Writer()
        self.beam = beam
        self.bound_conds = bound_conds
        self.plotter = Plot(self.beam.L, self.beam.supports, self.beam.loads, app)
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

    def _get_best_position(self, dict_values):
        """
        [(position, {'M': 'Value', 'V': 'Value'}), ...]

        * Conditions:
            1) Two equal forces equals zero at different positions.
                - [M(x->0):0; M(x->L):0] or [V(x->0):0; V(x->L):0]
            2) Two different forces equals zero at the same position
                - [M(x->0):0; V(x->L):0] or [M(x->L):0; V(x->0):0]

        * Returns:
            [position, [[force: 0.0], [force: 0.0], ...]]
        """

        dict_conditions = [condition[1] for condition in dict_values]
        values = np.array([list(value.values()) for value in dict_conditions])
        print("VALUES:\n", values)
        main_condition = (values != "?")

        valid_values = np.sum(main_condition)
        if valid_values <= 1:
            return [None, None]

        # 1st CASE: TWO VALUES IN ONE POSITION
        indices = np.argwhere(main_condition.all(axis=1)).flatten()
        if len(indices) > 0:
            return np.array(dict_values)[indices[0]]

        # 2nd CASE: VALUES IN DIFFERENT POSITIONS
        column_split = np.hsplit(main_condition, 2)

        if not any(column_split[0]):
            indices = np.where(column_split[1] == np.amax(column_split[1]))[0][:2]

        elif not any(column_split[1]):
            indices = np.where(column_split[0] == np.amax(column_split[0]))[0][:2]

        else:
            indices = [np.argmax(column_split[0]), np.argmax(column_split[1])]

        if len(indices) <= 1:
            return [None, None]

        return np.array(dict_values)[indices[:2]]

    def solve_for_force(self, force: str, equations: dict, position: int, value_force: int, subs={}):
        x = sym.Symbol("x")
        equation = equations[force]
        result = {}

        force_at_pos = equation.subs(dict(ChainMap({x: position}, subs)))
        force_at_pos = sym.Eq(force_at_pos.lhs, force_at_pos.rhs - value_force)
        variables = list(force_at_pos.atoms(sym.Symbol))

        for var in variables:
            result[var] = sym.solve(force_at_pos.args[1], var, rational=False)[0]

        if len(result) > 0:
            with sym.evaluate(False):
                self.writer.write_equation([
                    f"{sym.latex(equation.subs(dict(ChainMap({x: position}, subs))))} = {sym.latex(value_force)}"
                ])
                
                if value_force != 0.0:
                    self.writer.write_equation([
                        f"{sym.latex(equation.subs(dict(ChainMap({x: position}, subs))))} = {sym.latex(value_force)}"
                    ])
                    
            self.writer.write_equation([f"{sym.latex(force_at_pos.args[1])} = {value_force}"])

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

        self.plotter.plot_model(save=True)
        self.writer.add_image(self.plotter.beam_filename, scale_width="90%")
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

            conditions = self.bound_conds[support.category]
            position_conditions.append((support.position, conditions))
            self.writer.write_dict_boundaries(conditions, support.position if support.position != self.beam.L else "L")

        if not self.beam.supports.__contains__(self.beam.L):
            position_conditions.append((self.beam.L, self.bound_conds["free"]))
            
        if not self.beam.supports.__contains__(0.0):
            position_conditions.append((0.0, self.bound_conds["free"]))

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

        v_x = sym.dsolve(sym.Eq(v_diff, self.q.args[1]), rational=False)  # V(x)
        self.writer.write_equation([f"{sym.latex(symbolic_M.diff(x))} = {sym.latex(v_x)}"], box=True)
        self.writer.write_content("---")

        self.writer.write_equation([
            f"{sym.latex(sym.Eq(m_diff_2, symbolic_V))}{arrow}{sym.latex(sym.Eq(sym.Integral(m_diff_2, x), sym.Integral(symbolic_V, x)))}",
            f"\Rightarrow {sym.latex(sym.Eq(m_diff_2, v_x.args[1]))}",
            f"\Rightarrow {sym.latex(sym.Eq(sym.Integral(m_diff_2, x), sym.expand(sym.Integral(v_x.args[1], x))))}"
        ])

        m_x = sym.dsolve(sym.Eq(symbolic_M.diff(x), v_x.args[1]), rational=False)  # M(x)
        self.writer.write_equation([sym.latex(m_x)], box=True)
        self.writer.write_content("---")

        equations = {"M": m_x, "V": v_x}

        print("POSITION CONDITIONS")
        print(position_conditions)

        best_pos_bounds = self._get_best_position(position_conditions)
        if best_pos_bounds.size == best_pos_bounds.shape[0]:
            best_pos_bounds = best_pos_bounds[None, :]

        print("best_positions 02\n", best_pos_bounds)
        constants = {}

        for position, bounds in best_pos_bounds:
            bounds = dict(reversed(list(bounds.items())))
            self.writer.write_dict_boundaries(bounds, "L" if position == self.beam.L else position)

            for force in bounds.keys():
                if bounds[force] != "?":
                    constants.update(self.solve_for_force(force, equations, position, bounds[force], constants))

        print(constants)

        self.writer.add_section("4. Model plot", level=2)

        modules = [{"SingularityFunction": lambda x, a, e: (x - a) ** e * (x > a)}, "numpy"]
        final_v_x = v_x.subs(constants)
        final_m_x = m_x.subs(constants)
        function_v_x = sym.lambdify(x, expr=final_v_x.args[1], modules=modules)
        function_m_x = sym.lambdify(x, expr=final_m_x.args[1], modules=modules)

        self.writer.write_equation([sym.latex(final_m_x) + "; \qquad " + sym.latex(final_v_x)], box=True)

        x_points = np.linspace(0, self.beam.L, int(self.beam.L * 100))
        internal_strain = (x_points, function_v_x(x_points), function_m_x(x_points))

        self.plotter.plot_model(internal_strain, save=True)
        self.writer.add_image(self.plotter.strain_filename)
        self.writer.write_content(" ")
