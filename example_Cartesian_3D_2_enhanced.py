import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import customplot

mpl.rcParams['savefig.directory'] = '.'
mpl.rcParams['figure.dpi']        = 120

grapher = customplot.CustomPlot(dim = 3)
grapher.axis_fix('x', symbolic = True, first = -6, last = 6, step = 1)
grapher.axis_fix('y', symbolic = True, first = -6, last = 6, step = 1)
grapher.axis_fix('z', first = -3, last = 3, step = 1)

x = np.linspace(-6 * np.pi, 6 * np.pi, 1000)
y = np.linspace(-6 * np.pi, 6 * np.pi, 1000)
X, Y = np.meshgrid(x, y)
Z = 1.5 * np.cos(X / 2) * np.sin(Y / 5)
surf = grapher.ax.plot_surface(X, Y, Z, color = 'skyblue', label = r'$z=1.5\cdot\cos\,0.5x\cdot\sin\,0.2y$')
surf._facecolors2d = surf._edgecolors2d = None

grapher.configure()
grapher.aspect_fix(1)

plt.show()
plt.close(grapher.fig)

