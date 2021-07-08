import matplotlib.pyplot as plt
import numpy as np

import customplot

# Globally apply the style parameters.
plt.style.use('dandy.mplstyle')

###############################################################################

def cartesian_2d_minimal():
    '''\
Example of a minimal two-dimensional Cartesian plot.
'''

    ax = plt.figure().add_subplot()

    x = np.linspace(0, 20, 10000)
    y = np.sqrt(x)
    ax.plot(x, y, label = r'$y=\sqrt{x}$')

    customplot.polish(ax, title = 'This is a bare minimum example!')

    plt.show()

###############################################################################

def cartesian_2d():
    '''\
Example of a two-dimensional Cartesian plot.
'''

    # Create a Matplotlib axes instance.
    ax = plt.figure().add_subplot()

    # Set the locations of the grid lines on the x-axis. Grid lines will be
    # drawn at the following x-coordinates.
    # [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    customplot.limit(ax, 'x', first = -2, last = 10, step = 1)

    # Set the locations of the grid lines on the y-axis. Grid lines will be
    # drawn at the following y-coordinates.
    # [-2, -1, 0, 1, 2, 3, 4]
    customplot.limit(ax, 'y', first = -2, last = 4, step = 1)

    x = np.linspace(0, 20, 10000)
    y = np.sqrt(x)
    ax.plot(x, y, color = 'red', label = r'$y=\sqrt{x}$')

    customplot.polish(ax, title = 'This is the square root function!')

    # Set the ratio of the scales on the x-axis and y-axis (aspect ratio). As
    # far as possible, this should be set to 1 (so that shapes are not
    # distorted).
    customplot.aspect(ax, 1)

    plt.show()

###############################################################################

def cartesian_2d_discontinuous():
    '''\
Example of a two-dimensional Cartesian plot of a discontinuous function.
'''

    # Create a Matplotlib axes instance.
    ax = plt.figure().add_subplot()

    # Set the locations of the grid lines on the x-axis. Grid lines will be
    # drawn at the following x-coordinates.
    # [-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8]
    customplot.limit(ax, 'x', first = -4, last = 4, step = 0.5)

    # Set the locations of the grid lines on the y-axis. Grid lines will be
    # drawn at the following y-coordinates.
    # [-4, -3, -2, -1, 0, 1, 2, 3, 4]
    customplot.limit(ax, 'y', first = -1.5, last = 2.5, step = 0.5)

    x = np.linspace(-4, 4, 10000)
    y = np.heaviside(x, 0.5)

    # Remove the vertical line at the point of discontinuity.
    y = customplot.sanitise(y, maximum_diff = 0.1)

    ax.plot(x, y, color = 'red', label = r'$y=u(x)$')

    # Show the values of the function near the point of discontinuity.
    ax.plot(0, 0, color = 'red', linestyle = 'none', marker = 'o')
    ax.plot(0, 1, color = 'red', linestyle = 'none', marker = 'o')
    ax.plot(0, 0.5, color = 'red', linestyle = 'none', marker = 'o', mfc = 'red')

    customplot.polish(ax, title = 'This is the unit step function!')

    # Set the ratio of the scales on the x-axis and y-axis (aspect ratio). As
    # far as possible, this should be set to 1 (so that shapes are not
    # distorted).
    customplot.aspect(ax, 1)

    plt.show()

###############################################################################

def cartesian_2d_symbolic_1():
    '''\
Example of a two-dimensional Cartesian plot with symbolic labels on the x-axis.
Said labels contain the symbol for pi (π).
'''

    ax = plt.figure().add_subplot()

    # Set the locations of the grid lines on the x-axis. Note that `symbolic'
    # has been set to True. As a result, grid lines will be drawn at the
    # following x-coordinates.
    # [-2π, -1.75π, -1.5π, -1.25π, -π, -0.75π, -0.5π, -0.25π, 0, 0.25π, 0.5π, 0.75π, π, 1.25π, 1.5π, 1.75π, 2π]
    customplot.limit(ax, 'x', symbolic = True, first = -2, last = 2, step = 0.25)

    # Set the locations of the grid lines on the y-axis. Grid lines will be
    # drawn at the following y-coordinates.
    # [-3, -2, -1, 0, 1, 2, 3]
    customplot.limit(ax, 'y', first = -3, last = 3, step = 1)

    x = np.linspace(-2 * np.pi, 2 * np.pi, 10000)
    y = np.cos(x)
    ax.plot(x, y, color = 'green', label = r'$y=\cos\,x$')

    customplot.polish(ax, title = 'This is a trigonometric function!')
    customplot.aspect(ax, 1)

    plt.show()

