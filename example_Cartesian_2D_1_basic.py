import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import customplot

mpl.rcParams['savefig.directory'] = '.'

grapher = customplot.CustomPlot()

x = np.linspace(0, 8)
y = np.sqrt(x)
grapher.plot(x, y, label = 'square root')

grapher.configure()

plt.show()
plt.close(grapher.fig)

