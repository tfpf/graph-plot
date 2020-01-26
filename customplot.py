#!/usr/bin/env python3

import doctest
import fractions
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d
import numpy as np
import scipy.signal as sig
import sys
import time

###############################################################################

def show_nice_list(items, columns = 3):
	'''\
Display a list in neat centred columns.

Args:
	items: list (each of its contents must have `__str__` defined)
	columns: int (number of columns to arrange `items` in)

Returns:
	None
'''

	# convert the list of strings to list of list of strings
	while len(items) % columns:
		items.append('')
	rows = len(items) // columns
	items = [items[i :: rows] for i in range(rows)]

	# calculate the required width of all columns
	# width of a column is width of longest string in that column
	widths = [max([len(str(row[i])) for row in items])
	                                for i in range(columns)]
	for row in items:
		for r, width in zip(row, widths):
			sys.stdout.write(str(r).center(width + 2, ' '))
			sys.stdout.flush()
		print()

	return None

###############################################################################

def sanitise_discontinuous(y):
	'''\
At a point of jump discontinuity, a vertical line is drawn automatically. This
vertical line joins the two points around the point of discontinuity.
Traditionally, in maths, these vertical lines are not drawn. Hence, they need
to be removed from the plot. If the value is set to NaN at these points, they
will not be plotted.

Args:
	y: np.array or list (values of the discontinuous function)

Returns:
	np.array with NaN at the points of discontinuity
'''

	# locate points of discontinuity (check where the derivative is large)
	y = np.array(y)
	points_of_discontinuity = np.abs(np.concatenate([[0],
	                                                 np.diff(y)])) > 0.1
	y[points_of_discontinuity] = np.nan

	return y

###############################################################################

def graph_ticks(first, last, step):
	r'''
Create a list of tick values and labels at intervals of `step * np.pi`.	I think
it is best explained with examples. (To properly demonstrate the working, this
docstring is being marked as a raw string. Otherwise, the backslashes will be
interpreted as parts of escape sequences.)
>>> graph_ticks(-1, 5, 2)
(['$-\\pi$', '$\\pi$', '$3\\pi$', '$5\\pi$'], array([-3.14159265,  3.14159265,  9.42477796, 15.70796327]))
>>> graph_ticks(-1, -1 / 4, 1 / 4)
(['$-\\pi$', '$-\\frac{3\\pi}{4}$', '$-\\frac{\\pi}{2}$', '$-\\frac{\\pi}{4}$'], array([-3.14159265, -2.35619449, -1.57079633, -0.78539816]))
>>> graph_ticks(-2, 2, 1)
(['$-2\\pi$', '$-\\pi$', '$0$', '$\\pi$', '$2\\pi$'], array([-6.28318531, -3.14159265,  0.        ,  3.14159265,  6.28318531]))

What's required is a list of LaTeX-formatted strings for numbers going from one
rational multiple of pi to another, and the `np.array` of corresponding values.
Thus, a two-element tuple should be returned. (Note that LaTeX uses a backslash
to indicate keywords! Remember to either escape the backslash or simply use raw
strings. The latter approach was used just to keep all of those things simple.)
As a side effect of using LaTeX strings as labels instead of whatever is chosen
automatically, panning or zooming the graph does not update the grid lines like
it does otherwise.

Args:
	first: float (first grid line) (grid lines start at `first * np.pi`)
	last: float (last grid line) (grid lines end at `last * np.pi`)
	step: float (grid gap) (grid lines separated by `step * np.pi`)

Returns:
	tuple, containing list of labels and an array of values indicated by
		the labels
'''

	# create an array containing the desired coefficients of pi
	# notice the `last + step`
	# it is written that way because I don't want `last` to be excluded
	lattice = np.arange(first, last + step, step)

	# create a new list to store the label strings
	labels = []
	for number in lattice:
		value = fractions.Fraction(number).limit_denominator()
		num = value.numerator
		den = value.denominator

		# case 1: `value` is zero
		if num == 0:
			labels.append(r'$0$')
			continue

		# build a string which has to be appended to `label`
		# Python does not have a string builder data type
		# so, create a list to store the different parts of the string
		# then join those parts
		# this is the fastest way to build a string
		# https://waymoot.org/home/python_string/
		builder = ['$']

		# case 2: `value` is non-zero
		if num < 0:
			builder.append('-')
			num = -num
		if den != 1:
			builder.append(r'\frac{')
		if num == 1:
			builder.append(r'\pi')
		else:
			builder.append(fr'{num}\pi')
		if den != 1:
			builder.append(fr'}}{{{den}}}$')
		else:
			builder.append('$')
		labels.append(''.join(builder))

	return labels, np.pi * lattice