###############################################################################

def cartesian_2d_symbolic_2():
    '''\
Example of a two-dimensional Cartesian plot with symbolic labels on the x-axis.
Said labels contain the symbols for pi (π) and the Euler–Mascheroni constant
(γ).
'''

    ax = plt.figure().add_subplot()

    # Set the locations of the grid lines on the x-axis. Note that `symbolic'
    # has been set to True, and a value has been provided for `s' and `v'. As a
    # result, grid lines will be drawn at the following x-coordinates.
    # [-2π/γ, -1.75π/γ, -1.5π/γ, -1.25π/γ, -π/γ, -0.75π/γ, -0.5π/γ, -0.25π/γ, 0, 0.25π/γ, 0.5π/γ, 0.75π/γ, π/γ, 1.25π/γ, 1.5π/γ, 1.75π/γ, 2π/γ]
    customplot.limit(ax, 'x', symbolic = True, s = r'\pi/\gamma', v = np.pi / np.euler_gamma, first = -2, last = 2, step = 0.25)

    # Set the locations of the grid lines on the y-axis. Grid lines will be
    # drawn at the following y-coordinates.
    # [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
    customplot.limit(ax, 'y', first = -5, last = 5, step = 1)

    x = np.linspace(-12, 12, 10000)
    y = np.cos(np.euler_gamma * x)
    ax.plot(x, y, color = 'green', label = r'$y=\cos\,\gamma x$')

    customplot.polish(ax, title = 'This is a horizontally-scaled trigonometric function!')
    customplot.aspect(ax, 1)

    plt.show()

###############################################################################

def interactive():
    '''\
Example of an interactive plot.

Note that an interactive plot should be created only inside a function (like it
has been done here). At the very least, it should be done in a function called
`main', and
    if __name__ == '__main__':
        main()
should be used. If this is not done, Python may complain about problems with
starting a process.

This won't work on macOS unless a Tkinter-based backend is used. However, this
is handled automatically, so there should be no problems.
'''

    fig = plt.figure()
    ax = fig.add_subplot()
    customplot.limit(ax, 'x', first = -6, last = 6, step = 1)
    customplot.limit(ax, 'y', first = -3, last = 3, step = 1)

    x = np.linspace(-8, 8, 10000)
    y = np.sin(x)
    ax.plot(x, y, label = r'$y=\sin\,x$')
    ax.text(0, 0, r'$(0,0)$', size = 'large')
    ax.text(np.pi, 0, r'$(\pi,0)$', size = 'large')

    customplot.polish(ax, title = 'This is an interactive plot!')
    customplot.aspect(ax, 1)

    # Instead of calling `plt.show', call `customplot.show'. Provide the
    # Matplotlib figure instance as the argument.
    customplot.show(fig)

    # After doing this, two windows will open: the plot window and an
    # interactive GUI. This GUI has three parts.

    # The upper part is a ribbon where you can select one of the Matplotlib
    # axes present in the figure.

    # The middle part contains twelve entries and three checkboxes which can be
    # used to manipulate the axes of coordinates. 'Symbolic' is a checkbox
    # indicating whether the markings on the axis should be at multiples of the
    # number entered in 'Value'. 'Symbol' is a string which represents said
    # value. 'Limits' shall contain three space-separated numbers, which are
    # used as the arguments `first', `last' and `step' for the function
    # `customplot.limit'. 'Label' is used to label the axis of coordinates.
    # After you're done typing into any entry, press Enter. The plot will get
    # updated.

    # The lower part contains as many entries as there are text objects in the
    # plot. Specify the coordinates (again, space-separated) at which these
    # text objects must be placed, and press Enter. The plot will get updated.

###############################################################################

def cartesian_2d_ellipse():
    '''\
Example of a two-dimensional Cartesian plot of an ellipse.
'''

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

