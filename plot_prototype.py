#!/usr/bin/env python

import matplotlib.pyplot as pp
import numpy as np

################################################################################

'''
	tetration: this should compute x ^^ n
	where ^^ denotes tetration (using Knuth Arrow notation)
	x ^^ n = x ** (x ** x ** (...)) 'n' times
	look up tetration for more information
'''
def tetration(x, n):
	base = x
	result = base
	n -= 1
	while n:
		result = base ** result
		n -= 1
	return result

################################################################################

'''
	the file 'counter.txt' contains a number
	this number will be used to name any graph that is plotted
	use this number to set the window name of the new graph
	read this number, then increment it and write it to the file
	the new number will be used for the next plot
	it ensures that each graph plot has a unique name
'''
with open('counter.txt') as count_file:
	graph_id = int(count_file.readline().strip())
fig = pp.figure()
fig.canvas.set_window_title('graph_%x' % graph_id)
graph_id += 1
with open('counter.txt', 'w') as count_file:
	count_file.write('%d\n' % graph_id)

# display a thick line for the coordinate axes
ax = fig.add_subplot(1, 1, 1)
ax.axhline(linewidth = 1.5, color = 'k')
ax.axvline(linewidth = 1.5, color = 'k')

################################################################################

'''
	list of equations which are used to plot graphs
	necessary ones may be uncommented
	remember to also uncomment the corresponding plot statements
'''
# t = np.linspace(0, 2 * np.pi, 98756)
x1 = np.linspace(0, 12, 39257)
y1 = np.sqrt(x1)
# x2 = np.linspace(-1, np.pi + 1, 98734)
# y2 = np.sin(3 * x2)

################################################################################

'''
	readymade list of plot statements to plot graphs
	just edit and uncomment what is needed
	make sure that the variable definitions above match these plot statements
'''
ax.plot(x1, y1, 'r-', label = r'$y=\sqrt{x}$', linewidth = 0.8)
# ax.plot(x2, y2, 'b-', label = r'$y=\sin\,3x$', linewidth = 0.8)
# ax.plot(x3, y3, 'g-', label = r'$x=10$', linewidth = 0.8)
# ax.plot(x4, y4, 'y-', label = r'$y=x+3$', linewidth = 0.8)
# ax.plot(x5, y5, 'c-', label = r'$y=-x-\dfrac{x^2}{2}-\dfrac{x^3}{3}-\dfrac{x^4}{4}$', linewidth = 0.8)

################################################################################

'''
	annotations: annotate points in the graph plot
	argument 1: annotation text
	argument 2: annotation location
	argument 3: annotation text location
'''
# ax.annotate(r'$(3, 9)$', xy = (0.2, 0.3), xytext = (0.4, 0.5))
# ax.annotate(r'$(8.5, 11.5)$', xy = (8.5, 11.5), xytext = (7.3, 13.5))
# ax.annotate(r'$(10, 2)$', xy = (10, 2), xytext = (10.1, 2.3))
# ax.annotate(r'$(10, 10)$', xy = (10, 10), xytext = (10.1, 10.3))

################################################################################

'''
	miscellaneous settings
	tweak the plot to make it 'complete'
'''
ax.grid(True)
ax.legend()
# ax.set_title('example')
ax.set_xlabel(r'$x$')
# ax.set_xlim(-1, np.pi + 1)
# ax.set_xticks([])
ax.set_ylabel(r'$y$')
# ax.set_ylim(-1, 1)
# ax.set_yticks([])
# fig.gca().set_aspect('equal', adjustable = 'box')
pp.show()
