from .support import SupportTypes
from .load import LoadTypes
from .plotter_cli import PlotterCli

import numpy as np
import sympy as sym
from collections import ChainMap, OrderedDict
from pprint import pprint

BOUNDARY_CONDITIONS = {
    SupportTypes.fixed: {
        "V": "?",  # bending
        "M": "?",  # shear
        "v": 0.0   # displacement
    },
    SupportTypes.roller: {
        "V": "?",
        "M": 0.0,
        "v": 0.0
    },
    SupportTypes.pinned: {
        "V": "?",
        "M": 0.0,
        "v": 0.0
    },
    "free": {
        "V": 0.0,
        "M": 0.0,
        "v": "?"
    }
}

LOAD_STEP_EQUATIONS = {
    LoadTypes.centered: lambda p, _, a: p * sym.SingularityFunction(sym.Symbol('x'), a, -1),
    LoadTypes.uniformlyDistributed: lambda p, _, a: p * sym.SingularityFunction(sym.Symbol('x'), a, 0),
    LoadTypes.uniformlyVarying: lambda p, b, a: (p / b) * sym.SingularityFunction(sym.Symbol('x'), a, 1)
}


class ModelCli:
    def __init__(self, beam, bound_conds=None):
        if bound_conds is None:
            bound_conds = BOUNDARY_CONDITIONS

        self.beam = beam
        self.bound_conds = bound_conds
        self.plotter = PlotterCli(beam)
        self.q, self.M, self.V, self.O, self.v = self._define_equations()

    def _define_equations(self):

        x = sym.Symbol("x")
        q = sym.Function("q")(x)  # load
        V = sym.Function("V")(x)  # shear
        M = sym.Function("M")(x)  # bending
        O = sym.Function("O")(x)  # angle
        v = sym.Function("v")(x)  # displacement
        

        functions = 0.0
        for load in self.beam.loads:
            end = 0.0 if load.end is None else load.end
            functions += LOAD_STEP_EQUATIONS[load.category](sym.Rational(str(load.magnitude)),
                                                            sym.Rational(str(np.abs(end - load.start))),
                                                            sym.Rational(str(load.start)))

        q = sym.Eq(q, functions)
        V = sym.dsolve(sym.Eq(V.diff(x), functions))
        M = sym.dsolve(sym.Eq(M.diff(x), V.args[1]))
        O = sym.dsolve(sym.Eq(O.diff(x), M.args[1]))
        v = sym.dsolve(sym.Eq(v.diff(x), O.args[1]))

        return q, M, V, O, v

    def _get_best_position(self, dict_values):
        dict_values = sorted(dict_values, key=lambda bounds: bounds[0])
        dict_conditions = [condition[1] for condition in dict_values]
        values = np.array([[v if v != "?" else np.nan for v in value.values()] for value in dict_conditions])
        n_vars = len(dict_conditions[0].keys())
        main_condition = ~np.isnan(values)
        
        if np.sum(main_condition) < n_vars:
            return np.repeat(np.nan, n_vars).tolist()

        # 1st CASE: TWO VALUES IN ONE POSITION
        indices = np.argwhere(main_condition.all(1)).flatten()
        if len(indices) > 0:
            return np.array(dict_values)[indices[0]]

        # 2nd CASE: VALUES IN DIFFERENT POSITIONS
        if np.sum(main_condition) >= n_vars:
            indices = np.argwhere(main_condition.any(1)).flatten()
            return np.array(dict_values)[indices]

    def solve_for_force(self, force: str, equations: dict, position: int, value_force: int, subs={}):
        x = sym.Symbol("x")
        equation = equations[force]
        print(f"FORCE <{force}> at position <{position}>")
        print("EQUATION:", equation)
        print("SUBS:", subs, "\n")
        result = {}

        force_at_pos = equation.subs(dict(ChainMap({x: position}, subs)))
        force_at_pos = sym.Eq(force_at_pos.lhs, force_at_pos.rhs - value_force)
        variables = list(force_at_pos.atoms(sym.Symbol))

        for var in variables:
            result[var] = sym.solve(force_at_pos.args[1], var, rational=False)[0]

        return result

    def solve(self):

        # Variables & Functions
        x = sym.symbols("x")
        symbolic_q, symbolic_V, symbolic_M, symbolic_O, symbolic_v = sym.symbols("q V M O v", cls=sym.Function)
        symbolic_q = symbolic_q(x)
        symbolic_V = symbolic_V(x)
        symbolic_M = symbolic_M(x)
        symbolic_O = symbolic_O(x)
        symbolic_v = symbolic_v(x)

        position_conditions = []
        for support in self.beam.supports.values():
            conditions = OrderedDict(self.bound_conds[support.category])
            position_conditions.append((support.position, conditions))

        if not self.beam.supports.__contains__(self.beam.L):
            position_conditions.append((self.beam.L, OrderedDict(self.bound_conds["free"])))
            
        if not self.beam.supports.__contains__(0.0):
            position_conditions.append((0.0, OrderedDict(self.bound_conds["free"])))
             
        equations = {"M": self.M, "V": self.V,
                     "O": self.O, "v": self.v}
        
        pprint(equations)

        print("\nPOSITION CONDITIONS")
        print(position_conditions, "\n")

        best_pos_bounds = self._get_best_position(position_conditions)
        if best_pos_bounds.size == best_pos_bounds.shape[0]:
            best_pos_bounds = best_pos_bounds[None, :]
    
        constants = {}

        for position, bounds in best_pos_bounds:
            for force in bounds.keys():
                if bounds[force] != "?":
                    constants.update(self.solve_for_force(force, equations, position, bounds[force], constants))

        print("\nFINAL CONSTANTS", constants)

        modules = [{"SingularityFunction": lambda x, a, e: (x - a) ** e * (x > a)}, "numpy"]
        v_x = self.V.subs(constants)
        m_x = self.M.subs(constants)
        o_x = self.O.subs(constants)
        vv_x = self.v.subs(constants)
        
        function_v_x = sym.lambdify(x, expr=v_x.args[1], modules=modules)
        function_m_x = sym.lambdify(x, expr=m_x.args[1], modules=modules)
        function_o_x = sym.lambdify(x, expr=o_x.args[1], modules=modules)
        function_vv_x = sym.lambdify(x, expr=vv_x.args[1], modules=modules)
        
        x_points = np.linspace(0, self.beam.L, 10 * round(np.abs(100 * np.log(self.beam.L)) / 10))
        y_points = np.linspace(-self.beam.h/2, self.beam.h/2, len(x_points))
        
        mesh_x, mesh_y = np.meshgrid(x_points, y_points)
        
        final_vx = function_v_x(x_points)
        final_mx = function_m_x(x_points)
        final_ox = function_o_x(x_points)
        final_vvx = function_vv_x(x_points)
        
        inertia = (final_mx * mesh_y) / self.beam.I
        
        return constants, ((x_points, y_points), (mesh_x, mesh_y), (final_vx, final_mx, final_ox, final_vvx), inertia)
    
    def plot_results(self, xy, mesh_xy, internal_strain, inertia):
        return self.plotter.plot_model(xy, mesh_xy, internal_strain, inertia)