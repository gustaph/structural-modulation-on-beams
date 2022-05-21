import numpy as np
from enum import Enum


class SupportTypes(Enum):
    """
    """

    roller = "roller"
    pinned = "pinned"
    fixed = "fixed"


class Support:
    """
    """

    def __init__(self, position: float, type: SupportTypes) -> None:
        self.position = float(position)
        self.type = SupportTypes(type)

    def __repr__(self):
        return f"Support({self.position}, {self.type})"
