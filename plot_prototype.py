#!/usr/bin/env python3

import matplotlib.pyplot as pp
import numpy as np

################################################################################

# tetration: this should compute x ^^ n
# where ^^ denotes tetration (using Knuth Arrow notation)
# x ^^ n = x ** (x ** x ** (...)) 'n' times
# look up tetration for more information
def tetration(x, n):
	base = x
	result = base
	n -= 1
	while n:
		result = base ** result
		n -= 1
	return result

################################################################################

# open a window to plot a graph
# a subplot is created so that it can be easily modified to plot multiple
# set the name of the plot window from the number in 'counter.txt'
# increment that number and write it back to 'counter.txt'
fig = pp.figure()
ax = fig.add_subplot(1, 1, 1)
with open('counter.txt') as count_file:
	graph_id = int(count_file.readline())
fig.canvas.set_window_title('graph_%x' % graph_id)
print('run #{}'.format(graph_id))
with open('counter.txt', 'w') as count_file:
	count_file.write('%d' % (graph_id + 1))

# choose a plot style
# print(pp.style.available)
# pp.style.use('classic')

# display a thick line for the coordinate axes
ax.axhline(linewidth = 1.6, color = 'k')
ax.axvline(linewidth = 1.6, color = 'k')

################################################################################

# the statements which actually plot the graphs
# t = np.linspace(0, 10 * np.pi, 98257)
x1 = np.linspace(4, 100, 1e5)
y1 = (np.sin(x1 ** 2) - x1) / (np.cos(x1) ** 2 - x1)
ax.plot(x1, y1, 'r-', label = r'$y=\dfrac{\sin\,x^2-x}{\cos^2x-x}$', linewidth = 0.8)
# y2 = np.linspace(-4, 4, 38601)
# x2 = np.zeros(len(y2))
# ax.plot(x2, y2, 'r-', linewidth = 0.8)

################################################################################

# annotations: annotate points in the graph plot
# argument 1: annotation text
# argument 2: annotation location
# argument 3: annotation text locationfrequency of miracles
# ax.annotate(r'$(0, 0)$', xy = (0, 0), xytext = (0, 0))
# ax.annotate(r'$(8.5, 11.5)$', xy = (8.5, 11.5), xytext = (7.3, 13.5))
# ax.annotate(r'$(10, 2)$', xy = (10, 2), xytext = (10.1, 2.3))
# ax.annotate(r'$(10, 10)$', xy = (10, 10), xytext = (10.1, 10.3))

################################################################################

# miscellaneous settings
ax.grid(True, linewidth = 0.4)
ax.legend(loc = 'upper right')
# ax.set_title('example')
ax.set_xlabel(r'$x$')
# ax.set_xlim(-4, 4)
# ax.set_xticklabels([r'$\mu-4\sigma$', r'$\mu-3\sigma$', r'$\mu-2\sigma$', r'$\mu-\sigma$', r'$\mu$', r'$\mu+\sigma$', r'$\mu+2\sigma$', r'$\mu+3\sigma$', r'$\mu+4\sigma$'])
# ax.set_xticks([i * np.pi for i in range(-4, 5)])
ax.set_ylabel(r'$y$')
# ax.set_ylim(-2, 2)
# ax.set_yticklabels([r'$\dfrac{0.3989}{\sigma}$', r'$\dfrac{0.2420}{\sigma}$', r'$\dfrac{0.0540}{\sigma}$', r'$\dfrac{0.0044}{\sigma}$'])
# ax.set_yticks(np.array([0.3989, 0.2420, 0.0540, 0.0044]) / t)
# fig.gca().set_aspect('equal', adjustable = 'box')
pp.show()
