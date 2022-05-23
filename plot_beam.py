import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np
from support import Support, SupportTypes
from load import Load, LoadTypes
from typing import List
from datetime import datetime
from itertools import cycle


# Hyperparameters
WIDTH = -2
HEIGHT = 2
LINE_WIDTH = 5
FIG_YLIM = (-(HEIGHT/2) * 1.1, (HEIGHT/2) * 1.1)
COORD_X_SCALE = 0.02
COORD_Y_SCALE = 0.15

SUPP_FIXED_WIDTH_SCALE = 0.1
ARROW_COLOR = "red"
SECONDARY_COLOR = "black"

HATCH_SUPPORTS = "//"

TEXT_SPACE = 0.06 * HEIGHT
Y_DISTANCE = 0.25 * HEIGHT

N_ARROWS_SCALE = 2
ARROW_WIDTH_PERCENT = 0.04
UNIF_VAR_SLOPE = 0.1


class Plot:
    def __init__(self, L: float, supports: List[Support], loads: List[Load]):
        self.L = L
        self.supports = supports.values()
        self.loads = loads
        self.img_filename = f"plots/plot_{datetime.now().strftime('%Y%d%d%H%M')}.jpg"

    def draw(self, save=False):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_ylim(FIG_YLIM)
        ax.set_yticks([])

        ax.plot([0, self.L], [0, 0], color="black", linewidth=5)
        support_patches = self._plot_supports(ax)
        load_patches = self._plot_loads(ax)

        for patch in support_patches + load_patches:
            ax.add_patch(patch)

        if save:
            plt.savefig(self.img_filename, dpi=800)
            plt.close(fig)
        else:
            plt.show()

    def _get_coordinates(self, center, L):
        x, y = center
        scale_x = COORD_X_SCALE * L
        scale_y = COORD_Y_SCALE * FIG_YLIM[1]
        return (scale_x, scale_y), [(x - scale_x, y - scale_y), center, (x + scale_x, y - scale_y)]

    def _draw_triangle(self, center, L, ax):
        scale, coords = self._get_coordinates(center, L)
        triangle = plt.Polygon(coords, fill=False, hatch=HATCH_SUPPORTS)
        ax.add_patch(triangle)

        return scale, coords

    def _plot_supports(self, ax: plt.Axes):
        patch_elements = []
        for support in self.supports:
            if support.category == SupportTypes.roller:
                (scale_x, scale_y), coords = self._draw_triangle((support.position, -0.025),
                                                                 self.L, ax)
                penalty = cycle([scale_x/2.5, -scale_x/2])
                del coords[1]

                x = [value[0] + next(penalty) for value in coords]
                y = [value[1] - scale_y/5 for value in coords]
                plt.scatter(x, y, s=65, color=SECONDARY_COLOR)

            elif support.category == SupportTypes.pinned:
                _ = self._draw_triangle((support.position, -0.025), self.L, ax)

            elif support.category == SupportTypes.fixed:
                alpha = 0.0
                if support.position == self.L:
                    alpha = -WIDTH/2

                patch = patches.Rectangle((support.position + alpha, -HEIGHT/2),
                                          width=-SUPP_FIXED_WIDTH_SCALE * self.L,
                                          height=HEIGHT, hatch=HATCH_SUPPORTS,
                                          fill=False)
                patch_elements.append(patch)

        return patch_elements

    def _plot_loads(self, ax):
        patch_elements = []
        for load in self.loads:
            text = f"{load.magnitude}N"
            if load.magnitude < 0:
                y, dy = Y_DISTANCE, -Y_DISTANCE
            else:
                y, dy = 0, Y_DISTANCE

            if load.category == LoadTypes.centered:
                arrow = patches.Arrow(x=load.start, y=y, dx=0, dy=dy, color=ARROW_COLOR,
                                      width=ARROW_WIDTH_PERCENT * self.L)

                ax.text(load.start, Y_DISTANCE + TEXT_SPACE, s=text, ha='center', va='top',
                        weight='normal', fontfamily='monospace', fontsize='large')
                patch_elements.append(arrow)

            elif load.category == LoadTypes.uniformlyDistributed:
                n_arrows = int(N_ARROWS_SCALE * np.abs(load.end - load.start))
                arrow_positions = np.linspace(load.start, load.end, n_arrows)

                arrows = [patches.Arrow(x=position, y=Y_DISTANCE, dx=0, dy=-Y_DISTANCE,
                                        color=ARROW_COLOR, width=ARROW_WIDTH_PERCENT * self.L)
                          for position in arrow_positions]

                ax.text((load.end + load.start)/2, Y_DISTANCE + TEXT_SPACE, s=text, ha='center', va='top',
                        weight='normal', fontfamily='monospace', fontsize='large')

                ax.plot([load.start, load.end],
                        [Y_DISTANCE, Y_DISTANCE],
                        color=ARROW_COLOR, lw=3)

                patch_elements.extend(arrows)

            elif load.category == LoadTypes.uniformlyVarying:
                distance = np.abs(load.end - load.start)
                n_arrows = int(N_ARROWS_SCALE * distance)
                arrow_positions = np.linspace(load.start, load.end, n_arrows)

                ax.plot([load.start, load.end],
                        [Y_DISTANCE-UNIF_VAR_SLOPE, Y_DISTANCE+UNIF_VAR_SLOPE],
                        color=ARROW_COLOR, lw=3)
                
                lengths = np.linspace(Y_DISTANCE-UNIF_VAR_SLOPE, Y_DISTANCE+UNIF_VAR_SLOPE, n_arrows)

                arrows = [patches.Arrow(x=position, y=length, dx=0, dy=-length,
                                        color=ARROW_COLOR, width=ARROW_WIDTH_PERCENT * self.L)
                          for position, length in zip(arrow_positions, lengths)]

                ax.text((load.end + load.start)/2, Y_DISTANCE + TEXT_SPACE + UNIF_VAR_SLOPE/2, s=text, ha='center', va='top',
                        weight='normal', fontfamily='monospace', fontsize='large')
                
                patch_elements.extend(arrows)

        return patch_elements