###############################################################################

class CustomPlot:
	'''\
A class to easily plot two- and three-dimensional graphs.

Attributes:
	dim: str (dimension of the plot, either '2d' or '3d')
	aspect_ratio: float (ratio of scales on axes)
	fig: matplotlib.figure.Figure (figure to contain the plot)
	ax: matplotlib.axes._subplots.AxesSubplot (if `dim` is '2d') or
		matplotlib.axes._subplots.Axes3DSubplot (if `dim` is '3d')
		(axes object for the graph plot)

Methods:
	__init__
	__repr__
	__str__
	plot: check the attribute `dim`, then pass arguments to the actual
		plotting function `ax.plot`
	configure: spice up the plot to make it more complete
	axis_fix: modify the ticks and labels on the axes so they look nice
'''

	########################################

	def __init__(self, dim = '2d', aspect_ratio = 0):
		'''\
Assign essential class attributes.

Args:
	dim: str (dimension of the plot, either '2d' or '3d')
	aspect_ratio: float (ratio of scales on axes)

Returns:
	None
'''

		# 'classic' style renders LaTeX strings in Computer Modern font
		# 'seaborn-poster' style increases the font size
		# use both for two-dimensional plots
		# use only 'classic' for three-dimensional plots
		# because adjacent text items overlap when font size increases
		if dim == '2d':
			plt.style.use(['classic', 'seaborn-poster'])
		elif dim == '3d':
			plt.style.use('classic')
		else:
			raise ValueError('Member \'dim\' of class '
			                 '\'CustomPlot\' must be either \'2d\''
			                 ' or \'3d\'.')
		self.dim = dim
		self.aspect_ratio = aspect_ratio
		self.fig = plt.figure()
		if dim == '2d':
			self.ax = self.fig.add_subplot(1, 1, 1)
		else:
			self.ax = self.fig.add_subplot(1, 1, 1,
			                               projection = dim)

		# each run, the title of the window should be unique
		# use Unix time in the title
		self.fig.canvas.set_window_title(f'graph_{int(time.time())}')

		return None

	########################################

	def __repr__(self):
		'''\
Representation of the class object.

Args:
	no arguments

Returns:
	str
'''

		return (f'CustomPlot(dim = \'{self.dim}\', '
		        f'aspect_ratio = {self.aspect_ratio})')

	########################################

	def __str__(self):
		'''\
String form of the class object.

Args:
	no arguments

Returns:
	str
'''

		return (f'CustomPlot(dim = \'{self.dim}\', '
		        f'aspect_ratio = {self.aspect_ratio})')

	########################################

	def plot(self, *args, **kwargs):
		'''\
Plot a curve. These arguments get passed as they are to the function which
actually plots. Before plotting, unwanted vertical lines at points of
discontinuity are removed.

Args:
	args: tuple of 2 or 3 objects (each of the said objects is one of the
		following: 1-item list, 2-item list, 100000-item NumPy
		array)
	kwargs: dict (remaining arguments meant for plotting)

Returns:
	None
'''

		# if the arguments are 100000-item NumPy arrays, sanitise them
		# otherwise, vertical lines (if any) are supposedly intentional
		if len(args[0]) > 1000:
			args = tuple(sanitise_discontinuous(arg)
			             for arg in args)
		self.ax.plot(*args, **kwargs)

		return None

	########################################

	def configure(self, axis_labels = (r'$x$', r'$y$', r'$z$'),
	                    title       = None):
		'''\
Spice up the graph plot. Add a legend, axis labels and grid lines.

Args:
	axis_labels: tuple of 3 strings (which are the labels for the three
		coordinate axes)
	title: str (title of the graph)

Returns:
	None
'''

		# whether the scale should be the same on the coordinate axes
		# currently, because of a library bug, this works only in '2d'
		if self.aspect_ratio != 0 and self.dim == '2d':
			self.ax.set_aspect(aspect     = self.aspect_ratio,
			                   adjustable = 'box')

		# set legend and axis labels
		self.ax.legend(loc       = 'upper right',
		               fancybox  = True,
		               shadow    = True,
		               numpoints = 1)
		self.ax.set_xlabel(axis_labels[0])
		self.ax.set_ylabel(axis_labels[1])
		if self.dim == '3d':
			self.ax.set_zlabel(axis_labels[2])
		if title is not None:
			self.ax.set_title(title)

		# if this is a '2d' plot, draw thick coordinate axes
		# this does not work as expected in '3d'
		if self.dim == '2d':
			self.ax.axhline(linewidth = 1.2, color = 'k')
			self.ax.axvline(linewidth = 1.2, color = 'k')

		# enable grid
		# minor grid takes too much memory in '3d' plot
		self.ax.grid(b = True, which = 'major', linewidth = 0.8)
		if self.dim == '2d':
			self.ax.grid(b         = True,
			             which     = 'minor',
			             linewidth = 0.2)
			self.ax.minorticks_on()

		return None

	########################################

	def axis_fix(self, axis          = None,
	                   trigonometric = False,
	                   first         = None,
	                   last          = None,
	                   step          = None):
		'''\
Modify the labels and ticks on the specified axis of coordinates. Note that the
limits on the axis must necessarily be set after setting the axis ticks. This
is because floating point precision issues might introduce an extra tick beyond
the last point (`last`) to be displayed. This extra tick is eliminate simply by
specifying in the axis limit that the axis must end at `last`.

Args:
	axis: str (which axis to modify: 'x', 'y' or 'z')
	trigonometric: bool (whether ticks are at rational multiples of pi)
	first: float (grid start point)
	last: float (grid end point)
	step: float (grid gap)

Returns:
	None
'''

		if axis == 'x':
			limits_set_function = self.ax.set_xlim
			labels_get_function = self.ax.get_xticklabels
			labels_set_function = self.ax.set_xticklabels
			ticks_set_function = self.ax.set_xticks
		elif axis == 'y':
			limits_set_function = self.ax.set_ylim
			labels_get_function = self.ax.get_yticklabels
			labels_set_function = self.ax.set_yticklabels
			ticks_set_function = self.ax.set_yticks
		elif axis == 'z' and self.dim == '3d':
			limits_set_function = self.ax.set_zlim
			labels_get_function = self.ax.get_zticklabels
			labels_set_function = self.ax.set_zticklabels
			ticks_set_function = self.ax.set_zticks
		else:
			return None

		# case 1: grid lines at pi times the arguments provided
		if trigonometric:
			if None in {first, last, step}:
				raise ValueError('Argument \'trigonometric\' '
				                 'has been set to True. '
				                 'Arguments \'first\', '
				                 '\'last\' and \'step\' must '
				                 'not be None.')
			labels, ticks = graph_ticks(first, last, step)
			ticks_set_function(ticks)
			labels_set_function(labels)
			limits_set_function(np.pi * first, np.pi * last)

		# case 2: grid lines at the values provided in the arguments
		else:
			if None not in {first, last, step}:
				ticks_set_function(np.arange(first,
				                             last + step,
				                             step))
			if None not in {first, last}:
				limits_set_function(first, last)
			self.fig.canvas.draw()
			labels_set_function([fr'${t.get_text()}$'
			                     for t in labels_get_function()])

		return None

