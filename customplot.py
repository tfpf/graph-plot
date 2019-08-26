#!/usr/bin/env python3

import doctest
import fractions
import matplotlib
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d
import numpy as np
import sys
import time

###############################################################################

def show_nice_list(items, columns = 3):
	'''\
Display a list in neat centred columns.

Args:
	items: list, containing objects with an '__str__' method defined
	columns: int, number of columns to arrange 'items' in

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
	# width of a column is width of longest string in that column
	widths = [max([len(str(row[i])) for row in items])
	                                for i in range(columns)]

	# use the above-calculated widths to centre each column
	for row in items:
		for r, width in zip(row, widths):
			sys.stdout.write(str(r).center(width + 2, ' '))
			sys.stdout.flush()
		print()

###############################################################################

def sanitise_discontinuous(y):
	'''\
At a point of jump discontinuity, a vertical line is drawn automatically. This
vertical line joins the two points around the point of discontinuity.
Traditionally, in maths, these vertical lines are not drawn. Hence, they need
to be removed from the plot.

Args:
	y: np.array, array of values of the discontinuous function

Returns:
	None
'''

	# if the argument is a list, the following code may not work
	# hence, convert it to an array first
	y = np.array(y)

	# differentiate it to get an array which is shorter than 'y' by 1
	# prepend a zero to its front; now the length is same as that of 'y'
	# 'y' is assumed discontinuous at points where the derivative is large
	points_of_discontinuity = np.abs(np.concatenate([[0],
	                                                 np.diff(y)])) > 0.5

	# at the above points, change the value to NaN
	# this removes the vertical lines because those points won't be plotted
	y[points_of_discontinuity] = np.nan

	return y

###############################################################################

def graph_ticks(first, last, step):
	r'''
Create a list of tick values and labels at intervals of 'step * np.pi'.	I think
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
rational multiple of pi to another, and the 'np.array' of corresponding values.
Thus, a two-element tuple should be returned. (Note that LaTeX uses a backslash
to indicate keywords! Remember to either escape the backslash or simply use raw
strings. That latter approach has been used in this script because it simpler.)

Args:
	first: float, first grid line (grid lines start at 'first * np.pi')
	last: float, last grid line (grid lines end at 'last * np.pi')
	step: float, grid gap (distance between consecutive grid lines is
		'step * np.pi')

Returns:
	tuple, containing list of labels and an array of values indicated by
		the labels
'''

	# create an array containing the desired coefficients of pi
	# notice the 'last + step'
	# it is written that way because I don't want 'last' to be excluded
	# of course, this needs to be multiplied by pi before it is returned
	lattice = np.arange(first, last + step, step)

	# create a new list to store the label strings
	labels = []

	# represent each number in 'lattice' as a LaTeX-formatted string
	for number in lattice:

		# obtain the numerator and denominator
		value = fractions.Fraction(number).limit_denominator()
		num = value.numerator
		den = value.denominator

		# get the zero out of the way first
		if num == 0:
			labels.append(r'$0$')
			continue

		# build a string which has to be appended to 'label'
		# Python does not have a string builder data type
		# so, create a list to store the different parts of the string
		# then join those parts
		# this is the fastest way to build a string
		# https://waymoot.org/home/python_string/
		builder = ['$']

		# for negative tick values, write a minus sign right away
		if num < 0:
			builder.append('-')
			num = -num # now I don't have to worry about the sign

		# use '\frac{}{}' of LaTeX if denominator is not 1
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

###############################################################################

class CustomPlot:
	'''\
A class to easily plot two- and three-dimensional curves.

Args:
	dim: str, dimension of the plot ('2d' or '3d')
	aspect_ratio: float, ratio of scales on axes

Attributes:
	dim: str, dimension of the plot (either '2d' or '3d')
	aspect_ratio: float, ratio of scales on axes
	fig: matplotlib.figure.Figure, in which the graph will be plotted
	ax: matplotlib.axes._subplots.AxesSubplot (for '2d' graph) or
		matplotlib.axes._subplots.Axes3DSubplot (for '3d' graph), axes
		for the graph plot

Methods:
	__init__: set up a window to plot the graph
	__repr__: define representation of object
	__str__: define string form of object
	plot: check whether the plot is '2d' or '3d', then pass all arguments
		to the actual plotting function, i.e. 'ax.plot'
	configure: spice up the plot to make it more complete
	axis_fix: modify the ticks and labels on the axes so they look nice
	text: place a text string on the graph (just like 'plot', the arguments
		are simply passed to the actual text-placing function, i.e.
		'ax.text')
'''

	########################################

	def __init__(self, dim = '2d', aspect_ratio = 0):
		'''\
Assign essential class attributes.

Args:
	dim: str, dimension of the plot (either '2d' or '3d')
	aspect_ratio: float, ratio of scales on axes

Returns:
	None
