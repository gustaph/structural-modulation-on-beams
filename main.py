from utils.model_cli import ModelCli
from utils.beam import Beam
from utils.load import Load, LoadTypes
from utils.support import Support, SupportTypes

# # SIMPLE EXAMPLE FOR TESTING
beam = Beam(h=200, L=4.0, I=10e5)
beam.add_support(Support(0.0, SupportTypes.pinned))
beam.add_support(Support(4.0, SupportTypes.pinned))
beam.add_load(Load(-100, LoadTypes.uniformlyDistributed, 0.0, 4.0))
model = ModelCli(beam)
_, (x, y), (mesh_x, mesh_y), internal_strain, inertia = model.solve()
fig = model.plot_results((x, y), (mesh_x, mesh_y), internal_strain, inertia)

# # Q1
# beam = Beam(L=5)
# beam.remove_support(0.0)
# beam.add_support(Support(0.0, SupportTypes.pinned))
# beam.add_support(Support(5.0, SupportTypes.roller))
# beam.add_load(Load(-10, LoadTypes.centered, 1.0))
# beam.add_load(Load(-20, LoadTypes.centered, 2.0))
# beam.add_load(Load(-20, LoadTypes.centered, 3.0))
# model = Model(beam, app=True)
# model.solve()

# # Q2
# BOUNDARY_CONDITIONS = {
#     SupportTypes.fixed: {
#         "M": "?",
#         "V": "?"
#     },
#     SupportTypes.roller: {
#         "M": 80.0,
#         "V": "?"
#     },
#     SupportTypes.pinned: {
#         "M": 0.0,
#         "V": "?"
#     },
#     "free": {
#         "M": 0.0,
#         "V": 0.0
#     }
# }
# beam = Beam(L=10)
# beam.remove_support(0.0)
# beam.add_support(Support(0.0, SupportTypes.roller))
# beam.add_support(Support(10.0, SupportTypes.pinned))
# beam.add_load(Load(-5, LoadTypes.uniformlyDistributed, 5.0, 10.0))
# beam.add_load(Load(-15, LoadTypes.centered, 5.0))
# model = Model(beam, bound_conds=BOUNDARY_CONDITIONS, app=True)
# model.solve()

# Q3
# beam = Beam(L=4)
# beam.remove_support(0.0)
# beam.add_support(Support(4.0, SupportTypes.fixed))
# beam.add_load(Load(-2, LoadTypes.centered, 0.0))
# beam.add_load(Load(-1.5, LoadTypes.uniformlyDistributed, 2.0, 4.0))
# model = Model(beam, app=True)
# model.solve()

# beam = Beam(L=4)
# beam.remove_support(0.0)
# beam.add_support(Support(0.0, SupportTypes.pinned))
# beam.add_support(Support(4.0, SupportTypes.pinned))
# beam.add_load(Load(-100, LoadTypes.uniformlyDistributed, 0.0, 4.0))
# model = Model(beam, app=True)
# model.solve()


# beam = Beam(L=1500)
# beam.add_load(Load(-10, LoadTypes.uniformlyDistributed, 0.0, 500))
# beam.add_load(Load(-3000, LoadTypes.centered, 750.0))
# model = Model(beam, app=True)
# model.solve()