###############################################################################

def main():
	'''\
Instantiate the `CustomPlot` class. Call its `plot`, `configure` and `axis_fix`
methods (at the very least), and obtain an eye-candy graph.

Args:
	no arguments

Returns:
	None
'''

	if len(sys.argv) < 2:
		dimension = '2d'
	else:
		dimension = sys.argv[1]
	grapher = CustomPlot(dim = dimension, aspect_ratio = 1)

	########################################

	t = np.linspace(-np.pi / 2, np.pi / 2, 100000)
	x1 = np.linspace(-32, 32, 1000000)
	y1 = np.sin(np.arccos(x1))
	z1 = np.sin(x1)
	grapher.plot(x1, y1, color     = 'red',
	                     linestyle = '-',
	                     linewidth = 0.8,
	                     label     = r'$y=\sin\,\cos^{-1}x$')
	# x2 = np.linspace(-32, 32, 100000)
	# y2 = np.sin(x2)
	# z2 = np.sin(x2)
	# grapher.plot(x2, y2, color     = 'blue',
	#                      linestyle = '-',
	#                      linewidth = 0.8,
	#                      label     = r'$y=\sin\,x$')
	# grapher.ax.plot(5, -10, 'k.')
	# grapher.ax.text(4, -10.8, r'$(5,-10)$')
	# x4 = np.linspace(0, 3, 100000)
	# y4 = -x4 + 3
	# z4 = np.sin(x4)
	# grapher.plot(x4, y4, color     = 'red',
	#                      linestyle = '-',
	#                      linewidth = 0.8,
	#                      label     = r'')
	# y3 = np.linspace(2, 2.5, 100)
	# t = np.linspace(-np.pi, np.pi, 100)
	# R, T = np.meshgrid(y3, t)
	# Y = R * np.cos(T)
	# X = np.arccos((R - np.sqrt(R ** 2 - 4)) / 2)
	# Z = R * np.sin(T)
	# grapher.ax.plot_surface(X, Y, Z, cmap = 'Reds')
	# r = np.linspace(0, 4, 200)
	# t = np.linspace(-np.pi, np.pi, 200)
	# R, T = np.meshgrid(r, t)
	# x5 = R * np.cos(T)
	# y5 = R * np.sin(T)
	# z5 = 9 - x5 ** 2 - y5 ** 2
	# x5 = np.linspace(-4, 4, 200)
	# y5 = np.linspace(-4, 4, 200)
	# x5, y5 = np.meshgrid(x5, y5)
	# z5 = 9 - x5 ** 2 - y5 ** 2
	# for i in range(200):
	# 	for j in range(200):
	# 		if z5[i, j] < 0:
	# 			z5[i, j] = 0
	# grapher.ax.plot_surface(x5, y5, z5, cmap = 'Reds')

	# grapher.ax.fill_between(x1, y1, y2,  facecolor = 'cyan',
	#                                      linewidth = 0,
	#                                      label = r'$S$',
	#                                      where     = [True
	#                                                   if 0 < 1 else False
	#                                                   for i in x1])
	# grapher.ax.fill_between(x1, [min(i, j) for i, j in zip(y4, y6)], -4,  facecolor = 'cyan',
	#                                      linewidth = 0,
	#                                      label     = r'',
	#                                      where     = [True
	#                                                   if -8 < i < 0 else False
	#                                                   for i in x1])
	# grapher.ax.fill_between(x2, y2, -4, facecolor = 'cyan',
	#                                     linewidth = 0)

	grapher.configure(axis_labels = (r'$x$', r'$y$', r'$z$'), title = None)
	grapher.axis_fix(axis          = 'x',
	                 trigonometric = False,
	                 first         = -2,
	                 last          = 2,
	                 step          = 0.25)
	grapher.axis_fix(axis          = 'y',
	                 trigonometric = False,
	                 first         = -1,
	                 last          = 2,
	                 step          = 0.25)
	grapher.axis_fix(axis          = 'z',
	                 trigonometric = False,
	                 first         = -10,
	                 last          = 10,
	                 step          = 2)
	plt.show()

	return None

###############################################################################

if __name__ == '__main__':
	doctest.testmod()
	main()

