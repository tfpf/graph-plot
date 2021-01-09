import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import customplot

mpl.rcParams['savefig.directory'] = '.'
mpl.rcParams['figure.dpi']        = 120

grapher = customplot.CustomPlot()

t = np.linspace(-np.pi, np.pi)
x = 3 * np.cos(t) + 1
y = 5 * np.sin(t) - 2
grapher.plot(x, y, label = 'ellipse')

grapher.configure()

plt.show()
plt.close(grapher.fig)

