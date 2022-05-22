from enum import Enum


class LoadTypes(Enum):
    """
    """

    centered = "centered"
    uniformlyDistributed = "uniformly_distributed"
    uniformlyVarying = "uniformly_varying"


class Load:
    """
    """

    def __init__(self, magnitude: float, category: LoadTypes, start: float, end: float = None):
        self.magnitude = float(magnitude)
        self.category = category
        self.start = float(start)
        self.end = float(end) if end else None

        self._handle_invalid_inputs()

    def _handle_invalid_inputs(self):
        assert isinstance(self.category, LoadTypes), "Category must be a `LoadTypes` instance."
        if self.category == LoadTypes.centered:
            self.end = None

        elif self.end is None:
            print(f"End position not found. Changing type from {self.category} to {LoadTypes.centered}")
            self.category = LoadTypes.centered

    def __repr__(self):
        return f"Load([{self.start}{':' + str(self.end) if self.end else ''}], {self.magnitude})"
