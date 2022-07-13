from utils.model import Model
from utils.beam import Beam
from utils.load import Load, LoadTypes
from utils.support import Support, SupportTypes

# # SIMPLE EXAMPLE FOR TESTING
# b = Beam(L=0.5)
# b.add_load(Load(-1000, LoadTypes.centered, 0.3))
# model = Model(b, app=True)
# model.solve()

# # Q1
# b = Beam(L=5)
# b.remove_support(0.0)
# b.add_support(Support(0.0, SupportTypes.pinned))
# b.add_support(Support(5.0, SupportTypes.roller))
# b.add_load(Load(-10, LoadTypes.centered, 1.0))
# b.add_load(Load(-20, LoadTypes.centered, 2.0))
# b.add_load(Load(-20, LoadTypes.centered, 3.0))
# model = Model(b, app=True)
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
# b = Beam(L=10)
# b.remove_support(0.0)
# b.add_support(Support(0.0, SupportTypes.roller))
# b.add_support(Support(10.0, SupportTypes.pinned))
# b.add_load(Load(-5, LoadTypes.uniformlyDistributed, 5.0, 10.0))
# b.add_load(Load(-15, LoadTypes.centered, 5.0))
# model = Model(b, bound_conds=BOUNDARY_CONDITIONS, app=True)
# model.solve()

# Q3
# b = Beam(L=4)
# b.remove_support(0.0)
# b.add_support(Support(4.0, SupportTypes.fixed))
# b.add_load(Load(-2, LoadTypes.centered, 0.0))
# b.add_load(Load(-1.5, LoadTypes.uniformlyDistributed, 2.0, 4.0))
# model = Model(b, app=True)
# model.solve()

b = Beam(L=4)
# b.remove_support(0.0)
b.add_support(Support(0.0, SupportTypes.pinned))
b.add_support(Support(4.0, SupportTypes.pinned))
b.add_load(Load(-100, LoadTypes.uniformlyDistributed, 0.0, 4.0))
model = Model(b, app=True)
model.solve()


# b = Beam(L=1500)
# b.add_load(Load(-10, LoadTypes.uniformlyDistributed, 0.0, 500))
# b.add_load(Load(-3000, LoadTypes.centered, 750.0))
# model = Model(b, app=True)
# model.solve()
