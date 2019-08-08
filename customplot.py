#!/usr/bin/env python3

import fractions
import matplotlib
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as mp
import numpy as np
import sys
import time

################################################################################

def show_nice_list(items, columns = 3):
	'''\
Display a list in neat centred columns.

Args:
	items: list, containing items with a valid '__str__' method
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
	# width of a certain column is maximum of widths of strings in that column
	widths = [max([len(str(row[i])) for row in items]) for i in range(columns)]

	# use the above-calculated widths to centre each column
	for row in items:
		for r, width in zip(row, widths):
			sys.stdout.write(str(r).center(width + 2, ' '))
			sys.stdout.flush()
		print()

################################################################################

def remove_vertical_lines_at_discontinuities(y):
	'''\
At a point of jump discontinuity, a vertical line is drawn automatically. This
vertical line joins the two points around the point of discontinuity.
Traditionally, in maths, these vertical lines are not drawn. Hence, they need to
be removed from the plot.

Args:
	y: np.array, array of values of the discontinuous function

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

def graph_ticks(first, last, step):
	'''\
Create a list of tick values and labels at intervals of 'step * np.pi'.	I think
it is best explained with examples.
	graph_ticks(-1, 5, 2) == ['$-\\pi$', '$\\pi$', '$3\\pi$', '$5\\pi$']
	graph_ticks(-2, 2, 1) == ['$-2\\pi$', '$-\\pi$', '$0$', '$\\pi$', '$2\\pi$']
	graph_ticks(-1, -1 / 4, 1 / 4) == ['$-\\pi$', '$-\\frac{3\\pi}{4}$', '$-\\frac{\\pi}{2}$', '$-\\frac{\pi}{4}$']
Simply put, I want a list of LaTeX-formatted strings for numbers going from one
rational multiple of pi to another. Obviously, in addition to labels, a list of
the values should also be created. I'll try to write the function as clearly as
possible. (Note that LaTeX uses the backslash to indicate keywords! Remember to
either escape the backslash or simply use raw strings. I have done the latter.)
	
Args:
	first: float, first grid line (grid lines start at 'first * np.pi')
	last: float, last grid line (grid lines end at 'last * np.pi')
	step: float, grid gap (distance between consecutive grid lines is 'step * np.pi')
	
Returns:
	tuple, containing list of labels and list of values indicated by the labels
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

class CustomPlot:
	'''\
