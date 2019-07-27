#!/usr/bin/env python3

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

def remove_vertical_lines_at_discontinuities(y):
	'''
	At a point of jump discontinuity, a vertical lines is drawn.
	This vertical lines joins the two points around the point of discontinuity.
	Traditionally, in maths, these vertical lines are not drawn.
	Hence, they need to be removed from the plot.

	Args:
		y: NumPy array
	
	Returns:
		None
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

def mark_points(ax):
	'''
	Add markers to show points of interest.

	Args:
		ax: Axes object

	Returns:
		None
	'''

	ax.plot(-0.85, 0.39, 'k.'); ax.text(-0.85, 1.39, r'$\left(-0.85,0.39\right)$')
	ax.plot(0, 1, 'k.'); ax.text(0.05, 1.8, r'$\left(0,1\right)$')
	ax.plot(2, 9, 'k.'); ax.text(1.95, 7.5, r'$\left(2,9\right)$')
	ax.plot(3.22, 34.41, 'k.'); ax.text(3.22, 32.41, r'$\left(3.22,34.41\right)$')

################################################################################

def configure(fig, ax, keep_aspect_ratio = False):
	'''
	Spice up the plot.

	Args:
		fig: figure which contains the graph plot
		ax: Axes object
		keep_aspect_ratio: boolean, whether both axes are to have an identical scale

	Returns:
		None
	'''
	
	# same scale along both coordinate axes
	if keep_aspect_ratio:
		fig.gca().set_aspect('equal', adjustable = 'box')
	
	# graph description
	# without the 'numpoints' argument, two points are shown in the legend for 'ax.stem', etc.
	ax.legend(loc = 'best', fancybox = True, shadow = True, numpoints = 1)
	# ax.set_title('Example', **font_spec)
	
	# label the axes
	ax.set_xlabel(r'$x$')
	ax.set_ylabel(r'$y$', rotation = 90)
	
	# enable grid
	ax.axhline(linewidth = 1.6, color = 'k')
	ax.axvline(linewidth = 1.6, color = 'k')
	ax.grid(True, linewidth = 0.4)

################################################################################

def graph_ticks(first, last, step):
	'''
	Create a list of tick values and labels at intervals of 'step * np.pi'.
	I think it is best explained with examples.
		graph_ticks(-1, 5, 2) should create [r'$-\pi$', r'$\pi$', r'$3\pi$', r'$5\pi$']
		graph_ticks(-2, 2, 1) should create [r'$-2\pi$', r'$-\pi$', r'$0$', r'$\pi$', r'$2\pi$']
		graph_ticks(-1, -1 / 4, 1 / 4) should create [r'$-\pi$', r'$-\frac{3\pi}{4}$', r'$-\frac{\pi}{2}$', r'$-\frac{\pi}{4}$']
	Simply put, I want a list of LaTeX-formatted strings for numbers going from one rational multiple of pi to another.
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

def set_axis(fig, ax, axis          = 'x',
                      trigonometric = False,
                      first         = None,
                      last          = None,
                      step          = None):
	'''
	Some miscellaneous settings to make the plot look pretty.
	This function is supposed to be called twice: once to configure the x-axis, and once to configure the y-axis.
	If 'trigonometric' is True, ticks are drawn from 'first * np.pi' to 'last * np.pi' at steps of 'step * np.pi'.
	Else, they are drawn from 'first' to 'last' at steps of 'step'.
	Because of finite floating-point representation, an extra point may find its way into the list of ticks.	
		b + c in np.arange(a, b + c, c) == True
	Here, 'b + c' should not have been in the generated list, but the above can happen because of floating-point maths.
	This extra point 'b + c' is removed by simply not displaying it: by setting the limits on the axes from 'a' to 'b'.
	Hence, the limits must be set only after the ticks have been set.
	Take note of this happening in the non-trigonometric case below.

	Args:
		fig: figure which contains the graph plot
		ax: Axes object
		trigonometric: boolean, whether the axis should be ticked at multiples of pi
		first: grid start point
		last: grid end point
		step: grid gap

	Returns:
		None
	'''

	# use the 'axis' argument to decide which axis has to be set up
	if axis == 'x':
		limits_set_function = ax.set_xlim
		labels_get_function = ax.get_xticklabels
		labels_set_function = ax.set_xticklabels
		ticks_set_function = ax.set_xticks
	elif axis == 'y':
		limits_set_function = ax.set_ylim
		labels_get_function = ax.get_yticklabels
		labels_set_function = ax.set_yticklabels
		ticks_set_function = ax.set_yticks

	# placing vertical grid lines at rational multiples of pi
	if trigonometric:

		if first is None or last is None or step is None:
			raise ValueError('Argument \'trigonometric\' has been set to True--arguments \'first\', \'last\' and \'step\' must not be None.')
		
		# obtain lists of ticks and labels to set up grid lines
		labels, ticks = graph_ticks(first, last, step)
		ticks_set_function(ticks)
		labels_set_function(labels)
		limits_set_function(np.pi * first, np.pi * last)
		
	# placing grid lines normally
	else:
		
		# this is the non-trigonometric case
		# if you don't provide 'first' and 'last', they will be chosen automatically
		if first and last and step:
			ticks_set_function(np.arange(first, last + step, step))
		if first and last:
			limits_set_function(first, last) # removes extra point which may appear because of floating-point arithmetic
		
		# draw the graph with the ticks obtained above
		# if ticks were not obtained above, they will have been chosen automatically
		fig.canvas.draw()
		
		# this line changes the font used for the ticks to a math mode font
		# math mode font is a beatiful serif font if you use the 'classic' plot style
		# this line also fixes the ticks, so that the ticks will not be redrawn when you zoom or pan the graph
		# I assume that this is okay, because the purpose of this script is to plot a nice-looking graph
		# minute analysis is not the purpose here
		labels_set_function([fr'${t.get_text()}$' for t in labels_get_function()])

################################################################################

def main():

	# choose a font
	print('\033[1;31mAvailable fonts can be found in the following directory.\033[0m')
	print(matplotlib.get_cachedir())
	font_spec = {'fontname' : 'DejaVu Serif'}
	print()
	
	# choose a plot style
	try:
		plt.style.use(sys.argv[1])
		print('\033[1;31mHere is a list of all available plot styles.\033[0m')
	except (IndexError, OSError):
		print('\033[1;31mPlot style either not specified or invalid. Using \'classic\' and \'seaborn-poster\'.\nHere is a list of the available styles.\033[0m')
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
	x1 = np.linspace(-16, 16, 100000)
	y1 = np.cos(x1)
	ax.plot(x1, y1, 'r-', label = r'$y=\cos\,x$', linewidth = 0.8)
	# x2 = np.linspace(-16, 16, 100000)
	# y2 = 3 ** x2
	# ax.plot(x2, y2, 'b-', label = r'$y=3^x$', linewidth = 0.8)
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
	configure(fig, ax, keep_aspect_ratio = True)
	set_axis(fig, ax, axis          = 'x',
	                  trigonometric = True,
	                  first         = -2,
	                  last          = 2,
	                  step          = 0.25)
	set_axis(fig, ax, axis          = 'y',
	                  trigonometric = False,
	                  first         = -4,
	                  last          = 4,
	                  step          = 0.5)

	plt.show()

################################################################################

if __name__ == '__main__':
	main()
