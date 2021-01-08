import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import customplot

mpl.rcParams['savefig.directory'] = '.'

grapher = customplot.CustomPlot()

x = np.linspace(-2 * np.pi, 2 * np.pi)
y = np.cos(x)
grapher.plot(x, y, label = 'cosine')

grapher.configure()

plt.show()
plt.close(grapher.fig)