A class to easily plot two- and three-dimensional line graphs.

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
	plot: check whether the plot is '2d' or '3d', then pass all arguments to
		the actual plotting function
	configure: spice up the plot to make it more complete
	axis_fix: modify the ticks and labels on the axes so they look nice
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
		# I use 'classic' because it causes LaTeX-formatted strings to be rendered in Computer Modern
		# Computer Modern is prettier than the default font (at least on Linux)
		# for two-dimensional plots, I like to also use 'seaborn-poster', which increases the font size
		# in three-dimensional plots, this increased font size overlaps with surrounding text
		# hence, for three-dimensional plots, I use only 'classic'
		if dim == '2d':
			plt.style.use(['classic', 'seaborn-poster'])
		elif dim == '3d':
			plt.style.use('classic')
		else:
			raise ValueError('Member \'dim\' of class \'CustomPlot\' must be either \'2d\' or \'3d\'.')
		self.dim = dim
		self.aspect_ratio = aspect_ratio

		# figure containing the plot
		self.fig = plt.figure()

		# depending on the dimensionality, create an object for the axes
		if dim == '2d':
			self.ax = self.fig.add_subplot(1, 1, 1)
		else:
			self.ax = self.fig.add_subplot(1, 1, 1, projection = dim)
		
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

		return f'CustomPlot(dim = \'{self.dim}\', aspect_ratio = {self.aspect_ratio})'
	
	########################################

	def __str__(self):
		'''\
String form of the class object.

Args:
	no arguments

Returns:
	str, the string form of the object
'''

		return f'CustomPlot(dim = \'{self.dim}\', aspect_ratio = {self.aspect_ratio})'

	########################################

	def plot(self, *args, **kwargs):
		'''\
Plot a curve. These arguments get passed as they are to the function which
actually plots. In case of a '2d' plot, the third item in 'args' is ignored.

Args:
	args: tuple of 3 np.array objects, corresponding to three coordinate axes
	kwargs: dict, remaining arguments meant for plotting

Returns:
	None
'''

		# 'args' contains 'x', 'y' and 'z'
		# 'kwargs' contains style information and the label
		# if this is a '2d' plot, ignore the 'z' argument
		if self.dim == '2d':
			self.ax.plot(*args[: -1], **kwargs)
		else:
			self.ax.plot(*args, **kwargs)

	########################################

	def text(self, *args, **kwargs):
		'''\
Show text on the graph. The arguments are simply passed to the actual 'text'
method. This is meant to be used after the above 'plot' method has been used to
plot a single point.

Args:
	args: tuple of 3 floats (coordinates of the text), 1 string (text string)
	kwargs: dict, remaining arguments meant for placing text

Returns:
	None
'''

		# same as in 'plot' method
		# third coordinate ignored for '3d' plot
		if self.dim == '2d':
			self.ax.text(*args[: -1], **kwargs)
		else:
			self.ax.text(*args, **kwargs)

	########################################

	def configure(self):
		'''\
Spice up the graph plot.

Args:
	no arguments

Returns:
	None
'''

		# whether the scale should be the same on the coordinate axes
		# currently, because of a library bug, this works only in '2d'
		if self.aspect_ratio and self.dim == '2d':
			self.ax.set_aspect(aspect = self.aspect_ratio, adjustable = 'box')

		# set legend and axis labels
		self.ax.legend(loc = 'best', fancybox = True, shadow = True, numpoints = 1)
		self.ax.set_xlabel(r'$x$')
		self.ax.set_ylabel(r'$y$')
		if self.dim == '3d':
			self.ax.set_zlabel(r'$z$')

		# if this is a '2d' plot, draw thick coordinate axes
		if self.dim == '2d':
			self.ax.axhline(linewidth = 1.2, color = 'k')
			self.ax.axvline(linewidth = 1.2, color = 'k')

		# enable grid
		self.ax.grid(b = True, which = 'major', linewidth = 0.8)
		if self.dim == '2d': # takes too much memory in '3d'
			self.ax.grid(b = True, which = 'minor', linewidth = 0.2)
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

		# use the 'axis' argument to decide which axis is to be modified
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
		elif axis == 'z' and self.dim == '3d': # to modify 'z' axis, the plot must be '3d'
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
				raise ValueError('Argument \'trigonometric\' has been set to True--arguments \'first\', \'last\' and \'step\' must not be None.')

			# obtain lists of ticks and labels to set up grid lines
			labels, ticks = graph_ticks(first, last, step)
			ticks_set_function(ticks)
			labels_set_function(labels)
			limits_set_function(np.pi * first, np.pi * last) # removes extra point which may appear because of finite floating-point precision
			
		# placing grid lines normally
		else:
			
			# this is the non-trigonometric case
			# if you don't provide 'first' and 'last', they will be chosen automatically
			if first and last and step:
				ticks_set_function(np.arange(first, last + step, step))
			if first and last:
				limits_set_function(first, last) # removes extra point which may appear because of finite floating-point precision
			
			# draw the graph with the ticks obtained above
			# if ticks were not obtained above, they will have been chosen automatically
			# without this line, 'labels_get_function' will not return anything useful
			self.fig.canvas.draw()
			
			# this line changes the font used for the ticks to Computer Modern (if the 'classic' plot style is being used)
			# this line also changes the ticks from integers to strings
			# as a result, it fixes the ticks, so that the ticks will not be redrawn when you zoom or pan the graph
			# I assume that this is okay, because the purpose of this script is to plot a nice-looking graph
			# minute analysis is not the purpose here
			labels_set_function([fr'${t.get_text()}$' for t in labels_get_function()])

################################################################################

def main():

	# read command line argument
	# check whether this should be a two- or three-dimensional plot
	if len(sys.argv) < 2:
		dimension = '2d'
	else:
		dimension = sys.argv[1]

	# instantiate the class to take care of all the objects required
	grapher = CustomPlot(dim = dimension, aspect_ratio = 1)

	########################################

	x1 = np.linspace(-32, 32, 100000)
	y1 = 1 / np.sin(x1); remove_vertical_lines_at_discontinuities(y1)
	z1 = np.sin(x1)
	grapher.plot(x1, y1, z1, color = 'red', linestyle = '-', linewidth = 0.8, label = r'$y=\csc\,x$')

	x2 = np.linspace(-32, 32, 100000)
	y2 = x2
	z2 = np.sin(x1)
	grapher.plot(x2, y2, z2, color = 'blue', linestyle = '-', linewidth = 0.8, label = r'$y=x$')

	########################################

	grapher.plot([1], [1], [1], color = 'black', marker = '.', markersize = 10)
	grapher.text(0.7, 0.5, 1, s = r'$\left(1,1\right)$')

	########################################

	grapher.configure()
	grapher.axis_fix(axis          = 'x',
	                 trigonometric = True,
	                 first         = -4,
	                 last          = 4,
	                 step          = 1 / 2)
	grapher.axis_fix(axis          = 'y',
	                 trigonometric = False,
	                 first         = -8,
	                 last          = 8,
	                 step          = 1)
	grapher.axis_fix(axis          = 'z',
	                 trigonometric = False,
	                 first         = None,
	                 last          = None,
	                 step          = None)
	plt.show()

################################################################################

if __name__ == '__main__':
	main()
