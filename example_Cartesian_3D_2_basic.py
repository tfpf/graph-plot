import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import customplot

mpl.rcParams['savefig.directory'] = '.'
mpl.rcParams['figure.dpi']        = 120

grapher = customplot.CustomPlot(dim = 3)

x = np.linspace(-6 * np.pi, 6 * np.pi)
y = np.linspace(-6 * np.pi, 6 * np.pi)
X, Y = np.meshgrid(x, y)
Z = 1.5 * np.cos(X / 2) * np.sin(Y / 5)
surf = grapher.ax.plot_surface(X, Y, Z, label = 'interference pattern')
surf._facecolors2d = surf._edgecolors2d = None

grapher.configure()

plt.show()
plt.close(grapher.fig)

