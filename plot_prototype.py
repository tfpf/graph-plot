#!/usr/bin/env python3

import matplotlib.patches as mp
import matplotlib.pyplot as pp
import numpy as np
import sys

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

# print a list neatly
def show_nice_list(items, columns = 2):

	# pad the list
	while len(items) % columns:
		items.append(' ')
	rows = int(len(items) / columns)

	# split the list
	subitems = []
	for i in range(rows):
		subitems.append(items[i :: rows])

	print([len(row[i]) for i in range(columns) for row in subitems])
	# widths = [max(len(subitems[:][i])) for i in range(columns)]
	# print(widths)

	for item in subitems:
		for i in item:
			sys.stdout.write(i.ljust(25))
			sys.stdout.flush()
		print()


################################################################################

# open a window to plot a graph
# a subplot is created so that it can be easily modified to plot multiple
# set the name of the plot window from the number in 'counter.txt'
# increment that number and write it back to 'counter.txt'
fig = pp.figure()
ax = fig.add_subplot(1, 1, 1)
with open('counter.txt') as count_file:
	graph_id = int(count_file.readline().strip())
fig.canvas.set_window_title('graph_{}'.format(graph_id))
with open('counter.txt', 'w') as count_file:
	print('{}'.format(graph_id + 1), file = count_file)

# choose a plot style
try:
	pp.style.use(sys.argv[1])
except IndexError:
	print('Plot style not specified. Using \'classic\'.')
	pp.style.use('classic')
	pp.style.use('bmh')
except OSError:
	print('Invalid plot style specified. Using \'classic\'.')
	pp.style.use('classic')
	pp.style.use('bmh')

# display available styles
show_nice_list(pp.style.available, 4)
# styles = pp.style.available
# while len(styles) % 3:
# 	styles.append(' ')
# left = int(len(styles) / 3)
# right = 2 * left
# for k in zip(styles[: left], styles[left : right], styles[right :]):
# 	for i in k:
# 		sys.stdout.write(i.ljust(25))
# 		sys.stdout.flush()
# 	print()

# display a thick line for the coordinate axes
ax.axhline(linewidth = 1.6, color = 'k')
ax.axvline(linewidth = 1.6, color = 'k')

################################################################################

# the statements which actually plot the graphs
# t = np.linspace(0, 10 * np.pi, 98257)
x1 = np.linspace(1, 150, 1e5)
y1 = (np.sin(x1 ** 2) - x1) / (np.cos(x1) ** 2 - x1)
ax.plot(x1, y1, 'r-', label = r'$y=\dfrac{\sin\,x^2-x}{\cos^2x-x}$', linewidth = 0.8)
# x2 = np.linspace(2, 10, 1e5)
# y2 = x2 - 4
# ax.plot(x2, y2, 'b-', label = r'$y=x-4$', linewidth = 0.8)
# x3 = np.linspace(0.2, 10, 1e5)
# y3 = 1 / x3
# ax.plot(x3, y3, 'g-', label = r'$y=\dfrac{1}{x}$', linewidth = 0.8)

################################################################################

# annotations: annotate points in the graph plot
# argument 1: annotation text
# argument 2: annotation location
# argument 3: annotation text location
# ax.annotate(r'$i^3$', xy = (0, -1), xytext = (0.05, -1.05))
# ax.add_patch(mp.Circle((0, -1), 0.03))
# ax.annotate(r'$i$', xy = (0, 1), xytext = (0.05, 0.95))
# ax.add_patch(mp.Circle((0, 1), 0.03))
# ax.annotate(r'$(10, 2)$', xy = (10, 2), xytext = (10.1, 2.3))
# ax.annotate(r'$(10, 10)$', xy = (10, 10), xytext = (10.1, 10.3))

################################################################################

# miscellaneous settings
ax.grid(True, linewidth = 0.4)
ax.legend(loc = 'best')
# ax.set_title('example')
ax.set_xlabel(r'$x$')
# ax.set_xlim(-2, 2)
# ax.set_xticklabels([r'$\mu-4\sigma$', r'$\mu-3\sigma$', r'$\mu-2\sigma$', r'$\mu-\sigma$', r'$\mu$', r'$\mu+\sigma$', r'$\mu+2\sigma$', r'$\mu+3\sigma$', r'$\mu+4\sigma$'])
# ax.set_xticklabels([r'$-4\pi$', r'$-3\pi$', r'$-2\pi$', r'$-\pi$', r'$0$', r'$\pi$', r'$2\pi$', r'$3\pi$', r'$4\pi$'])
# ax.set_xticks([i * np.pi for i in range(-4, 5)])
ax.set_xticklabels([r'${}\pi$'.format(i) for i in range(5, 51, 5)])
ax.set_xticks([i * np.pi for i in range(5, 51, 5)])
# ax.set_xticks([4, 6])
# ax.set_xticklabels(['invention of\ncamera', 'invention of\nphoto editing'])
ax.set_ylabel(r'$y$')
# ax.set_ylim(-4, 4)
# ax.set_yticklabels([r'$\dfrac{0.3989}{\sigma}$', r'$\dfrac{0.2420}{\sigma}$', r'$\dfrac{0.0540}{\sigma}$', r'$\dfrac{0.0044}{\sigma}$'])
# ax.set_yticks(np.array([0.3989, 0.2420, 0.0540, 0.0044]) / t)
# ax.set_yticklabels([r'${}$'.format(i) for i in ax.get_yticklabels()])
# fig.gca().set_aspect('equal', adjustable = 'box')
pp.show()
# ax.set_yticks([r'${}$'.format(i) for i in ax.get_yticks()])
