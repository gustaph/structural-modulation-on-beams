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
        self.start = start
        self.end = end
        self.magnitude = magnitude
        self.category = category

        self._handle_invalid_type()

    def _handle_invalid_type(self):
        if self.category == LoadTypes.centered:
            self.end = None

    def __repr__(self):
        return f"Load([{self.start}{':' + str(self.end) if self.end else ''}], {self.magnitude})"
