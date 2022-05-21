from load import Load
from support import Support, SupportTypes
from plot_beam import Plot
from pprint import pprint


class Beam:
    """
    """

    def __init__(self, L: float):
        self.L = L
        self.supports = {0.0: Support(0.0, SupportTypes.fixed)}
        self.loads = dict()

    def add_load(self, load: Load) -> None:
        assert 0 <= load.position <= self.L, f"{load} position must be within the limits of the beam."
        assert not self.loads.__contains__(
            load.position), f"Position {load.position} already has a load"
        self.loads[load.position] = load

    def add_support(self, support: Support) -> None:
        assert support.position in (
            0.0, self.L), f"A support can only be added at the edges of the beam."
        assert 0 <= support.position <= self.L, f"{support} position must be within the limits of the beam."
        assert not self.supports.__contains__(
            support.position), f"Position {support.position} already has a support"
        self.supports[support.position] = support

    def remove_load(self, position: float) -> None:
        assert self.loads.__contains__(
            position), "Beam does not have a Load in position {position}."
        load = self.loads.pop(position)
        print(f"[*] {load} removed from Beam.")

    def remove_support(self, position: float) -> None:
        assert self.supports.__contains__(
            position), "Beam does not have a Support in position {position}."
        support = self.supports.pop(position)
        print(f"[*] {support} removed from Beam.")
