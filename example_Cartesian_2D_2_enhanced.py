import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import customplot

mpl.rcParams['savefig.directory'] = '.'
mpl.rcParams['figure.dpi']        = 120

grapher = customplot.CustomPlot()
grapher.axis_fix('x', symbolic = True, first = -2, last = 2, step = 1 / 4)
grapher.axis_fix('y', first = -3, last = 3, step = 1)

x = np.linspace(-2 * np.pi, 2 * np.pi, 10000)
y = np.cos(x)
grapher.plot(x, y, color = 'green', label = r'$y=\cos\,x$')

grapher.configure()
grapher.aspect_fix(1)

plt.show()
plt.close(grapher.fig)

