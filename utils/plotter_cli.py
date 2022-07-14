import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

plt.rcParams.update({
    'xtick.direction': 'in', 'ytick.direction': 'in', 'xtick.major.size': 5, 
    'xtick.minor.size': 3, 'xtick.minor.visible': True, 
    'ytick.minor.visible': True, 'ytick.major.size': 5, 'ytick.minor.size': 3, 
    'axes.linewidth': .8, 'axes.linewidth': .5,
    'legend.handlelength': 2.0, 'legend.fancybox': False, 'legend.edgecolor': 'black',
    'font.size': 12, 'grid.linewidth': .2
})


class PlotterCli:
    def __init__(self, beam):
        self.beam = beam
        self.load_positions = np.unique([l.start for l in self.beam.loads] + [l.end for l in self.beam.loads])
    
    def plot_model(self, xy, mesh_xy, internal_strain, inertia):
        x, y = xy
        mesh_x, mesh_y = mesh_xy
        vx, mx, ox, vvx = internal_strain
        
        mosaic = [["A", "A"], ["B", "B"],
                  ["C", "C"], ["D", "D"], ["E", "E"]]

        fig = plt.figure(constrained_layout=True, figsize=(10, 10))
        ax_dict = fig.subplot_mosaic(mosaic)
        
        for position in self.load_positions:
            for ax in ax_dict:
                ax_dict[ax].axvline(position, linestyle="--", color="dimgrey")
        
        ax_dict["A"].set_title("Shear Force [$V(x)$]")
        ax_dict["A"].plot(x, vx, color="blue", label="$V(x)$")
        ax_dict["A"].fill_between(x, vx, alpha=0.3, color="royalblue")
        ax_dict["A"].legend()

        ax_dict["B"].set_title("Bending-Moment [$M(x)$]")
        ax_dict["B"].plot(x, mx, color="red", label="$M(x)$")
        ax_dict["B"].fill_between(x, mx, alpha=0.3, color="salmon")
        ax_dict["B"].legend()

        ax_dict["C"].set_title("Angle [$\epsilon$]")
        ax_dict["C"].plot(x, ox, color="orange", label="$\\theta(x)$")
        ax_dict["C"].fill_between(x, ox, alpha=0.3, color="gold")
        ax_dict["C"].legend()

        ax_dict["D"].set_title("Displacement [$\\nu(x)$]")
        ax_dict["D"].plot(x, vvx, color="limegreen", label="$\\nu(x)$")
        ax_dict["D"].text(x[np.abs(vvx).argmax()], vvx[np.abs(vvx).argmax()],
                        f"Max: {round(vvx[np.abs(vvx).argmax()], 2)}\nPos: {round(x[np.abs(vvx).argmax()], 2)}",
                        bbox=dict(facecolor='white', edgecolor='black'))
        ax_dict["D"].fill_between(x, vvx, alpha=0.3, color="springgreen")
        ax_dict["D"].legend()

        ax_dict["E"].set_title("Tension [$\sigma_{zz}$]")
        self._plot_contour_labels(ax_dict["E"], mesh_x, mesh_y, inertia)
        plt.show()
        
        return fig
    
    @staticmethod    
    def _plot_contour_labels(ax, x, y, function, f_cmap=cm.jet, levels=20):
        ax.contourf(x, y, function, cmap=f_cmap, levels=levels, alpha=.75, label="$\sigma_{zz}$")
        labels = ax.contour(x, y, function, colors="black", levels=levels, alpha=.75)
        
        if np.max(function) > 999:
            ax.clabel(labels, inline=1, fontsize=10, fmt=np.format_float_scientific)
        else:
            ax.clabel(labels, inline=1, fontsize=10)
        
        