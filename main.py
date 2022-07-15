from utils.model_cli import ModelCli
from utils.beam import Beam
from utils.load import Load, LoadTypes
from utils.support import Support, SupportTypes

# SIMPLE PROBLEM
# beam = Beam(h=200, L=4.0, I=10e5)
# beam.add_support(Support(0.0, SupportTypes.pinned))
# beam.add_support(Support(4.0, SupportTypes.pinned))
# beam.add_load(Load(-100, LoadTypes.uniformlyDistributed, 0.0, 4.0))
# model = ModelCli(beam)
# _, (x, y), (mesh_x, mesh_y), internal_strain, inertia = model.solve()
# fig = model.plot_results((x, y), (mesh_x, mesh_y), internal_strain, inertia)


# Q1
# beam = Beam(h=200, L=5, I=10e5)
# beam.add_support(Support(0.0, SupportTypes.pinned))
# beam.add_support(Support(5.0, SupportTypes.roller))
# beam.add_load(Load(-10, LoadTypes.centered, 1.0))
# beam.add_load(Load(-20, LoadTypes.centered, 2.0))
# beam.add_load(Load(-20, LoadTypes.centered, 3.0))
# model = ModelCli(beam)
# _, (x, y), (mesh_x, mesh_y), internal_strain, inertia = model.solve()
# fig = model.plot_results((x, y), (mesh_x, mesh_y), internal_strain, inertia)


# Q2
# BOUNDARY_CONDITIONS = {
#     SupportTypes.fixed: {
#         "V": "?",  # bending
#         "M": "?",  # shear
#         "O": 0.0,  # angle
#         "v": 0.0   # displacement
#     },
#     SupportTypes.roller: {
#         "V": "?",
#         "M": 80.0,
#         "O": "?",
#         "v": 0.0
#     },
#     SupportTypes.pinned: {
#         "V": "?",
#         "M": 0.0,
#         "O": "?",
#         "v": 0.0
#     },
#     "free": {
#         "V": 0.0,
#         "M": 0.0,
#         "O": "?",
#         "v": "?"
#     }
# }
# beam = Beam(h=200, L=10, I=15e5)
# beam.add_support(Support(0.0, SupportTypes.roller))
# beam.add_support(Support(10.0, SupportTypes.pinned))
# beam.add_load(Load(-5, LoadTypes.uniformlyDistributed, 5.0, 10.0))
# beam.add_load(Load(-15, LoadTypes.centered, 5.0))
# model = ModelCli(beam, bound_conds=BOUNDARY_CONDITIONS)
# _, (x, y), (mesh_x, mesh_y), internal_strain, inertia = model.solve()
# fig = model.plot_results((x, y), (mesh_x, mesh_y), internal_strain, inertia)


# Q3
beam = Beam(h=200, L=4, I=12e5)
beam.add_support(Support(4.0, SupportTypes.fixed))
beam.add_load(Load(-2, LoadTypes.centered, 0.0))
beam.add_load(Load(-1.5, LoadTypes.uniformlyDistributed, 2.0, 4.0))
model = ModelCli(beam)
_, (x, y), (mesh_x, mesh_y), internal_strain, inertia = model.solve()
fig = model.plot_results((x, y), (mesh_x, mesh_y), internal_strain, inertia)
