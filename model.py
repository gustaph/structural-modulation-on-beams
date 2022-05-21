import numpy as np
from beam import Beam
import simpy


class Model:
    def __init__(self, beam):
        self.beam = beam

        self.M = None  # momentum
        self.V = None  # shear force
        self.q = None
