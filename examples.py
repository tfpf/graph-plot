import matplotlib.pyplot as plt
import numpy as np

import customplot

###############################################################################
# two-dimensional Cartesian plot (bare minimum)
###############################################################################
with plt.style.context('dandy.mplstyle'):
    ax = plt.figure().add_subplot()

    x = np.linspace(0, 8, 10000)
    y = np.sqrt(x)
    ax.plot(x, y, label = r'$y=\sqrt{x}$')

    customplot.polish(ax, title = 'This is a bare minimum example!')

    plt.show()

###############################################################################
# two-dimensional Cartesian plot
###############################################################################
with plt.style.context('dandy.mplstyle'):

    # create a Matplotlib axes instance
    ax = plt.figure().add_subplot()

    # set the locations of the grid lines on the x-axis
    # grid lines will be drawn at: [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    customplot.limit(ax, 'x', first = -2, last = 10, step = 1)

    # set the locations of the grid lines on the y-axis
    # grid lines will be drawn at: [-2, -1, 0, 1, 2, 3, 4]
    customplot.limit(ax, 'y', first = -2, last = 4, step = 1)

    x = np.linspace(0, 8, 10000)
    y = np.sqrt(x)
    ax.plot(x, y, color = 'red', label = r'$y=\sqrt{x}$')

    customplot.polish(ax, title = 'This is the square root function!')

    # set the graph aspect ratio (ratio of the scales on the x-axis and y-axis)
    customplot.aspect(ax, ratio = 1)

    plt.show()

###############################################################################
# two-dimensional Cartesian plot (trigonometric grid spacing)
###############################################################################
with plt.style.context('dandy.mplstyle'):
    ax = plt.figure().add_subplot()

    # set the locations of the grid lines on the x-axis
    # `symbolic' indicates that the grid lines should be at multiples of π
    # i.e. grid lines will be drawn at: [-2π, -1.75π, -1.5π, -1.25π, -π, -0.75π, -0.5π, -0.25π, 0, 0.25π, 0.5π, 0.75π, π, 1.25π, 1.5π, 1.75π, 2π]
    customplot.limit(ax, 'x', symbolic = True, first = -2, last = 2, step = 0.25)

    # set the locations of the grid lines on the y-axis
    # grid lines will be drawn at: [-3, -2, -1, 0, 1, 2, 3]
    customplot.limit(ax, 'y', first = -3, last = 3, step = 1)

    x = np.linspace(-2 * np.pi, 2 * np.pi, 10000)
    y = np.cos(x)
    ax.plot(x, y, color = 'green', label = r'$y=\cos\,x$')

    customplot.polish(ax, title = 'This is a trigonometric function!')
    customplot.aspect(ax, 1)

    plt.show()

###############################################################################
# two-dimensional Cartesian plot (implicitly defined functions)
###############################################################################
with plt.style.context('dandy.mplstyle'):
    ax = plt.figure().add_subplot()
    customplot.limit(ax, 'x', first = -3, last = 5, step = 1)
    customplot.limit(ax, 'y', first = -9, last = 4, step = 1)

    t = np.linspace(0, 2 * np.pi, 10000)
    x = 3 * np.cos(t) + 1
    y = 5 * np.sin(t) - 2
    ax.plot(x, y, label = r'$\dfrac{(x-1)^2}{9}+\dfrac{(y+2)^2}{25}=1$')

    customplot.polish(ax, title = 'This is an ellipse!')
    customplot.aspect(ax, 1)

    plt.show()

###############################################################################
# two-dimensional polar plot
###############################################################################
with plt.style.context('dandy.mplstyle'):
    ax = plt.figure().add_subplot(projection = 'polar')

    # for polar plots, the y-axis is actually the radial axis
    # in most cases, `first' should be zero
    # grid lines will be drawn at: [0, 1, 2, 3, 4]
    # but the first (i.e. 0) and last (i.e. 4) will not be labelled
    # otherwise, the figure gets cluttered
    customplot.limit(ax, 'y', first = 0, last = 4, step = 1)

    t = np.linspace(0, 2 * np.pi, 10000)
    r = 1 - np.cos(t)
    ax.plot(t, r, label = r'$r=1-\cos\,t$')

    # since this is a polar plot, the axis labels must be changed
    # the dollar signs ensure that the labels are written in a maths font
    customplot.polish(ax, labels = ('$t$', '$r$'), title = 'This is a cardioid!')

    plt.show()

###############################################################################
# two-dimensional polar plot (trigonometric grid spacing)
###############################################################################
with plt.style.context('dandy.mplstyle'):
    ax = plt.figure().add_subplot(projection = 'polar')

    # for polar plots, the x-axis is actually the angular axis
    # `symbolic' indicates that the grid lines should be at pi times the range
    # i.e. grid lines will be drawn at: [0, 0.25π, 0.5π, 0.75π, π, 1.25π, 1.5π, 1.75π]
    # the last grid line (2π) is ignored (it coincides with 0)
    customplot.limit(ax, 'x', symbolic = True, first = 0, last = 2, step = 0.25)

    # for polar plots, the y-axis is actually the radial axis
    # in most cases, `first' should be zero
    # grid lines will be drawn at: [0.0, 0.5, 1.0, 1.5, 2.0]
    # but the first (i.e. 0.0) and last (i.e. 2.0) will not be labelled
    # otherwise, the figure gets cluttered
    customplot.limit(ax, 'y', first = 0, last = 2, step = 0.5)

    t = np.linspace(0, 2 * np.pi, 10000)
    r = np.sqrt(t / np.pi / 2)
    ax.plot(t, r, label = r'$r=\sqrt{\dfrac{t}{2\pi}}$')

    # since this is a polar plot, the axis labels must be changed
    # the dollar signs ensure that the labels are written in a maths font
    customplot.polish(ax, labels = ('$t$', '$r$'), title = 'This is a spiral!')

    plt.show()

