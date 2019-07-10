#!/usr/bin/env python3

import colorama
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

	ax.plot(np.cos(0.9), np.sin(0.9), 'k.'); ax.text(np.cos(0.9) + 0.04, np.sin(0.9), r'$\left(\cos\,\theta,\sin\,\theta\right)$')
	ax.plot(np.cos(0.9), np.sin(0.9), 'k.'); ax.text(np.cos(0.9) + 0.04, np.sin(0.9), r'$\left(\cos\,\theta,\sin\,\theta\right)$')
	ax.text(np.cos(0.9) / 2 - 0.07, np.sin(0.9) + 0.01, r'$\cos\,\theta$')
	ax.text(np.cos(0.9) + 0.03, np.sin(0.9) / 2 - 0.04, r'$\sin\,\theta$')
	ax.text(0.08, 0.03, r'$\theta$')
	ax.text(1.11, 0.4, r'$\tan\,\theta$')
	ax.text(0.34, 1.02, r'$\cot\,\theta$')

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
              ystep = None,
              ztrigonometric = False,
              z1 = None,
              z2 = None,
              zstep = None):
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
	And 'ztrigonometric', 'z1', 'z2' and 'zstep'.

	Args:
		fig: the figure which contains the graph plot
		ax: Axes object
		keep_aspect_ratio: boolean, whether both axes are to have an identical scale
		xtrigonometric: boolean, whether the horizontal axis should be marked at multiples of pi
		x1: first x-coordinate to be shown
		x2: last x-coordinate to be shown
		xstep: gap between x-axis ticks
		ytrigonometric: boolean, whether the vertical axis should be marked at multiples of pi
		y1: first y-coordinate to be shown
		y2: last y-coordinate to be shown
		ystep: gap between y-axis ticks
		ztrigonometric: boolean, whether the vertical axis should be marked at multiples of pi
		z1: first z-coordinate to be shown
		z2: last z-coordinate to be shown
		zstep: gap between z-axis ticks

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
	ax.set_ylabel(r'$y$')
	ax.set_zlabel(r'$z$')
	
	# enable grid
	ax.grid(True, linewidth = 0.4)
	
	# placing ticks on the x-axis at rational multiples of pi
	if xtrigonometric:
		if x1 is None or x2 is None or xstep is None:
			raise ValueError('xtrigonometric has been set to True. x1, x2 and xstep must not be None.')
		
		# obtain lists of ticks and labels
		x_labels, x_ticks = graph_ticks(x1, x2, xstep)
		ax.set_xlim(np.pi * x1, np.pi * x2)
		ax.set_xticklabels(x_labels)
		ax.set_xticks(x_ticks)
		
	# placing ticks on the x-axis normally
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
		ax.set_xticklabels([r'${}$'.format(t.get_text()) for t in ax.get_xticklabels()])
	
	# placing ticks on the y-axis at rational multiples of pi
	if ytrigonometric:
		if y1 is None or y2 is None or ystep is None:
			raise ValueError('ytrigonometric has been set to True. y1, y2 and ystep must not be None.')
			
		# obtain lists of ticks and labels
		y_labels, y_ticks = graph_ticks(y1, y2, ystep)
		ax.set_ylim(np.pi * y1, np.pi * y2)
		ax.set_yticklabels(y_labels)
		ax.set_yticks(y_ticks)
	
	# placing ticks on the y-axis normally
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
		ax.set_yticklabels([r'${}$'.format(t.get_text()) for t in ax.get_yticklabels()])
	
	# placing ticks on the z-axis at rational multiples of pi
	if ztrigonometric:
		if z1 is None or z2 is None or zstep is None:
			raise ValueError('ztrigonometric has been set to True. z1, z2 and ystep must not be None.')
			
		# obtain lists of ticks and labels
		z_labels, z_ticks = graph_ticks(z1, z2, zstep)
		ax.set_zlim(np.pi * z1, np.pi * z2)
		ax.set_zticklabels(z_labels)
		ax.set_zticks(z_ticks)
	
	# placing ticks on the z-axis normally
	else:
	
		# this is the non-trigonometric case
		# if you don't provide z1 and z2, they will be chosen automatically
		if z1 and z2 and zstep:
			ax.set_zticks(np.arange(z1, z2 + zstep, zstep))
		if z1 and z2:
			ax.set_zlim(z1, z2)
		
		# draw the graph with the zticks obtained above
		# if zticks were not obtained above, they will have been chosen automatically
		fig.canvas.draw()
		
		# this line changes the font used for the ticks to a math mode font
		ax.set_zticklabels([r'${}$'.format(t.get_text()) for t in ax.get_zticklabels()])

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
		print(f'{colorama.Fore.RED}{colorama.Style.BRIGHT}Plot style either not specified or invalid. Using \'classic\'.\nHere is a list of the available styles.')
		colorama.deinit()
		plt.style.use('classic')
	show_nice_list(plt.style.available)
	print()

	# set up a window to display the graph
	# window title number is Unix time
	fig = plt.figure()
	ax = fig.gca(projection = '3d')
	fig.canvas.set_window_title(f'graph_{int(time.time())}')

	########################################

	# t = np.concatenate([np.linspace(-20, -1, 100000), np.linspace(-1, 0, 100000), np.linspace(0, 20, 100000)])
	x1 = np.linspace(-8, 8, 100000)
	y1 = np.cos(np.pi * x1)
	z1 = np.sin(np.pi * x1)
	ax.plot(x1, y1, z1, 'r-', label = r'$y+iz=(-1)^x$', linewidth = 0.8)
	# x2 = np.linspace(-20, 20, 100000)
	# y2 = np.sin(9 * x1) * np.cos(7 * x1)
	# ax.plot(x2, y2, 'b-', label = r'$y=\sin\,9x\,\cos\,7x$', linewidth = 0.8)
	# x3 = [33 / 8, 33 / 8]
	# y3 = [-100, 100]
	# ax.plot(x3, y3, 'g--', label = r'$x=\dfrac{33}{8}$', linewidth = 0.8)
	# x4 = np.linspace(-20, 20, 100000)
	# y4 = np.exp(-x4)
	# ax.plot(x4, y4, 'm-', label = r'$y=e^{-x}$', linewidth = 0.8)
	# x5 = np.linspace(-1, 1, 100000)
	# y5 = [f(20, x) for x in x2]
	# ax.plot(x5, y5, 'c-', label = r'$y=f_{20}(x)$', linewidth = 0.8)
	# mark_points(ax)
	configure(fig,
	          ax,
	          keep_aspect_ratio = False,
	          xtrigonometric = False,
	          x1 = -8,
	          x2 = 8,
	          xstep = 2,
	          ytrigonometric = False,
	          y1 = -8,
	          y2 = 8,
	          ystep = 2,
	          ztrigonometric = False,
	          z1 = -1,
	          z2 = 1,
	          zstep = 0.5)

	plt.show()