def polar():
    '''\
Example of a polar plot.
'''

    ax = plt.figure().add_subplot(projection = 'polar')

    # In a polar plot, the y-axis is actually the radial axis. In most cases,
    # this axis should start from zero. Grid lines will be drawn at the
    # following r-coordinates.
    # [0, 1, 2, 3, 4]
    # However, the first and last grid lines will not be labelled (otherwise,
    # the figure gets cluttered).
    customplot.limit(ax, 'y', first = 0, last = 4, step = 1)

    t = np.linspace(0, 2 * np.pi, 10000)
    r = 1 - np.cos(t)
    ax.plot(t, r, label = r'$r=1-\cos\,t$')

    # The polar coordinate axes should be labelled 't' and 'r', not 'x' and
    # 'y'. These labels are surrounded by dollar signs so that they are
    # rendered the way mathematical expressions would be rendered.
    customplot.polish(ax, labels = ('$t$', '$r$'), title = 'This is a cardioid!')

    # An aspect ratio is meaningless in polar plots. Hence, `ax.set_aspect' is
    # not called.

    plt.show()

###############################################################################

def polar_symbolic():
    '''\
Example of a polar plot with symbolic labels on the angular axis. Said labels
contain the symbol for pi (π).
'''

    ax = plt.figure().add_subplot(projection = 'polar')

    # In a polar plot, the x-axis is actually the angular axis. Note that
    # `symbolic' has been set to True. As a result, grid lines will be drawn at
    # the following t-coordinates.
    # [0, 0.25π, 0.5π, 0.75π, π, 1.25π, 1.5π, 1.75π]
    # No grid line is drawn at 2π because a t-coordinate of 2π is the same as a
    # t-coordinate of 0.
    customplot.limit(ax, 'x', symbolic = True, first = 0, last = 2, step = 0.25)

    # In a polar plot, the y-axis is actually the radial axis. In most cases,
    # this axis should start from zero. Grid lines will be drawn at the
    # following r-coordinates.
    # [0.0, 0.5, 1.0, 1.5, 2.0]
    # However, the first and last grid lines will not be labelled (otherwise,
    # the figure gets cluttered).
    customplot.limit(ax, 'y', first = 0, last = 2, step = 0.5)

    # This is not a trigonometric function, so the range of values the
    # independent variable `t' may take is not restricted. Here, the upper
    # limit on `t' has been chosen in such a way that the visible portion of
    # the graph does not end abruptly.
    t = np.linspace(0, 25, 10000)
    r = np.sqrt(t / np.pi / 2)
    ax.plot(t, r, label = r'$r=\sqrt{\dfrac{t}{2\pi}}$')

    # The polar coordinate axes should be labelled 't' and 'r', not 'x' and
    # 'y'. These labels are surrounded by dollar signs so that they are
    # rendered the way mathematical expressions would be rendered.
    customplot.polish(ax, labels = ('$t$', '$r$'), title = 'This is a spiral!')

    # An aspect ratio is meaningless in polar plots. Hence, `ax.set_aspect' is
    # not called.

    plt.show()

###############################################################################

def subplots():
    '''\
Example of subplots.
'''

    fig = plt.figure()
    axs = [None] * 3
    axs[0] = fig.add_subplot(2, 2, 1)
    axs[1] = fig.add_subplot(2, 2, 3)
    axs[2] = fig.add_subplot(1, 2, 2, projection = 'polar')

    customplot.limit(axs[0], 'x', first = 0, last = 8, step = 1)
    customplot.limit(axs[0], 'y', first = 0, last = 4, step = 1)
    x = np.linspace(0, 8, 10000)
    y = x / 2
    axs[0].plot(x, y, color = 'green', label = r'$x-2y=0$')
    customplot.polish(axs[0], title = 'This is a line!')
    customplot.aspect(axs[0], 1)

    customplot.limit(axs[1], 'x', first = 0, last = 8, step = 0.5)
    customplot.limit(axs[1], 'y', first = -1, last = 1, step = 0.5)
    x = np.linspace(0, 8, 4000)
    y = np.random.randn(len(x)) / 10
    axs[1].plot(x, y, label = r'$\nu=\psi(\tau)$')
    customplot.polish(axs[1], labels = (r'$\tau$', r'$\nu$'), title = 'This is random noise!')
    customplot.aspect(axs[1], 1)

    customplot.limit(axs[2], 'x', first = 0, last = 2 * np.pi, step = np.pi / 6)
    customplot.limit(axs[2], 'y', first = 0, last = 5, step = 1)
    phi = np.linspace(0, 2 * np.pi, 10000)
    rho = 4 * np.sin(3 * phi)
    axs[2].plot(phi, rho, color = 'red', label = r'$\rho=4\,\sin\,3\varphi$')
    customplot.polish(axs[2], labels = (r'$\varphi$', r'$\rho$'), title = 'This is a flower!')

    plt.show()

