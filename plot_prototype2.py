#!/usr/bin/env python3

import colorama
import fractions
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
	rows = len(items) // columns

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

def graph_ticks(first, last, step):
	'''
	Create a list of tick values and labels at intervals of 'step * np.pi'.
	I think it is best explained with examples.
		graph_ticks(-1, 5, 2) should create [r'$-\pi$', r'$\pi$', r'$3\pi$', r'$5\pi$']
		graph_ticks(-2, 2, 1) should create [r'$-2\pi$', r'$-\pi$', r'$0$', r'$\pi$', r'$2\pi$']
		graph_ticks(-1, -1 / 4, 1 / 4) should create [r'$-\pi$', r'$-\frac{3\pi}{4}$', r'$-\frac{\pi}{2}$', r'$-\frac{\pi}{4}$']
	Simply put, I want a list of LaTeX-formatted labels to describe the graph plot grid lines at some multiples of pi.
	Obviously, in addition to labels, a list of the values should also be created.
	I'll try to write the function as clearly as possible.
	
	Args:
		first: first grid line (grid lines should start at 'first * np.pi')
		last: last grid line (grid lines should end at 'last * np.pi')
		step: grid gap (distance between consecutive grid lines is 'step * np.pi')
	
	Returns:
		2-tuple containing list of labels and list of values indicated by the labels
	'''
	
	# list of coefficients of pi
	# notice the 'last + step'
	# it is written that way because I don't want 'last' to be excluded
	# multiplying this by 'np.pi' will give the ticks (i.e. locations of grid lines)
	lattice = np.arange(first, last + step, step)
	
	# create a new list to store the labels
	labels = []
	
	# represent each number in 'lattice' as a rational number
	for j in lattice:
		value = fractions.Fraction(j).limit_denominator()
		num = value.numerator
		den = value.denominator
		
		# get the zero out of the way first
		if num == 0:
			labels.append(r'$0$')
			continue
			
		# build a string which has to be appended to 'label'
		builder = r'$'
		
		# for negative tick values, write a minus sign outside the fraction
		if num < 0:
			builder += r'-'
			num = -num # now I don't have to worry about the sign
		
		# '\frac{}{}' construct of LaTeX has to be used if denominator is not 1
		if den != 1:
			builder += r'\frac{'
		
		# if the coefficient is 1, it is not conventionally written
		if num == 1:
			builder += r'\pi'
		else:
			builder += r'{}\pi'.format(num)
		
		# complete the '\frac{}{}' construct (if applicable)
		if den != 1:
			builder += r'}}{{{}}}$'.format(den)
		else:
			builder += r'$'
		
		labels.append(builder)
		
	return labels, np.pi * lattice

################################################################################

def mark_points(ax):
	'''
	Add markers to show points of interest.

	Args:
		ax: Axes object

	Returns:
		None
	'''

	ax.plot(1, 1, 'k.')
	ax.text(1.1, 1.1, r'$\left(1,1\right)$')

################################################################################

def configure(fig, ax):
	'''
	Some miscellaneous settings to make the plot beautiful.
	By default, the 'classic' and 'seaborn-poster' plot styles are used.
	'seaborn-poster' increases the font size, making everything readable.
	'classic' causes a beautiful serif font to be used (but only if a string is written as a LaTeX string).
	That is why the 'xticklabels' and 'yticklabels' have been set using r'${}$'.
	This leads to a problem. On zooming or panning, the ticks will not modify to suit the new zoom level.
	This is okay, because this script is meant for publication-quality graphing, not for analysis.
	If you want to, you can avoid this problem by commenting the 'xticklabels' and 'yticklabels' lines.

	Args:
		fig: the figure which contains the graph plot
		ax: Axes object

	Returns:
		None
	'''

	ax.axhline(linewidth = 1.6, color = 'k')
	ax.axvline(linewidth = 1.6, color = 'k')
	ax.grid(True, linewidth = 0.4)

	ax.legend(loc = 'best', fancybox = True, shadow = True, numpoints = 1)
	# ax.set_title('Example', **title_font)

	ax.set_xlim(-2 * np.pi, 2 * np.pi)
	ax.set_ylim(-3, 3)
	fig.canvas.draw() # automatically sets tick labels based on the last two lines
	
	# use the following lines if you want the automatically chosen tick labels
	ax.set_xticklabels([r'${}$'.format(t.get_text()) for t in ax.get_xticklabels()])
	ax.set_yticklabels([r'${}$'.format(t.get_text()) for t in ax.get_yticklabels()])

	# use the following lines if you want to customise tick labels
	# these will override the automatically chosen tick labels lines above
	labels, ticks = graph_ticks(-2, 2, 1 / 4); ax.set_xticklabels(labels); ax.set_xticks(ticks)
	
	# label the axes
	ax.set_xlabel(r'$x$')
	ax.set_ylabel(r'$y$', rotation = 90)

################################################################################

if __name__ == '__main__':

	# choose a font
	title_font = {'fontname' : 'DejaVu Serif'}
	colorama.init(autoreset = True)
	print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}Available fonts can be found in the following directory.')
	print(matplotlib.get_cachedir())
	print()
	
	# choose a plot style
	try:
		pp.style.use(sys.argv[1])
	except (IndexError, OSError):
		print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}Plot style either not specified or invalid. Using \'classic\' and \'seaborn-poster\'.\nHere is a list of the available styles.')
		colorama.deinit()
		pp.style.use('classic')
		pp.style.use('seaborn-poster')
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

	########################################

	x1 = np.linspace(-6 * np.pi, 6 * np.pi, 100000)
	y1 = np.cos(x1) / x1
	ax.plot(x1, y1, 'r-', label = r'$y=\dfrac{\cos\,x}{x}$', linewidth = 0.8)
	# x2 = np.linspace(-100, 100, 100000)
	# y2 = x2 - 2
	# ax.plot(x2, y2, 'b--', label = r'$y=x-2$', linewidth = 0.8)
	# x3 = np.linspace(0, 100, 100000)
	# y3 = 1 / x3
	# ax.plot(x3, y3, 'g-', label = r'$y=\dfrac{1}{x}$', linewidth = 0.8)
	# mark_points(ax)
	configure(fig, ax)

	pp.show()