'''

		# check the 'dim' argument and set the plot style
		# 'classic' style renders LaTeX strings in Computer Modern
		# Computer Modern is a great font for maths equations
		# 'seaborn-poster' style increases the font size
		# use both for two-dimensional plots
		# use only 'classic' for three-dimensional plot
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

		# figure containing the plot
		self.fig = plt.figure()

		# create an object for the axes
		if dim == '2d':
			self.ax = self.fig.add_subplot(1, 1, 1)
		else:
			self.ax = self.fig.add_subplot(1, 1, 1,
			                               projection = dim)

		# each run, the title of the window should be unique
		# use Unix time in the title
		self.fig.canvas.set_window_title(f'graph_{int(time.time())}')

	########################################

	def __repr__(self):
		'''\
Representation of the class object.

Args:
	no arguments

Returns:
	str, the representation of the object
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
	str, the string form of the object
'''

		return (f'CustomPlot(dim = \'{self.dim}\', '
		        f'aspect_ratio = {self.aspect_ratio})')

	########################################

	def plot(self, *args, **kwargs):
		'''\
Plot a curve. These arguments get passed as they are to the function which
actually plots. In case of a '2d' plot, the third item in 'args' is ignored.

Args:
	args: tuple of 3 np.array objects, corresponding to three coordinate
		axes
	kwargs: dict, remaining arguments meant for plotting

Returns:
	None
'''

		# 'args' contains 'x', 'y' and 'z'
		# remove vertical line around points of discontinuity
		# do this only to functions (i.e. if it contains many points)
		# if 'args' contains only 1 or 2 points, do nothing
		# use 10000 as the length threshold to allow margin for error
		sanitised_args = tuple(sanitise_discontinuous(arg)
		                       if len(arg) > 10000 else arg
		                       for arg in args)

		# 'kwargs' contains style information and the label
		# pass it without any changes
		# if this is a '2d' plot, ignore the 'z' argument in 'args'
		if self.dim == '2d':
			self.ax.plot(*sanitised_args[: -1], **kwargs)
		else:
			self.ax.plot(*sanitised_args, **kwargs)

	########################################

	def text(self, *args, **kwargs):
		'''\
Show text on the graph. The arguments are simply passed to the actual 'text'
method. This is meant to be used after the above 'plot' method has been used to
plot a single point.

Args:
	args: tuple of 3 single-item (float) lists (coordinates of the text),
		1 string (text string)
	kwargs: dict, remaining arguments meant for placing text

Returns:
	None
'''

		# same as in 'plot' method
		# third argument ignored for '2d' plot
		if self.dim == '2d':
			self.ax.text(*args[: -1], **kwargs)
		else:
			self.ax.text(*args, **kwargs)

	########################################

	def fill_between(self, *args, **kwargs):
		'''\
Fill an area with a colour. Can be used to show regions on the graph. Arguments
are directly passed to the actual 'fill_between' method. Obviously, this makes
sense only for '2d' plots.

Args:
	args: tuple of 3 np.array objects (indicating the 2 curves to fill
		between)
	kwargs: dict, remaining arguments meant for filling
'''

		if self.dim == '2d':
			self.ax.fill_between(*args, **kwargs)

	########################################

	def fill_betweenx(self, *args, **kwargs):
		'''\
Fill a vertical region with a colour. Mostly the same as 'fill_between'.

Args:
	args: tuple of 3 np.array objects (indicating the 2 curves to fill
		between)
	kwargs: dict, remaining arguments meant for filling
'''

		if self.dim == '2d':
			self.ax.fill_betweenx(*args, **kwargs)

	########################################

	def configure(self, axis_labels = (r'$x$', r'$y$', r'$z$'),
	                    title       = None):
		'''\
Spice up the graph plot. Add a legend, axis labels and grid lines.

Args:
	axis_labels: tuple of 3 strings (which are the labels for the three
		axes)
	title: str, title of the graph

Returns:
	None
'''

		# whether the scale should be the same on the coordinate axes
		# currently, because of a library bug, this works only in '2d'
		if self.aspect_ratio and self.dim == '2d':
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
		if self.dim == '2d':
			self.ax.axhline(linewidth = 1.2, color = 'k')
			self.ax.axvline(linewidth = 1.2, color = 'k')

		# enable grid
		self.ax.grid(b = True, which = 'major', linewidth = 0.8)
		if self.dim == '2d': # takes too much memory in '3d'
			self.ax.grid(b         = True,
			             which     = 'minor',
			             linewidth = 0.2)
			self.ax.minorticks_on()

	########################################

	def axis_fix(self, axis          = None,
	                   trigonometric = False,
	                   first         = None,
	                   last          = None,
	                   step          = None):
		'''\
Modify the labels and ticks on one of the axes of coordinates.

Args:
	axis: str, which axis to modify ('x', 'y' or 'z')
	trigonometric: bool, whether axis ticks are at rational multiples of pi
	first: float, grid start point
	last: float, grid end point
	step: float, grid gap

