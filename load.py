class Load:
    """
    """

    def __init__(self, position: float, magnitude: float):
        self.position = position
        self.magnitude = magnitude

    def __repr__(self):
        return f"Load({self.position}, {self.magnitude})"
