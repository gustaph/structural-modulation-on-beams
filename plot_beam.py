import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np
from support import Support, SupportTypes
from load import Load, LoadTypes
from typing import List

# Hyperparameters
WIDTH = -2
HEIGHT = 1
LINE_WIDTH = 5

HATCH_FIXED = "//"
HATCH_ROLLER = "OO"

TEXT_SPACE = 0.06 * HEIGHT
Y_DISTANCE = 0.25 * HEIGHT

N_ARROWS_MULTIPLIER = 2
ARROW_WIDTH = 0.4
UNIF_VAR_SLOPE = 0.1

class Plot:
    def __init__(self, L: float, supports: List[Support], loads: List[Load]):
        self.L = L
        self.supports = supports
        self.loads = loads

    def plot(self):
        fig, ax = plt.subplots(figsize=(15, 6))
        ax.plot([0, self.L], [0, 0], color="black", linewidth=5)

        support_patches = self._plot_supports(ax)
        load_patches = self._plot_loads(ax)

        for patch in support_patches + load_patches:
            ax.add_patch(patch)

        plt.show()

    def _plot_supports(self, ax: plt.Axes):
        patch_elements = []
        for support in self.supports:
            if support.category == SupportTypes.roller:
                pass

            elif support.category == SupportTypes.pinned:
                pass

            elif support.category == SupportTypes.fixed:
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
            text = f"{load.magnitude}N"

            if load.category == LoadTypes.centered:
                arrow = patches.Arrow(x=load.start, y=Y_DISTANCE,
                                      dx=0, dy=-Y_DISTANCE, color="red", width=ARROW_WIDTH)

                ax.text(load.start, Y_DISTANCE + TEXT_SPACE, s=text, ha='center', va='top',
                        weight='normal', fontfamily='monospace', fontsize='large')
                patch_elements.append(arrow)

            elif load.category == LoadTypes.uniformlyDistributed:
                distance = np.abs(load.end - load.start)
                n_arrows = int(N_ARROWS_MULTIPLIER * distance)
                arrow_positions = np.linspace(load.start, load.end, n_arrows)
                
                arrows = [patches.Arrow(x=position, y=Y_DISTANCE, dx=0, dy=-Y_DISTANCE, color="red", width=ARROW_WIDTH)
                          for position in arrow_positions]

                ax.text((distance / 2) + load.start, Y_DISTANCE + TEXT_SPACE, s=text, ha='center', va='top',
                        weight='normal', fontfamily='monospace', fontsize='large')

                ax.plot([load.start, load.end], [Y_DISTANCE, Y_DISTANCE], color="red", lw=3)

                patch_elements.extend(arrows)

            elif load.category == LoadTypes.uniformlyVarying:
                distance = np.abs(load.end - load.start)
                n_arrows = int(N_ARROWS_MULTIPLIER * distance)
                arrow_positions = np.linspace(load.start, load.end, n_arrows)
                
                ax.plot([load.start, load.end], [Y_DISTANCE-UNIF_VAR_SLOPE, Y_DISTANCE+UNIF_VAR_SLOPE], color="red", lw=3)
                lengths = np.linspace(Y_DISTANCE-UNIF_VAR_SLOPE, Y_DISTANCE+UNIF_VAR_SLOPE, n_arrows)
                
                arrows = [patches.Arrow(x=position, y=length, dx=0, dy=-length, color="red", width=ARROW_WIDTH)
                          for position, length in zip(arrow_positions, lengths)]

                ax.text((distance / 2) + load.start, Y_DISTANCE + TEXT_SPACE + UNIF_VAR_SLOPE/2, s=text, ha='center', va='top',
                        weight='normal', fontfamily='monospace', fontsize='large')


                patch_elements.extend(arrows)

        return patch_elements


if __name__ == '__main__':
    # p = Plot(20, [Support(0.0, "fixed"), Support(20.0, "fixed")],
    #              [Load(15.0, LoadTypes.centered, 5.0),
    #              Load(20.0, LoadTypes.centered, 10.0),
    #              Load(1000.0, LoadTypes.centered, 15.0)])

    # p = Plot(20.5, [Support(0.0, "fixed")], [
    #          Load(15.0, LoadTypes.uniformlyDistributed, 5.0, 10.0)])
    
    p = Plot(20.5, [Support(0.0, "fixed")], [
             Load(15.0, LoadTypes.uniformlyVarying, 2.0, 10.0)])
    
    p.plot()
