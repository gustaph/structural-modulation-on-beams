from load import Load, LoadTypes
from support import Support, SupportTypes
from plot_beam import Plot
from typing import Tuple


class Beam:
    """
    """

    def __init__(self, L: float):
        self.L = float(L)
        self.supports = {0.0: Support(0.0, SupportTypes.fixed)}
        self.loads = list()
        self.taken_positions = list()

    def _is_intersection(self, a: Tuple[float, float], b: Tuple[float, float]):
        """

        reference: https://www.youtube.com/watch?v=bbTqI0oqL5U
        """
        p1, p2 = a
        p3, p4 = b

        return ((p3 >= p1) and (p3 <= p2)) or ((p4 >= p1) and (p4 <= p2))

    def _validate_load_input(self, start: float, end: float):
        if self.taken_positions == []:
            return True
        end = start if end is None else end

        for position in self.taken_positions:
            validate = self._is_intersection((start, end), position)
            if validate:
                return False

        return True

    def add_load(self, load: Load) -> None:
        assert 0.0 <= load.start <= self.L, f"{load} position must be within the limits of the beam."
        if load.end:
            assert 0.0 <= load.end <= self.L, f"{load} position must be within the limits of the beam."
        assert self._validate_load_input(load.start, load.end), f"There is another load between position {(load.start, load.end)}."
        self.taken_positions.append((load.start, load.end if load.end else load.start))
        self.loads.append(load)

    def add_support(self, support: Support) -> None:
        assert (support.category == SupportTypes.fixed) and support.position in (0.0, self.L), f"A support can only be added at the edges of the beam."
        assert 0 <= support.position <= self.L, f"{support} position must be within the limits of the beam."
        assert not self.supports.__contains__(support.position), f"Position {support.position} already has a support"
        self.supports[support.position] = support

    def remove_load(self, position: Tuple) -> None:
        assert position in self.taken_positions, "Beam does not have a Load in position {position}."
        index = self.taken_positions.index(position)
        del self.loads[index]
        del self.taken_positions[index]

    def remove_support(self, position: float) -> None:
        assert self.supports.__contains__(position), "Beam does not have a Support in position {position}."
        support = self.supports.pop(position)
        print(f"[*] {support} removed from Beam.")

    def draw(self, save=False):
        plot_object = Plot(self.L, self.supports, self.loads)
        plot_object.draw(save)
        
        return plot_object.img_filename