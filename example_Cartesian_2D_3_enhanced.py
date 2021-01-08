import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import customplot

mpl.rcParams['savefig.directory'] = '.'

grapher = customplot.CustomPlot()
grapher.axis_fix('x', first = -3, last = 5, step = 1)
grapher.axis_fix('y', first = -9, last = 4, step = 1)

t = np.linspace(-np.pi, np.pi, 10000)
x = 3 * np.cos(t) + 1
y = 5 * np.sin(t) - 2
grapher.plot(x, y, label = r'$\dfrac{(x-1)^2}{9}+\dfrac{(y+2)^2}{25}=1$')

grapher.configure()
grapher.aspect_fix(1)

plt.show()
plt.close(grapher.fig)

