import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import customplot

mpl.rcParams['savefig.directory'] = '.'
mpl.rcParams['figure.dpi']        = 120

grapher = customplot.CustomPlot(dim = 3)
grapher.axis_fix('x', first = 0, last = 12, step = 1)
grapher.axis_fix('y', first = -2, last = 2, step = 1)
grapher.axis_fix('z', first = -2, last = 2, step = 1)

x = np.linspace(0, 12, 10000)
y = (3 / 4) ** x * np.cos(np.pi * x)
z = (3 / 4) ** x * np.sin(np.pi * x)
grapher.plot(x, y, z, color = 'gray', label = r'$y+iz=\left(-\dfrac{3}{4}\right)^x$')

grapher.configure()
grapher.aspect_fix(1)

plt.show()
plt.close(grapher.fig)

