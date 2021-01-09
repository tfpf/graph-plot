import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import customplot

mpl.rcParams['savefig.directory'] = '.'
mpl.rcParams['figure.dpi']        = 120

grapher = customplot.CustomPlot(dim = 3)

x = np.linspace(0, 12)
y = (3 / 4) ** x * np.cos(np.pi * x)
z = (3 / 4) ** x * np.sin(np.pi * x)
grapher.plot(x, y, z, label = 'spiral')

grapher.configure()

plt.show()
plt.close(grapher.fig)