###############################################################################

def cartesian_3d_curve():
    '''\
Example of a three-dimensional Cartesian plot of a curve.
'''

    ax = plt.figure().add_subplot(projection = '3d')
    customplot.limit(ax, 'x', first = 0, last = 12, step = 1)
    customplot.limit(ax, 'y', first = -2, last = 2, step = 1)
    customplot.limit(ax, 'z', first = -2, last = 2, step = 1)

    x = np.linspace(0, 12, 10000)
    y = (3 / 4) ** x * np.cos(np.pi * x)
    z = (3 / 4) ** x * np.sin(np.pi * x)
    ax.plot(x, y, z, color = 'gray', label = r'$y+iz=(-0.75)^x$')

    customplot.polish(ax, title = 'This is a helix!')

    # An aspect ratio is meaningless in three-dimensional plots, because there
    # are three axes of coordinates. Hence, if `ax.set_aspect' is called with
    # any non-zero ratio, the scales on the x-axis, y-axis and z-axis will be
    # made equal.
    customplot.aspect(ax, 1)

    plt.show()

###############################################################################

def cartesian_3d_curve_symbolic():
    '''\
Example of a three-dimensional Cartesian plot of a curve with symbolic labels
on the x-axis. Said labels contain the symbol for pi (π).
'''

    ax = plt.figure().add_subplot(projection = '3d')
    customplot.limit(ax, 'x', symbolic = True, first = -4, last = 4, step = 0.5)
    customplot.limit(ax, 'y', first = -3, last = 3, step = 1)
    customplot.limit(ax, 'z', first = -3, last = 3, step = 1)

    x = np.linspace(-4 * np.pi, 4 * np.pi, 10000)
    y = np.cos(x)
    z = np.sin(x)
    ax.plot(x, y, z, label = r'$y+iz=e^{ix}$')

    customplot.polish(ax, title = 'This is a spring!')

    # An aspect ratio is meaningless in three-dimensional plots, because there
    # are three axes of coordinates. Hence, if `ax.set_aspect' is called with
    # any non-zero ratio, the scales on the x-axis, y-axis and z-axis will be
    # made equal.
    customplot.aspect(ax, 1)

    plt.show()

###############################################################################

def cartesian_3d_surface_symbolic():
    '''\
Example of a three-dimensional Cartesian plot of a surface with symbolic labels
on the x-axis and the y-axis. Said labels contain the symbol for pi (π).
'''

    ax = plt.figure().add_subplot(projection = '3d')
    customplot.limit(ax, 'x', symbolic = True, first = -6, last = 6, step = 1)
    customplot.limit(ax, 'y', symbolic = True, first = -6, last = 6, step = 1)
    customplot.limit(ax, 'z', first = -4, last = 4, step = 2)

    x = np.linspace(-6 * np.pi, 6 * np.pi, 1000)
    y = np.linspace(-6 * np.pi, 6 * np.pi, 1000)
    X, Y = np.meshgrid(x, y)
    Z = 1.5 * np.cos(X / 2) * np.sin(Y / 5)
    surf = ax.plot_surface(X, Y, Z, color = 'skyblue', label = r'$z=1.5\cdot\cos\,0.5x\cdot\sin\,0.2y$')

    # This line is required because of a library bug.
    surf._facecolors2d = surf._edgecolors2d = None

    customplot.polish(ax, title = 'This is an interference pattern!')
    customplot.aspect(ax, 1)

    plt.show()

###############################################################################

if __name__ == '__main__':
    cartesian_2d_minimal()
    cartesian_2d()
    cartesian_2d_discontinuous()
    cartesian_2d_symbolic_1()
    cartesian_2d_symbolic_2()
    interactive()
    cartesian_2d_ellipse()
    polar()
    polar_symbolic()
    subplots()
    cartesian_3d_curve()
    cartesian_3d_curve_symbolic()
    cartesian_3d_surface_symbolic()

