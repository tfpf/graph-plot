#!/usr/bin/env python3

import colorama
import matplotlib
import matplotlib.patches as mp
import matplotlib.pyplot as pp
import numpy as np
import sys

################################################################################

def show_nice_list(items, columns = 3):
	'''
	Display a list in neat columns.

	Args:
		items: list of strings
		columns: number of columns to arrange 'items' in

	Returns:
		None
	'''

	# pad the list with empty strings
	while len(items) % columns:
		items.append('')
	rows = int(len(items) / columns)

	# the number of elements in the list is now exactly 'rows * columns'
	# break the list row-wise so that it becomes a two-dimensional list
	items = [items[i :: rows] for i in range(rows)]

	# calculate the required width of all columns
	# width of a certain column is maximum of widths of strings in that column
	widths = [max([len(str(row[i])) for row in items]) for i in range(columns)]

	# use the above-calculated widths to centre each column
	for row in items:
		for r, width in zip(row, widths):
			sys.stdout.write(str(r).center(width + 2, ' '))
			sys.stdout.flush()
		print()

################################################################################

def annotate(ax):
	'''
	Add annotations and point markers to a graph plot.

	Args:
		ax: Axes object

	Returns:
		None
	'''

	ax.annotate(r'$\left(e,\dfrac{1}{e}\right)$', xy = (np.e, 1 / np.e), xytext = (np.e, 1 / np.e + 0.2))
	ax.plot([np.e], [1 / np.e], marker = '.', color = 'r')
	ax.annotate(r'$\left(-e,-\dfrac{1}{e}\right)$', xy = (-np.e, -1 / np.e), xytext = (-np.e - 0.3, -1 / np.e - 0.3))
	ax.plot([-np.e], [-1 / np.e], marker = '.', color = 'r')

################################################################################

def configure(fig, ax):
	'''
	Some miscellaneous settings to make the plot beautiful.
	By default, the 'classic' and 'seaborn-poster' plot styles are used.
	'seaborn-poster' increases the font size, making everything readable.
	'classic' causes a beautiful serif font to be used (but only if a string is written as a LaTeX string).
	That is why the 'xticklabels' and 'yticklabels' have been set using r'${}$'.
	The result is that on zooming or panning, the ticks will not modify to suit the new zoom level.
	This is okay, because this script is meant for publication-quality graphing, not for analysis.

	Args:
		fig: the figure which contains the graph plot
		ax: Axes object

	Returns:
		None
	'''

	ax.axhline(linewidth = 1.6, color = 'k')
	ax.axvline(linewidth = 1.6, color = 'k')
	ax.grid(True, linewidth = 0.4)

	ax.legend(loc = 'best', fancybox = True, shadow = True)
	ax.set_title('Example', **title_font)

	ax.set_xlim(-2 * np.pi, 6 * np.pi)
	ax.set_ylim(-4, 4)
	fig.canvas.draw()

	# use the following lines if you want to customise labels for ticks
	horz_labels = [r'${}\pi$'.format(i) for i in np.arange(-2, 7, 1)]
	horz_labels[1 : 4] = [r'$-\pi$', r'$0$', r'$\pi$']
	ax.set_xticklabels(horz_labels)
	ax.set_xticks([i * np.pi for i in np.arange(-2, 7, 1)])

	# use the following lines if you want tick labels to be chosen automatically
	# horz_labels = [item.get_text() for item in ax.get_xticklabels()]
	# ax.set_xticklabels([r'${}$'.format(i) for i in horz_labels])
	ax.set_yticklabels([r'${}$'.format(t.get_text()) for t in ax.get_yticklabels()])

	ax.set_xlabel(r'$x$')
	ax.set_ylabel(r'$y$', rotation = 90)

################################################################################

# choose a font
title_font = {'fontname' : 'DejaVu Serif'}
colorama.init(autoreset = True)
print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}List of available fonts can be found here.')
colorama.deinit()
print(matplotlib.get_cachedir())

# choose a plot style
try:
	pp.style.use(sys.argv[1])
except (IndexError, OSError):
	colorama.init(autoreset = True)
	print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}Plot style either not specified or invalid. Using \'classic\' and \'seaborn-poster\'.')
	colorama.deinit()
	pp.style.use('classic')
	pp.style.use('seaborn-poster')
print('available styles:')
show_nice_list(pp.style.available)

# set up a window to display the graph
# window title is a number obtained from 'counter.txt'
fig = pp.figure()
ax = fig.add_subplot(1, 1, 1)
with open('counter.txt') as count_file:
	graph_id = int(count_file.readline().strip())
fig.canvas.set_window_title('graph_{}'.format(graph_id))
with open('counter.txt', 'w') as count_file:
	print('{}'.format(graph_id + 1), file = count_file)
# fig.gca().set_aspect('equal', adjustable = 'box')

################################################################################

# t = np.linspace(-np.pi, np.pi, 100000)
x1 = np.linspace(-2 * np.pi, 6 * np.pi, 100000)
y1 = np.exp(-x1 / 4) * np.sin(2 * x1)
ax.plot(x1, y1, 'r-', label = r'$y=e^{-\frac{x}{4}}\,\sin\,2x$', linewidth = 0.8)
# x2 = np.linspace(-4 * np.pi, 4 * np.pi, 100000)
# y2 = 1 + np.cos(x2)
# ax.plot(x2, y2, 'b-', label = r'$y=1+\cos\,x$', linewidth = 0.8)
# x3 = np.linspace(0, np.sqrt(1 / 2), 100000)
# y3 = x3
# ax.plot(x3, y3, 'k-', label = r'', linewidth = 0.8)
# annotate(ax)
configure(fig, ax)

pp.show()