Returns:
	None
'''

		# decide which axis is to be modified
		# this method may be called for each axis
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
			return

		# placing vertical grid lines at rational multiples of pi
		if trigonometric:

			# this case requires all three following arguments
			if first is None or last is None or step is None:
				raise ValueError('Argument \'trigonometric\' '
				                 'has been set to True. '
				                 'Arguments \'first\', '
				                 '\'last\' and \'step\' must '
				                 'not be None.')

			# obtain lists of ticks and labels to set up grid lines
			# there may be an extra tick beyond 'last * np.pi'
			# this may happen because of floating-point precision
			# to remove this, set limits only after setting ticks
			labels, ticks = graph_ticks(first, last, step)
			ticks_set_function(ticks)
			labels_set_function(labels)
			limits_set_function(np.pi * first, np.pi * last)

		# placing grid lines normally
		else:

			# this is the non-trigonometric case
			# 'first' and 'last' need not be given
			# if not given, they are taken from 'np.linspace' below
			if first and last and step:
				ticks_set_function(np.arange(first,
				                             last + step,
				                             step))

			# again, limits must be set after setting the ticks
			if first and last:
				limits_set_function(first, last)

			# draw the graph with the ticks obtained above
			# ensures meaningful output of 'labels_get_function'
			self.fig.canvas.draw()

			# change the ticks font to Computer Modern
			# (requires using the 'classic' plot style)
			# the tick labels will become fixed non-numeric strings
			# thus, ticks will not be redrawn when you zoom or pan
			# this should not be an issue
			# minute analysis is not the purpose of this script
			labels_set_function([fr'${t.get_text()}$'
			                     for t in labels_get_function()])

###############################################################################

def main():
	'''\
Instantiate the 'CustomPlot' class. Call its 'plot', 'configure' and 'axis_fix'
methods (at the very least), and obtain an eye-candy graph.

Args:
	no arguments

Returns:
	None
'''

	# read command line argument
	# check whether this should be a two- or three-dimensional plot
	if len(sys.argv) < 2:
		dimension = '2d'
	else:
		dimension = sys.argv[1]
	grapher = CustomPlot(dim = dimension, aspect_ratio = 1)

	########################################

	# grapher.text(-0.6, -0.2, 1, s = r'$\left(0,0\right)$')
	# grapher.plot([0], [0], [1],
	#              color      = 'black',
	#              marker     = '.',
	#              markersize = 10)
	# grapher.text(3.15, -2.9, 1, s = r'$\left(3,-3\right)$')
	# grapher.plot([3], [-3], [1],
	#              color      = 'black',
	#              marker     = '.',
	#              markersize = 10)
	# grapher.text(-1, 4.1, 1, s = r'$\left(0,y\right)$')
	# grapher.plot([0], [4], [1],
	#              color      = 'black',
	#              marker     = '.',
	#              markersize = 10)

	########################################

	t = np.linspace(-5 * np.pi, 5 * np.pi, 100000)
	x1 = np.linspace(-32, 32, 100000)
	y1 = np.tan(x1)
	z1 = np.tan(x1)
	grapher.plot(x1, y1, z1, color     = 'red',
	                         linestyle = '-',
	                         linewidth = 0.8,
	                         label     = r'$y=\tan\,x$')
	# x2 = np.linspace(-32, 32, 100000)
	# y2 = 1 - np.abs(x2)
	# z2 = np.sin(x1)
	# grapher.plot(x2, y2, z2, color     = 'blue',
	#                          linestyle = '-',
	#                          linewidth = 0.8,
	#                          label     = r'$y=1-|x|$')
	# y3 = np.linspace(-32, 32, 100000)
	# x3 = -np.ones(100000)
	# z3 = np.sin(x3)
	# grapher.plot(x3, y3, z3, color     = 'green',
	#                          linestyle = '-',
	#                          linewidth = 0.8,
	#                          label     = r'$x=-1$')

	# grapher.fill_between(x1, y1, 0, facecolor = 'cyan',
	#                                 linewidth = 0,
	#                                 label     = r'$R$',
	#                                 where = [True if -1 < i < 1 else False
	#                                          for i in x1])

	grapher.configure(axis_labels = (r'$x$', r'$y$', r'$z$'), title = None)
	grapher.axis_fix(axis          = 'x',
	                 trigonometric = True,
	                 first         = -2,
	                 last          = 3,
	                 step          = 1 / 4)
	grapher.axis_fix(axis          = 'y',
	                 trigonometric = False,
	                 first         = -4,
	                 last          = 4,
	                 step          = 1)
	grapher.axis_fix(axis          = 'z',
	                 trigonometric = False,
	                 first         = None,
	                 last          = None,
	                 step          = None)
	plt.show()

###############################################################################

if __name__ == '__main__':
	doctest.testmod()
	main()
