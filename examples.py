import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import customplot

# this is the directory in which you will be prompted to save graphs
# currently, it is set to '.' (which means the current directory)
mpl.rcParams['savefig.directory'] = '.'

###############################################################################
# two-dimensional Cartesian plot
###############################################################################
with plt.style.context('dandy.mplstyle'):

    # create an instance of the `CustomPlot' class inside a style context
    # this ensures that the style is applied only to this particular plot
    grapher = customplot.CustomPlot()

    # set the locations of the grid lines on the x-axis
    # grid lines will be drawn at: [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    grapher.axis_fix('x', first = -2, last = 10, step = 1)

    # set the locations of the grid lines on the y-axis
    # grid lines will be drawn at: [-2, -1, 0, 1, 2, 3, 4]
    grapher.axis_fix('y', first = -2, last = 4, step = 1)

    x = np.linspace(0, 8, 10000)
    y = np.sqrt(x)
    grapher.plot(x, y, color = 'red', label = r'$y=\sqrt{x}$')

    # set the main title of the graph and do other basic appearance enhancements
    # if you do not provide the `title' argument, no title will be added
    grapher.configure(title = 'This is the square root function!')

    # set the graph aspect ratio (ratio of the scales on the y-axis and x-axis)
    # this line is optional
    grapher.aspect_fix(1)

    plt.show()
    plt.close(grapher.fig)

###############################################################################
# two-dimensional Cartesian plot with trigonometric grid spacing
###############################################################################
with plt.style.context('dandy.mplstyle'):

    # create an instance of the `CustomPlot' class inside a style context
    # this ensures that the style is applied only to this particular plot
    grapher = customplot.CustomPlot()

    # set the locations of the grid lines on the x-axis
    # `symbolic' indicates that the grid lines should be at pi times the range
    # i.e. grid lines will be drawn at: [-2.00 * pi, -1.75 * pi, -1.50 * pi, -1.25 * pi, -1.00 * pi, -0.75 * pi, -0.50 * pi, -0.25 * pi, 0.00 * pi, 0.25 * pi, 0.50 * pi, 0.75 * pi, 1.00 * pi, 1.25 * pi, 1.50 * pi, 1.75 * pi, 2.00 * pi]
    grapher.axis_fix('x', symbolic = True, first = -2, last = 2, step = 0.25)

    # set the locations of the grid lines on the y-axis
    # grid lines will be drawn at: [-3, -2, -1, 0, 1, 2, 3]
    grapher.axis_fix('y', first = -3, last = 3, step = 1)

    x = np.linspace(-2 * np.pi, 2 * np.pi, 10000)
    y = np.cos(x)
    grapher.plot(x, y, color = 'green', label = r'$y=\cos\,x$')

    # set the main title of the graph and do other basic appearance enhancements
    # if you do not provide the `title' argument, no title will be added
    grapher.configure(title = 'This is a trigonometric function!')

    # set the graph aspect ratio (ratio of the scales on the y-axis and x-axis)
    # this line is optional
    grapher.aspect_fix(1)

    plt.show()
    plt.close(grapher.fig)

###############################################################################
# two-dimensional Cartesian plot of a non-function
###############################################################################
with plt.style.context('dandy.mplstyle'):
    grapher = customplot.CustomPlot()
    grapher.axis_fix('x', first = -3, last = 5, step = 1)
    grapher.axis_fix('y', first = -9, last = 4, step = 1)

    t = np.linspace(0, 2 * np.pi, 10000)
    x = 3 * np.cos(t) + 1
    y = 5 * np.sin(t) - 2
    grapher.plot(x, y, label = r'$\dfrac{(x-1)^2}{9}+\dfrac{(y+2)^2}{25}=1$')
    grapher.configure(title = 'This is an ellipse!')
    grapher.aspect_fix(1)

    plt.show()
    plt.close(grapher.fig)

###############################################################################
# two-dimensional XKCD-style Cartesian plot (https://xkcd.com/605/)
###############################################################################
with plt.xkcd():
    grapher = customplot.CustomPlot(xkcd = True)

    x = [0, 1, 8]
    y = [0, 1, 8]
    grapher.plot(x, y, color = 'black', marker = 'o', mfc = 'black', markersize = 10, label = 'marriage rate')

    # since this is not a conventional graph, the axis labels must be changed
    grapher.configure(axis_labels = ('days', 'number of husbands'), title = 'my hobby: extrapolating')

    # some more modifications to emphasise the jocular nature of this plot
    grapher.ax.set_xticks([0, 1, 8])
    grapher.ax.set_xticklabels(['yesterday', 'today', 'next week (predicted)'])

    plt.show()
    plt.close(grapher.fig)

###############################################################################
# two-dimensional polar plot
###############################################################################
with plt.style.context('dandy.mplstyle'):
    grapher = customplot.CustomPlot(polar = True)

    # for polar plots, the y-axis is actually the radial axis
    # in most cases, `first' should be zero
    # grid lines will be drawn at: [0, 1, 2, 3, 4]
    # but the first (i.e. 0) and last (i.e. 4) will not be labelled
    # otherwise, the figure gets cluttered
    grapher.axis_fix('y', first = 0, last = 4, step = 1)

    t = np.linspace(0, 2 * np.pi, 10000)
    r = 1 - np.cos(t)
    grapher.plot(t, r, label = r'$r=1-\cos\,t$')

    # since this is a polar plot, the axis labels must be changed
    # the dollar signs ensure that the labels are written in a maths font
    grapher.configure(axis_labels = ('$t$', '$r$'), title = 'This is a cardioid!')

    plt.show()
    plt.close(grapher.fig)

