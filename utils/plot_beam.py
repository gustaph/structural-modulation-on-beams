import numpy as np
from typing import List
from matplotlib import patches
import matplotlib.pyplot as plt
from datetime import datetime
from itertools import cycle

from .support import Support, SupportTypes
from .load import Load, LoadTypes


# Hyperparameters
WIDTH = -2
HEIGHT = 2
LINE_WIDTH = 5
FIG_YLIM = (-(HEIGHT/2) * 0.5, (HEIGHT/2) * 0.8)
COORD_X_SCALE = 0.02
COORD_Y_SCALE = 0.15

SUPP_FIXED_WIDTH_SCALE = 0.1
ARROW_COLOR = "red"
SECONDARY_COLOR = "black"

HATCH_SUPPORTS = "//"

TEXT_SPACE = 0.06 * HEIGHT
Y_DISTANCE = 0.20 * HEIGHT

N_ARROWS_SCALE = 2
ARROW_WIDTH_PERCENT = 0.04
UNIF_VAR_SLOPE = 0.2


class Plot:
    def __init__(self, L: float, supports: List[Support], loads: List[Load], app: bool = False):
        self.L = L
        self.supports = supports.values()
        self.loads = loads
        self.x_positions = np.unique([l.start for l in self.loads] + [l.end for l in self.loads])
        self.ax_beam = None
        
        now = datetime.now().strftime('%Y%d%d%H%M')
        self.beam_filename = f"../plots/beam/plot_{now}.jpg"
        self.strain_filename = f"../plots/strain/plot_{now}.jpg"
        
        if app:
            self.beam_filename = self.beam_filename[3:]
            self.strain_filename = self.strain_filename[3:]
    
    def plot_model(self, internal_strain=None, save=False):
        plot_complete_model = False
        if internal_strain is not None:
            assert len(internal_strain) == 3, "`internal_strain` must contain 3 elements (x, shear, bending)"
            figsize = (10, 8)
            x, shear, bending = internal_strain
            plot_complete_model = True
            nrows, ncols = 3, 1
            gridspec_kw = {"height_ratios": [1, 0.5, 0.5]}
            
        else:
            figsize = (10, 5)
            nrows, ncols = 1, 1
            gridspec_kw = {}
            
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize, sharex=True, squeeze=False,
                                 constrained_layout=True, gridspec_kw=gridspec_kw)
        axes = axes.flatten()
        
        axes[0].set_ylim(FIG_YLIM)
        axes[0].plot([0, self.L], [0, 0], color="black", linewidth=5)
        axes[0].set_xticks(list(axes[0].get_xticks()) + self.x_positions.tolist())

        support_patches = self._plot_supports(axes[0])
        load_patches = self._plot_loads(axes[0])
        for patch in support_patches + load_patches:
            axes[0].add_patch(patch)
            
        if plot_complete_model:
            axes[1].plot(x, shear, color="royalblue")
            axes[1].fill_between(x, shear, alpha=0.3, color="royalblue")
            
            axes[2].plot(x, bending, color="salmon")
            axes[2].fill_between(x, bending, alpha=0.3, color="salmon")
            
            for position in self.x_positions.tolist():
                axes[0].axvline(position, ymax=0.4, linestyle="--", color="dimgrey")
                axes[1].axvline(position, linestyle="--", color="dimgrey")
                axes[2].axvline(position, linestyle="--", color="dimgrey")
            
            if save:
                plt.savefig(self.strain_filename, dpi=800)
                plt.close(fig)
            else:
                plt.show()
        else:
            axes[0].set_yticks([])
            if save:
                plt.savefig(self.beam_filename, dpi=800)
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
                ax.scatter(x, y, s=65, color=SECONDARY_COLOR)

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
                        [0, Y_DISTANCE+UNIF_VAR_SLOPE],
                        color=ARROW_COLOR, lw=3)
                
                lengths = np.linspace(0, Y_DISTANCE+UNIF_VAR_SLOPE, n_arrows)

                arrows = [patches.Arrow(x=position, y=length, dx=0, dy=-length,
                                        color=ARROW_COLOR, width=ARROW_WIDTH_PERCENT * self.L)
                          for position, length in zip(arrow_positions, lengths)]

                ax.text((load.end + load.start)/2, Y_DISTANCE + TEXT_SPACE + UNIF_VAR_SLOPE/2, s=text, ha='center', va='top',
                        weight='normal', fontfamily='monospace', fontsize='large')
                
                patch_elements.extend(arrows)

        return patch_elements
