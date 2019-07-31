#!/usr/bin/env python3

import argparse
import fractions
import matplotlib
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as mp
import numpy as np
import sys
import time

################################################################################

def show_nice_list(items, columns = 3):
	'''
Display a list in neat centred columns.

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

def remove_vertical_lines_at_discontinuities(y):
	'''
At a point of jump discontinuity, a vertical line is drawn automatically. This \
vertical line joins the two points around the point of discontinuity. \
Traditionally, in maths, these vertical lines are not drawn. Hence, they need \
to be removed from the plot.
to be removed from the 
to be removed from the Args:
to be removed from the 	y: NumPy array
to be removed from the 
to be removed from the Returns:
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
	'''
Create a list of tick values and labels at intervals of 'step * np.pi'.	I think\
 it is best explained with examples.
	graph_ticks(-1, 5, 2) == ['$-\\pi$', '$\\pi$', '$3\\pi$', '$5\\pi$']
	graph_ticks(-2, 2, 1) == ['$-2\\pi$', '$-\\pi$', '$0$', '$\\pi$', '$2\\pi$']
	graph_ticks(-1, -1 / 4, 1 / 4) == ['$-\\pi$', '$-\\frac{3\\pi}{4}$', '$-\\frac{\\pi}{2}$', '$-\\frac{\pi}{4}$']
Simply put, I want a list of LaTeX-formatted strings for numbers going from one\
 rational multiple of pi to another. Obviously, in addition to labels, a list \
of the values should also be created. I'll try to write the function as clearly\
 as possible. (Note that LaTeX uses the backslash to indicate keywords! \
Remember to either escape the backslash or simply use raw strings. I have done \
the latter.)
	
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

class CustomPlot:
	'''
A class to easily plot two- and three-dimensional line graphs.

Args:
	dim: str, dimension of the plot (either '2d' or '3d')
	keep_aspect_ratio: boolean, whether scales on the axes should be same

Attributes:
	dim: str, dimension of the plot (either '2d' or '3d')
	keep_aspect_ratio: bool, whether scales on the axes should be same
	fig: matplotlib.figure.Figure, in which the graph will be plotted
	ax: matplotlib.axes._subplots.AxesSubplot (for '2d' graph) or \
matplotlib.axes._subplots.AxesSubplot (for '3d' graph), axes for the graph plot

Methods:
	__init__: set up 'fig' to plot the graph
	plot: check whether the plot is '2d' or '3d', then pass all arguments \
to plt.plot
	configure: spice up the plot to make it more complete
	axis_fix: modify the ticks and labels on the axes so they look nice
'''
	
	def __init__(self, dim, keep_aspect_ratio = False):
		'''Assign member variables.'''

		self.dim = dim
		self.keep_aspect_ratio = keep_aspect_ratio
		self.fig = plt.figure()
		if dim == '2d':
			self.ax = self.fig.add_subplot(1, 1, 1)
		else:
			self.ax = self.fig.add_subplot(1, 1, 1, projection = dim)
		
		# each run, the title of the window should be unique
		# use Unix time in the title
		self.fig.canvas.set_window_title(f'graph_{int(time.time())}')
		
	########################################

	def plot(self, *args, **kwargs):
		'''Plot stuff.'''

		# if this is a two-dimensional plot, ignore the 'z' argument
		# 'args' contains 'x', 'y' and 'z'
		# kwargs contains style information and the label
		if self.dim == '2d':
			plt.plot(*args[: -1], **kwargs)
		else:
			plt.plot(*args, **kwargs)
	
	########################################

	def configure(self):
		'''Spice.'''

		# whether the scale should be the same on the coordinate axes
		if self.keep_aspect_ratio:
			fig.gca().set_aspect('equal', adjustable = 'box')

		self.ax.legend(loc = 'best', fancybox = True, shadow = True, numpoints = 1)
		self.ax.set_xlabel(r'$x$')
		self.ax.set_ylabel(r'$y$')
		if self.dim == '3d':
			self.ax.set_zlabel(r'$z$')

		if self.dim == '2d':
			self.ax.axhline(linewidth = 1.2, color = 'k')
			self.ax.axvline(linewidth = 1.2, color = 'k')
		self.ax.grid(True, linewidth = 0.8)

	########################################

	def axis_fix(self, axis          = None,
	                   trigonometric = False,
	                   first         = None,
	                   last          = None,
	                   step          = None):
		'''Set axis.'''

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
			self.fig.canvas.draw()
			
			# this line changes the font used for the ticks to a math mode font
			# math mode font is a beatiful serif font if you use the 'classic' plot style
			# this line also fixes the ticks, so that the ticks will not be redrawn when you zoom or pan the graph
			# I assume that this is okay, because the purpose of this script is to plot a nice-looking graph
			# minute analysis is not the purpose here
			labels_set_function([fr'${t.get_text()}$' for t in labels_get_function()])


################################################################################

def main():

	# read command line argument
	# check whether this should be a two- or three-dimensional plot
	try:
		dim = sys.argv[1]
		assert dim in {'2d', '3d'}
	except (IndexError, AssertionError):
		print('\033[1;31mProjection either invalid or not specified. Using default \'2d\'.\033[0m')
		dim = '2d'

	# set the plot style
	# I use 'classic' because it causes LaTeX-formatted strings to be rendered in Computer Modern
	# Computer Modern is prettier than the default font (at least on Linux)
	# for two-dimensional plots, I like to also use 'seaborn-poster', which increases the font size
	# in three-dimensional plots, this increased font size overlaps with surrounding text
	# hence, I use only use 'classic'
	if dim == '2d':
		plt.style.use(['classic', 'seaborn-poster'])
	else:
		plt.style.use('classic')

	# instantiate the class to take care of all the objects required
	grapher = CustomPlot(dim, keep_aspect_ratio = False)

	x1 = np.linspace(-16, 16, 100000)
	y1 = np.cos(x1)
	z1 = np.sin(x1)
	grapher.plot(x1, y1, z1, color = 'red', linestyle = '-', linewidth = 0.8, label = r'$R$')

	grapher.configure()
	grapher.axis_fix(axis          = 'x',
	                 trigonometric = True,
	                 first         = -4,
	                 last          = 4,
	                 step          = 0.5)
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

################################################################################

if __name__ == '__main__':
	main()
