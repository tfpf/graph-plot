import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import customplot

mpl.rcParams['savefig.directory'] = '.'

grapher = customplot.CustomPlot()
grapher.axis_fix('x', first = -2, last = 10, step = 1)
grapher.axis_fix('y', first = -2, last = 4, step = 1)

x = np.linspace(0, 8, 10000)
y = np.sqrt(x)
grapher.plot(x, y, color = 'red', label = r'$y=\sqrt{x}$')

grapher.configure()
grapher.aspect_fix(1)

plt.show()
plt.close(grapher.fig)