###############################################################################
# two-dimensional polar plot with trigonometric grid spacing
###############################################################################
with plt.style.context('dandy.mplstyle'):
    grapher = customplot.CustomPlot(polar = True)

    # for polar plots, the x-axis is actually the angular axis
    # `symbolic' indicates that the grid lines should be at pi times the range
    # i.e. grid lines will be drawn at: [0.00 * pi, 0.25 * pi, 0.50 * pi, 0.75 * pi, 1.00 * pi, 1.25 * pi, 1.50 * pi, 1.75 * pi]
    # the last grid line (2.00 * pi) is ignored (it coincides with 0.00 * pi)
    grapher.axis_fix('x', symbolic = True, first = 0, last = 2, step = 0.25)

    # for polar plots, the y-axis is actually the radial axis
    # in most cases, `first' should be zero
    # grid lines will be drawn at: [0.0, 0.5, 1.0, 1.5, 2.0]
    # but the first (i.e. 0.0) and last (i.e. 2.0) will not be labelled
    # otherwise, the figure gets cluttered
    grapher.axis_fix('y', first = 0, last = 2, step = 0.5)

    t = np.linspace(0, 2 * np.pi, 10000)
    r = np.sqrt(t / np.pi / 2)
    grapher.plot(t, r, label = r'$r=\sqrt{\dfrac{t}{2\pi}}$')

    # since this is a polar plot, the axis labels must be specified
    # the dollar signs ensure that the labels are written in a maths font
    grapher.configure(axis_labels = ('$t$', '$r$'), title = 'This is a spiral!')

    plt.show()
    plt.close(grapher.fig)

###############################################################################
# three-dimensional Cartesian plot of a curve
###############################################################################
with plt.style.context('dandy.mplstyle'):
    grapher = customplot.CustomPlot(dim = 3)
    grapher.axis_fix('x', first = 0, last = 12, step = 1)
    grapher.axis_fix('y', first = -2, last = 2, step = 1)
    grapher.axis_fix('z', first = -2, last = 2, step = 1)

    x = np.linspace(0, 12, 10000)
    y = (3 / 4) ** x * np.cos(np.pi * x)
    z = (3 / 4) ** x * np.sin(np.pi * x)
    grapher.plot(x, y, z, color = 'gray', label = r'$y+iz=(-0.75)^x$')
    grapher.configure(title = 'This is a helix!')

    # as this is a three-dimensional plot, an aspect ratio does not make sense
    # hence, if the value is any non-zero number, the plot is drawn to scale
    # however, as in case of two-dimensional plots, this line is optional
    grapher.aspect_fix(1)

    plt.show()
    plt.close(grapher.fig)

###############################################################################
# three-dimensional Cartesian plot of a curve with trigonometric grid spacing
###############################################################################
with plt.style.context('dandy.mplstyle'):
    grapher = customplot.CustomPlot(dim = 3)
    grapher.axis_fix('x', symbolic = True, first = -4, last = 4, step = 0.5)
    grapher.axis_fix('y', first = -3, last = 3, step = 1)
    grapher.axis_fix('z', first = -3, last = 3, step = 1)

    x = np.linspace(-4 * np.pi, 4 * np.pi, 10000)
    y = np.cos(x)
    z = np.sin(x)
    grapher.plot(x, y, z, label = r'$y+iz=e^{ix}$')
    grapher.configure(title = 'This is a spring!')

    # as this is a three-dimensional plot, an aspect ratio does not make sense
    # hence, if the value is any non-zero number, the plot is drawn to scale
    # however, as in case of two-dimensional plots, this line is optional
    grapher.aspect_fix(1)

    plt.show()
    plt.close(grapher.fig)

###############################################################################
# three-dimensional Cartesian plot of a surface
###############################################################################
with plt.style.context('dandy.mplstyle'):
    grapher = customplot.CustomPlot(dim = 3)
    grapher.axis_fix('x', symbolic = True, first = -6, last = 6, step = 1)
    grapher.axis_fix('y', symbolic = True, first = -6, last = 6, step = 1)
    grapher.axis_fix('z', first = -4, last = 4, step = 2)

    x = np.linspace(-6 * np.pi, 6 * np.pi, 1000)
    y = np.linspace(-6 * np.pi, 6 * np.pi, 1000)
    X, Y = np.meshgrid(x, y)
    Z = 1.5 * np.cos(X / 2) * np.sin(Y / 5)
    surf = grapher.ax.plot_surface(X, Y, Z, color = 'skyblue', label = r'$z=1.5\cdot\cos\,0.5x\cdot\sin\,0.2y$')

    # this line is required because of a library bug
    surf._facecolors2d = surf._edgecolors2d = None

    grapher.configure(title = 'This is an interference pattern!')
    grapher.aspect_fix(1)

    plt.show()
    plt.close(grapher.fig)

