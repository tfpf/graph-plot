#!/usr/bin/env python3

import colorama
import fractions
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys
import time
	
################################################################################

def show_nice_list(items, columns = 3):
	'''
	Display a list in neat columns.

	Args:
		items: list of objects
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
		for r, w in zip(row, widths):
			print(str(r).center(w + 2, ' '), end = '', flush = True)
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
		# to do this, create a list of the different pieces of the string
		# then join them
		# this is the fastest way to build a string
		# https://waymoot.org/home/python_string/
		builder = ['$']
		
		# for negative tick values, write a minus sign outside the fraction
		if num < 0:
			builder.append('-')
			num = -num # now I don't have to worry about the sign
		
		# '\frac{}{}' construct of LaTeX has to be used if denominator is not 1
		if den != 1:
			builder.append(r'\frac{')
		
		# if the coefficient is 1, it is not conventionally written
		if num == 1:
			builder.append(r'\pi')
		else:
			builder.append(fr'{num}\pi')
		
		# complete the '\frac{}{}' construct (if applicable)
		if den != 1:
			builder.append(fr'}}{{{den}}}$')
		else:
			builder.append('$')
		
		# now all pieces of the string are in place
		# create the LaTeX-formatted string by joining the pieces
		# append thusly created string to the list of labels
		labels.append(''.join(builder))
		
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

	ax.plot(1 / np.e, np.exp(-1 / np.e), 'r.'); ax.text(1 / np.e - 0.2, np.exp(-1 / np.e) + 0.15, r'$\left(e^{-1},e^{-\frac{1}{e}}\right)$')
	ax.plot(np.exp(-1 / np.e), 1 / np.e, 'k.'); ax.text(np.exp(-1 / np.e) + 0.1, 1 / np.e - 0.1, r'$\left(e^{-\frac{1}{e}},e^{-1}\right)$')

################################################################################

def configure(fig,
              ax,
              keep_aspect_ratio = False,
              xtrigonometric = False,
              x1 = None,
              x2 = None,
              xstep = None,
              ytrigonometric = False,
              y1 = None,
              y2 = None,
              ystep = None):
	'''
	Some miscellaneous settings to make the plot beautiful.
	By default, the 'classic' and 'seaborn-poster' plot styles are used.
	'seaborn-poster' increases the font size, making everything readable.
	'classic' causes a beautiful serif font to be used (but only if a string is written as a LaTeX string).
	That is why the 'xticklabels' and 'yticklabels' have been set using r'${}$'.
	This leads to a problem. On zooming or panning, the ticks will not modify to suit the new zoom level.
	This is okay, because this script is meant for publication-quality graphing, not for analysis.
	If the 'xtrigonometric' argument is 'True', vertical grid lines will be drawn from 'np.pi * x1' to 'np.pi * x2'.
	Distance between consecutive grid lines will be 'np.pi * xstep'.
	Else, they will be drawn from 'x1' to 'x2' at steps of 'xstep'.
	Ditto for 'ytrigonometric', 'y1', 'y2' and 'ystep'.
	Important! 'ax.set_*lim' must be called only after calling 'ax.set_*ticks'.
	Else, one extra tick may appear because of floating-point representation.
	For instance, the result of
		np.arange(-2, 2 + 1 / 3, 1 / 3)
	includes the rightmost point, 2.33, in the output!
		

	Args:
		fig: the figure which contains the graph plot
		ax: Axes object
		keep_aspect_ratio: boolean, whether both axes are to have an identical scale
		xtrigonometric: boolean, whether the horizontal axis should be marked at multiples of pi
		x1: leftmost x-coordinate to be shown
		x2: rightmost x-coordinate to be shown
		xstep: gap between vertical grid lines
		ytrigonometric: boolean, whether the vertical axis should be marked at multiples of pi
		y1: bottommost y-coordinate to be shown
		y2: topmost y-coordinate to be shown
		ystep: gap between horizontal grid lines

	Returns:
		None
	'''
	
	# same scale along both coordinate axes
	if keep_aspect_ratio:
		fig.gca().set_aspect('equal', adjustable = 'box')
	
	# graph description
	ax.legend(loc = 'best', fancybox = True, shadow = True, numpoints = 1)
	# ax.set_title('Example', **font_spec)
	
	# label the axes
	ax.set_xlabel(r'$x$')
	ax.set_ylabel(r'$y$', rotation = 90)
	
	# enable grid
	ax.axhline(linewidth = 1.6, color = 'k')
	ax.axvline(linewidth = 1.6, color = 'k')
	ax.grid(True, linewidth = 0.4)
	
	# placing vertical grid lines at rational multiples of pi
	if xtrigonometric:
		if x1 is None or x2 is None or xstep is None:
			raise ValueError('xtrigonometric has been set to True. x1, x2 and xstep must not be None.')
		
		# obtain lists of ticks and labels to set up vertical grid lines
		# markings on the horizontal axis correspond to vertical grid lines
		horizontal_labels, horizontal_ticks = graph_ticks(x1, x2, xstep)
		ax.set_xticklabels(horizontal_labels)
		ax.set_xticks(horizontal_ticks)
		ax.set_xlim(np.pi * x1, np.pi * x2)
		
	# placing vertical grid lines normally
	else:
		
		# this is the non-trigonometric case
		# if you don't provide x1 and x2, they will be chosen automatically
		if x1 and x2 and xstep:
			ax.set_xticks(np.arange(x1, x2 + xstep, xstep))
		if x1 and x2:
			ax.set_xlim(x1, x2)
		
		# draw the graph with the xticks obtained above
		# if xticks were not obtained above, they will have been chosen automatically
		fig.canvas.draw()
		
		# this line changes the font used for the ticks to a math mode font
		ax.set_xticklabels([fr'${t.get_text()}$' for t in ax.get_xticklabels()])
	
	# placing horizontal grid lines at rational multiples of pi
	if ytrigonometric:
		if y1 is None or y2 is None or ystep is None:
			raise ValueError('ytrigonometric has been set to True. y1, y2 and ystep must not be None.')
			
		# obtain lists of ticks and labels to set up horizontal grid lines
		# markings on the vertical axis correspond to horizontal grid lines
		vertical_labels, vertical_ticks = graph_ticks(y1, y2, ystep)
		ax.set_yticklabels(vertical_labels)
		ax.set_yticks(vertical_ticks)
		ax.set_ylim(np.pi * y1, np.pi * y2)
	
	# placing horizontal grid lines normally
	else:
	
		# this is the non-trigonometric case
		# if you don't provide y1 and y2, they will be chosen automatically
		if y1 and y2 and ystep:
			ax.set_yticks(np.arange(y1, y2 + ystep, ystep))
		if y1 and y2:
			ax.set_ylim(y1, y2)
		
		# draw the graph with the yticks obtained above
		# if yticks were not obtained above, they will have been chosen automatically
		fig.canvas.draw()
		
		# this line changes the font used for the ticks to a math mode font
		ax.set_yticklabels([fr'${t.get_text()}$' for t in ax.get_yticklabels()])

################################################################################

def remove_vertical_lines_at_discontinuities(y):
	'''
	At a point of jump discontinuity, a vertical lines is drawn.
	This vertical lines joins the two points around the point of discontinuity.
	Traditionally, in maths, these vertical lines are not drawn.
	Hence, they need to be removed.
	'''
	
	# if the difference between two consecutive points is large, the function is discontinuous there
	# differentiating 'y' gives an array whose length is less than the length of 'y' by 1
	# hence, I concatenate a zero to the front of derivative array
	# points where its elements are large are the points where 'y' is discontinuous
	points_of_discontinuity = np.concatenate([[0], np.diff(y)]) > 0.5
	
	# at the above points, change the value to 'np.nan'
	# this removes the vertical line
	y[points_of_discontinuity] = np.nan

################################################################################

if __name__ == '__main__':

	# choose a font
	colorama.init(autoreset = True)
	print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}Available fonts can be found in the following directory.')
	print(matplotlib.get_cachedir())
	font_spec = {'fontname' : 'DejaVu Serif'}
	print()
	
	# choose a plot style
	try:
		plt.style.use(sys.argv[1])
		print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}Here is a list of all available plot styles.')
	except (IndexError, OSError):
		print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}Plot style either not specified or invalid. Using \'classic\' and \'seaborn-poster\'.\nHere is a list of the available styles.')
		colorama.deinit()
		plt.style.use('classic')
		plt.style.use('seaborn-poster')
	show_nice_list(plt.style.available)
	print()

	# set up a window to display the graph
	# window title number is Unix time
	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	fig.canvas.set_window_title(f'graph_{int(time.time())}')

	########################################

	# t = np.concatenate([np.linspace(-20, -1, 100000), np.linspace(-1, 0, 100000), np.linspace(0, 20, 100000)])
	x1 = np.linspace(-16, 100, 100000)
	y1 = np.tan(x1); remove_vertical_lines_at_discontinuities(y1)
	ax.plot(x1, y1, 'r-', label = r'$y=\tan\,x$', linewidth = 0.8)
	# x2 = np.linspace(-16, 16, 100000)
	# y2 = np.exp(-x1 * np.log(x1))
	# ax.plot(x2, y2, 'b-', label = r'$y=\sin^2x$', linewidth = 0.8)
	# x3 = np.linspace(1 / np.e, 16, 100000)
	# y3 = x3 ** x3
	# ax.plot(y3, x3, 'g-', label = r'$y=e^{W_0(\ln\,x)}$', linewidth = 0.8)
	# x4 = np.array([2.773, 2.773])
	# y4 = [-100, 100]
	# ax.plot(x4, y4, 'g-', label = r'', linewidth = 0.8)
	# x5 = np.array([6.439, 6.439])
	# y5 = [-100, 100]
	# ax.plot(x5, y5, 'g-', label = r'', linewidth = 0.8)
	# x6 = np.array([9.317, 9.317])
	# y6 = [-100, 100]
	# ax.plot(x6, y6, 'g-', label = r'', linewidth = 0.8)
	# mark_points(ax)
	configure(fig,
	          ax,
	          keep_aspect_ratio = True,
	          xtrigonometric = True,
	          x1 = -1,
	          x2 = 4,
	          xstep = 0.5,
	          ytrigonometric = False,
	          y1 = -4,
	          y2 = 4,
	          ystep = 1)

	plt.show()
