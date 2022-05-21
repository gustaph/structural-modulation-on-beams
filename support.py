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

    def __init__(self, position: float, category: SupportTypes) -> None:
        self.position = float(position)
        self.category = SupportTypes(category)

    def __repr__(self):
        return f"Support({self.position}, {self.category})"
