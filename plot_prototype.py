#!/usr/bin/env python3

import colorama
import matplotlib.patches as mp
import matplotlib.pyplot as pp
import numpy as np
import sys

with pp.xkcd():
	# Based on "The Data So Far" from XKCD by Randall Munroe
	# http://xkcd.com/373/

	fig = pp.figure()
	ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
	x1 = np.linspace(0, 10, 100000)
	y1 = 0.1 * np.random.randn(100000) + 8
	y1[40000 : 60000] = 0
	ax.plot(x1, y1, 'r-', label = r'trends of supernatural miracles', linewidth = 0.8)
	# ax.bar([0, 1], [0, 100], 0.25)
	ax.spines['right'].set_color('none')
	ax.spines['top'].set_color('none')
	ax.xaxis.set_ticks_position('bottom')
	ax.set_xticks([4, 6])
	# ax.set_xlim([-0.5, 1.5])
	# ax.set_ylim([0, 110])
	ax.set_xticklabels(['invention of\nthe camera', 'invention of image\nediting software'])
	pp.yticks([])
	# pp.xlabel('time')
	pp.legend()
	pp.ylabel('frequency of miracles')

	# pp.title("CLAIMS OF SUPERNATURAL POWERS")

	# fig.text(
	# 	0.5, 0.05,
	# 	'"The Data So Far" from xkcd by Randall Munroe',
	# 	ha='center')

pp.show()

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

# print a list neatly in columns
def show_nice_list(items, columns = 3):

	# pad the list and split it into equal-length rows
	while len(items) % columns:
		items.append('')
	rows = int(len(items) / columns)
	items = [items[i :: rows] for i in range(rows)]

	# find out the maximum width of all columns
	# then use those maximum widths to justify all columns
	widths = [max([len(row[i]) for row in items]) for i in range(columns)]
	for row in items:
		for r, width in zip(row, widths):
			sys.stdout.write(r.rjust(width + 1))
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
	# pp.style.use(sys.argv[1])
	pass
except (IndexError, OSError):
	colorama.init(autoreset = True) # to allow coloured text on Windows
	print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}Plot style either not specified or invalid. Using \'classic\'.')
	colorama.deinit()
	pp.style.use('classic')
print('available styles:')
show_nice_list(pp.style.available)

################################################################################

# set up variables to plot graphs
# t = np.linspace(0, 10 * np.pi, 98257)
x1 = np.linspace(0, 10, 100000)
y1 = 0.1 * np.random.randn(100000) + 8
y1[40000 : 60000] = 0
ax.plot(x1, y1, 'r-', label = r'trends of supernatural miracles', linewidth = 0.8)
# x2 = np.linspace(0, 10, 1e5)
# y2 = x2
# ax.plot(x2, y2, 'b-', label = r'$y=x$', linewidth = 0.8)
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
pp.xkcd()
ax.axhline(linewidth = 1.6, color = 'k')
ax.axvline(linewidth = 1.6, color = 'k')
ax.grid(True, linewidth = 0.4)
ax.legend(loc = 'best', fancybox = True, shadow = True)
# ax.set_title('example')
ax.set_xlabel('frequency of miracles')
# ax.set_xlim(-6 * np.pi, 6 * np.pi)
# ax.set_xticklabels([r'$\mu-4\sigma$', r'$\mu-3\sigma$', r'$\mu-2\sigma$', r'$\mu-\sigma$', r'$\mu$', r'$\mu+\sigma$', r'$\mu+2\sigma$', r'$\mu+3\sigma$', r'$\mu+4\sigma$'])
ax.set_xticks([4, 6])
ax.set_xticklabels(['invention of\nthe camera', 'invention of image\nediting software'])
# ax.set_xticks([i for i in np.arange(-4, 5, 1)])
# ax.set_xticklabels([r'${}$'.format(i) for i in np.arange(-4, 5, 1)])
# ax.set_xticklabels([r'${}\pi$'.format(i) for i in range(-6, -1)] + [r'$-\pi$', r'$0$', r'$\pi$'] + [r'${}\pi$'.format(i) for i in range(2, 7)])
# ax.set_xticks([i * np.pi for i in range(-6, 7)])
ax.set_ylabel('time')
# ax.set_ylim(-2, 8)
# ax.set_yticklabels([r'$\dfrac{0.3989}{\sigma}$', r'$\dfrac{0.2420}{\sigma}$', r'$\dfrac{0.0540}{\sigma}$', r'$\dfrac{0.0044}{\sigma}$'])
# ax.set_yticks(np.array([0.3989, 0.2420, 0.0540, 0.0044]) / t)
ax.set_yticks([])
# ax.set_yticklabels([r'${}$'.format(i) for i in ax.get_yticklabels()])
# ax.set_yticks([i for i in np.arange(-0.2, 1.3, 0.2)])
# ax.set_yticklabels([r'${}$'.format(round(i, 2)) for i in np.arange(-0.2, 1.3, 0.2)])
# fig.gca().set_aspect('equal', adjustable = 'box')
pp.show()
