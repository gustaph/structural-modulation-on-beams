import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np
from support import Support, SupportTypes
from load import Load
from typing import List

# Hyperparameters
WIDTH = -2
HEIGHT = 1
LINE_WIDTH = 5

HATCH_FIXED = "//"
HATCH_ROLLER = "OO"

TEXT_SPACE = 0.06 * HEIGHT
Y_DISTANCE = 0.35 * HEIGHT


class Plot:
    def __init__(self, L: float, supports: List[Support], loads: List[Load]):
        self.L = L
        self.supports = supports
        self.loads = loads

    def plot(self):
        fig, ax = plt.subplots(figsize=(15, 6))
        ax.plot(range(np.floor(self.L).astype(int)),
                [0] * np.floor(self.L).astype(int), color="black", linewidth=5)

        support_patches = self._plot_supports(ax)
        load_patches = self._plot_loads(ax)

        for patch in support_patches + load_patches:
            ax.add_patch(patch)

        plt.show()

    def _plot_supports(self, ax: plt.Axes):
        patch_elements = []
        for support in self.supports:
            if support.type == SupportTypes.roller:
                pass

            elif support.type == SupportTypes.pinned:
                pass

            elif support.type == SupportTypes.fixed:
                alpha = 0.0
                if support.position == self.L:
                    alpha = -WIDTH/2

                patch = patches.Rectangle((support.position + alpha, -HEIGHT/2),
                                      width=WIDTH,
                                      height=HEIGHT,
                                      hatch=HATCH_FIXED,
                                      fill=False)
                patch_elements.append(patch)

        return patch_elements

    def _plot_loads(self, ax):
        patch_elements = []
        for load in self.loads:
            arrow = patches.Arrow(x=load.position, y=Y_DISTANCE,
                              dx=0, dy=-Y_DISTANCE, color="red", width=0.6, clip_on=False)
            text = f"{load.magnitude}N"
            ax.text(load.position, Y_DISTANCE + TEXT_SPACE, s=text, ha='center', va='top',
                    weight='normal', fontfamily='monospace', fontsize='large')
            patch_elements.append(arrow)

        return patch_elements


if __name__ == '__main__':
    p = p = Plot(20, [Support(0.0, "fixed"), Support(20.0, "fixed")],
                 [Load(5.0, 15.0), Load(10.0, 20.0), Load(12.0, 250.0)])
    p.plot()