###############################################################################
# two-dimensional subplots
###############################################################################
with plt.style.context('dandy.mplstyle'):
    fig = plt.figure()
    axs = [None] * 3
    axs[0] = fig.add_subplot(2, 2, 1, projection = 'polar')
    axs[1] = fig.add_subplot(2, 2, 2)
    axs[2] = fig.add_subplot(2, 1, 2)

    customplot.limit(axs[0], 'y', first = 0, last = 4, step = 1)
    t = np.linspace(0, 2 * np.pi, 10000)
    r = 2 * np.sin(3 * t)
    axs[0].plot(t, r, label = r'$r=2\,\sin\,3t$')
    customplot.polish(axs[0], labels = ('$t$', '$r$'), title = 'This is a flower!')

    customplot.limit(axs[1], 'x', first = 0, last = 8, step = 1)
    customplot.limit(axs[1], 'y', first = 0, last = 4, step = 1)
    x = np.linspace(0, 8, 10000)
    y = x / 2
    axs[1].plot(x, y, label = r'$x-2y=0$')
    customplot.polish(axs[1], title = 'This is a line!')

    customplot.limit(axs[2], 'x', first = 0, last = 8, step = 0.5)
    customplot.limit(axs[2], 'y', first = -1, last = 1, step = 0.5)
    x = np.linspace(0, 8, 10000)
    y = np.random.randn(10000) / 10
    axs[2].plot(x, y, label = r'Noise')
    customplot.polish(axs[2], title = 'This is a random signal!')

    plt.show()

###############################################################################
# three-dimensional Cartesian plot (curve)
###############################################################################
with plt.style.context('dandy.mplstyle'):
    ax = plt.figure().add_subplot(projection = '3d')
    customplot.limit(ax, 'x', first = 0, last = 12, step = 1)
    customplot.limit(ax, 'y', first = -2, last = 2, step = 1)
    customplot.limit(ax, 'z', first = -2, last = 2, step = 1)

    x = np.linspace(0, 12, 10000)
    y = (3 / 4) ** x * np.cos(np.pi * x)
    z = (3 / 4) ** x * np.sin(np.pi * x)
    ax.plot(x, y, z, color = 'gray', label = r'$y+iz=(-0.75)^x$')

    customplot.polish(ax, title = 'This is a helix!')

    # if the aspect ratio is 1, the scales on all three axes are made equal
    # otherwise, it is ignored
    customplot.aspect(ax, 1)

    plt.show()

###############################################################################
# three-dimensional Cartesian plot (curve) (trigonometric grid spacing)
###############################################################################
with plt.style.context('dandy.mplstyle'):
    ax = plt.figure().add_subplot(projection = '3d')
    customplot.limit(ax, 'x', symbolic = True, first = -4, last = 4, step = 0.5)
    customplot.limit(ax, 'y', first = -3, last = 3, step = 1)
    customplot.limit(ax, 'z', first = -3, last = 3, step = 1)

    x = np.linspace(-4 * np.pi, 4 * np.pi, 10000)
    y = np.cos(x)
    z = np.sin(x)
    ax.plot(x, y, z, label = r'$y+iz=e^{ix}$')

    customplot.polish(ax, title = 'This is a spring!')

    # if the aspect ratio is 1, the scales on all three axes are made equal
    # otherwise, it is ignored
    customplot.aspect(ax, 1)

    plt.show()

###############################################################################
# three-dimensional Cartesian plot (surface) (trigonometric grid spacing)
###############################################################################
with plt.style.context('dandy.mplstyle'):
    ax = plt.figure().add_subplot(projection = '3d')
    customplot.limit(ax, 'x', symbolic = True, first = -6, last = 6, step = 1)
    customplot.limit(ax, 'y', symbolic = True, first = -6, last = 6, step = 1)
    customplot.limit(ax, 'z', first = -4, last = 4, step = 2)

    x = np.linspace(-6 * np.pi, 6 * np.pi, 1000)
    y = np.linspace(-6 * np.pi, 6 * np.pi, 1000)
    X, Y = np.meshgrid(x, y)
    Z = 1.5 * np.cos(X / 2) * np.sin(Y / 5)
    surf = ax.plot_surface(X, Y, Z, color = 'skyblue', label = r'$z=1.5\cdot\cos\,0.5x\cdot\sin\,0.2y$')

    # this line is required because of a library bug
    surf._facecolors2d = surf._edgecolors2d = None

    customplot.polish(ax, title = 'This is an interference pattern!')
    customplot.aspect(ax, 1)

    plt.show()

