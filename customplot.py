#! /usr/local/bin/python3.8

import fractions
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys
import time

# GUI and non-GUI backends for matplotlib
# print(matplotlib.rcsetup.interactive_bk)
# print(matplotlib.rcsetup.non_interactive_bk)
matplotlib.use('TkAgg')

matplotlib.rcParams['figure.dpi']          = 125
matplotlib.rcParams['savefig.dpi']         = 200
matplotlib.rcParams['savefig.format']      = 'png'
matplotlib.rcParams['savefig.directory']   = '/mnt/c/Users/vpaij/Pictures/'
matplotlib.rcParams['savefig.orientation'] = 'portrait'

###############################################################################

def show_nice_list(items, columns = 3):
    '''\
Display a list in neat centred columns.

Args:
    items: list (each list element must have an `__str__' method)
    columns: int (number of columns to arrange `items' in)

Returns:
    None
'''

    # convert 1D list to 2D list
    while len(items) % columns:
        items.append('')
    rows = len(items) // columns
    items = [items[i :: rows] for i in range(rows)]

    # calculate the required width of all columns
    # width of a column is width of longest string in that column
    widths = [max([len(str(row[i])) for row in items]) for i in range(columns)]
    for row in items:
        for r, width in zip(row, widths):
            print(str(r).center(width + 2, ' '), end = '', flush = True)
        print()

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
    points_of_discontinuity = np.abs(np.r_[[0], np.diff(y)]) > 0.1
    y[points_of_discontinuity] = np.nan

    return y

###############################################################################

def graph_ticks(first, last, step, symbol = r'\pi', symval = np.pi):
    r'''
Create a list of tick values and labels at intervals of `step * np.pi'. I think
it is best explained with examples. (To properly demonstrate the working, this
docstring is being marked as a raw string. Otherwise, the backslashes will be
interpreted as parts of escape sequences. You can test the functionality using
the `doctest' module.)
>>> graph_ticks(-1, 5, 2)
(['$-\\pi$', '$\\pi$', '$3\\pi$', '$5\\pi$'], array([-3.14159265,  3.14159265,  9.42477796, 15.70796327]))
>>> graph_ticks(-1, -1 / 4, 1 / 4)
(['$-\\pi$', '$-\\dfrac{3\\pi}{4}$', '$-\\dfrac{\\pi}{2}$', '$-\\dfrac{\\pi}{4}$'], array([-3.14159265, -2.35619449, -1.57079633, -0.78539816]))
>>> graph_ticks(-2, 2, 1)
(['$-2\\pi$', '$-\\pi$', '$0$', '$\\pi$', '$2\\pi$'], array([-6.28318531, -3.14159265,  0.        ,  3.14159265,  6.28318531]))

What's required is a list of LaTeX-formatted strings for numbers going from one
rational multiple of pi to another, and the `np.array' of corresponding values.
Thus, a two-element tuple should be returned. (Note that LaTeX uses a backslash
to indicate keywords! Remember to either escape the backslash or simply use raw
strings. The latter approach was used just to keep all of those things simple.)
As a side effect of using LaTeX strings as labels instead of whatever is chosen
automatically, panning or zooming the graph does not update the grid lines like
it does otherwise.

Args:
    first: float (grid lines start at `first * np.pi')
    last: float (grid lines end at `last * np.pi')
    step: float (grid lines are separated by `step * np.pi')
    symbol: str (the symbol to use instead of the symbol for pi)
    symval: float (numerical value of `symbol')

Returns:
    tuple of a list of labels and an array of values indicated by said labels
'''

    coefficients = np.arange(first, last + step, step)

    labels = []
    for coefficient in coefficients:
        value = fractions.Fraction(coefficient).limit_denominator()
        num = value.numerator
        den = value.denominator

        # case 1: `coefficient' is zero
        if num == 0:
            labels.append(r'$0$')
            continue

        # build a string which has to be appended to `label'
        # Python does not have a string builder data type
        # so, create a list to store the different parts of the string
        # then join those parts
        # this is the fastest way to build a string
        # https://waymoot.org/home/python_string/
        builder = ['$']

        # case 2: `coefficient' is non-zero
        if num < 0:
            builder.append('-')
            num = -num
        if den != 1:
            builder.append(r'\dfrac{')
        if num != 1:
            builder.append(f'{num}')
        builder.append(symbol)
        if den != 1:
            builder.append(f'}}{{{den}}}')
        builder.append('$')
        labels.append(''.join(builder))

    return labels, symval * coefficients

###############################################################################

class CustomPlot:
    '''\
A class to easily plot two- and three-dimensional graphs.

Attributes:
    dim: str (dimension of the plot, either '2d' or '3d')
    aspect_ratio: float (ratio of scales on axes)
    fig: matplotlib.figure.Figure (figure to contain the plot)
    ax: matplotlib.axes._subplots.AxesSubplot (if `dim' is '2d') or
        matplotlib.axes._subplots.Axes3DSubplot (if `dim' is '3d')
        (axes object for the graph plot)

Methods:
    __init__
    __repr__
    __str__
    plot: wrapper for the actual plot function provided by matplotlib
    configure: spice up the plot to make it more complete
    axis_fix: modify the ticks and labels on the axes so they look nice
'''

    ########################################

    def __init__(self, dim = '2d', aspect_ratio = 0):
        if dim == '2d':
            # plt.style.use(['classic', 'seaborn-poster'])
            plt.style.use(['bmh', 'seaborn-poster', 'candy.mplstyle'])
        elif dim == '3d':
            plt.style.use('classic')
        else:
            raise ValueError('Member \'dim\' of class \'CustomPlot\' must be either \'2d\' or \'3d\'.')

        self.dim = dim
        self.aspect_ratio = aspect_ratio
        self.fig = plt.figure()
        if dim == '2d':
            self.ax = self.fig.add_subplot(1, 1, 1)
        else:
            self.ax = self.fig.add_subplot(1, 1, 1, projection = '3d')

        self.fig.canvas.set_window_title(f'graph_{int(time.time())}')

    ########################################

    def __repr__(self):
        return (f'CustomPlot(dim = \'{self.dim}\', aspect_ratio = {self.aspect_ratio})')

    ########################################

    def __str__(self):
        return (f'CustomPlot(dim = \'{self.dim}\', aspect_ratio = {self.aspect_ratio})')

    ########################################

    def plot(self, *args, **kwargs):
        '''\
Wrapper for plotting a graph.

If the arguments are lists or arrays containing a large number of items,
vertical lines at points of discontinuity are removed. Else, the arguments are
left unchanged. Then, these arguments get passed to the function which actually
plots the graph.

Args:
    args
    kwargs

Returns:
    None
'''

        try:
            if len(args[0]) > 1000:
                args = tuple(sanitise_discontinuous(arg) for arg in args)
        except TypeError:
            pass
        finally:
            self.ax.plot(*args, **kwargs)

    ########################################

    def configure(self, axis_labels = (r'$x$', r'$y$', r'$z$'), title = None):
        '''\
Do makeup.

Args:
    axis_labels: tuple (strings to use to label the coordinate axes
    title: str (title of the graph)

Returns:
    None
'''

        # whether the scale should be the same on the coordinate axes
        # currently, because of a library bug, this works only in '2d'
        if self.aspect_ratio != 0 and self.dim == '2d':
            self.ax.set_aspect(aspect = self.aspect_ratio, adjustable = 'box')

        self.ax.legend(loc = 'best')
        self.ax.set_xlabel(axis_labels[0])
        self.ax.set_ylabel(axis_labels[1])
        if self.dim == '3d':
            self.ax.set_zlabel(axis_labels[2])
        if title is not None:
            self.ax.set_title(title)

        # if this is a '2d' plot, draw thick coordinate axes
        # this does not work as expected in '3d'
        if self.dim == '2d':
            kwargs = {'alpha': 0.6, 'linewidth': 1.2, 'color': 'gray'}
            self.ax.axhline(**kwargs)
            self.ax.axvline(**kwargs)

        # enable grid
        # minor grid takes too much memory in '3d' plot
        self.ax.grid(b = True, which = 'major', linewidth = 0.8)
        if self.dim == '2d':
            self.ax.grid(b = True, which = 'minor', linewidth = 0.2)
            self.ax.minorticks_on()

    ########################################

    def axis_fix(self, axis          = None,
                       trigonometric = False,
                       s             = r'\pi',
                       v             = np.pi,
                       first         = None,
                       last          = None,
                       step          = None):
        '''\
Modify the labels and ticks on the specified axis of coordinates. Note that the
limits on the axis must necessarily be set after setting the axis ticks. This
is because floating point precision issues might introduce an extra tick beyond
the last point (`last') to be displayed. This extra tick is eliminated by
simply specifying in the axis limit that the axis must end at `last'.

Args:
    axis: str (which axis to modify: 'x', 'y' or 'z')
    trigonometric: bool (whether ticks are at rational multiples of `v')
    s: str (symbol to use instead of the symbol for pi)
    v: float (numerical value of `s')
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
            ticks_set_function  = self.ax.set_xticks
        elif axis == 'y':
            limits_set_function = self.ax.set_ylim
            labels_get_function = self.ax.get_yticklabels
            labels_set_function = self.ax.set_yticklabels
            ticks_set_function  = self.ax.set_yticks
        elif axis == 'z' and self.dim == '3d':
            limits_set_function = self.ax.set_zlim
            labels_get_function = self.ax.get_zticklabels
            labels_set_function = self.ax.set_zticklabels
            ticks_set_function  = self.ax.set_zticks
        else:
            return

        # case 1: grid lines at rational multiples of `v'
        if trigonometric:
            if None in {first, last, step}:
                raise ValueError('When \'trigonometric\' is True, \'first\', \'last\' and \'step\' must not be None.')

            labels, ticks = graph_ticks(first, last, step, s, v)
            ticks_set_function(ticks)
            labels_set_function(labels)
            limits_set_function(v * first, v * last)
            return

        # case 2: grid lines at the values provided in the arguments
        if None not in {first, last, step}:
            ticks_set_function(np.arange(first, last + step, step))
        if None not in {first, last}:
            limits_set_function(first, last)
        self.fig.canvas.draw()
        labels_set_function([f'${t.get_text()}$' for t in labels_get_function()])

###############################################################################

def main():
    if len(sys.argv) < 2:
        dimension = '2d'
    else:
        dimension = sys.argv[1]
    grapher = CustomPlot(dim = dimension, aspect_ratio = 1)

    ########################################

    t = np.linspace(-np.pi, np.pi, 100000)
    x1 = np.linspace(-32, 32, 100000)
    y1 = np.sin(x1) + np.cos(x1)
    z1 = np.sin(x1)
    grapher.plot(x1, y1, color = 'red', label = r'$y=\sin\,x+\cos\,x$')
    # grapher.plot(0, 0, linestyle = ':', marker = 'o', markerfacecolor = 'none', markeredgecolor = 'red', markersize = 4, fillstyle = 'none')
    # grapher.ax.text(1.1, 1.8, r'$(a,2a)$')

    x2 = np.linspace(-32, 32, 100000)
    y2 = np.floor(y1)
    z2 = np.sin(x2)
    grapher.plot(x2, y2, color = 'blue', label = r'$y=\lfloor\sin\,x+\cos\,x\rfloor$')
    # grapher.plot(1, 0, 'k.')
    # grapher.ax.text(1.1, 0.1, r'$(a,0)$')

    x3 = np.linspace(-32, 32, 100000)
    y3 = y1 + y2
    z3 = np.sin(x3)
    # grapher.plot(x3, y3, color = 'green', label = r'$y=|x|+|x-1|$')
    # grapher.plot(0, 0, 'k.')
    # grapher.ax.text(-0.5, -0.2, r'$(0,0)$')

    # x4 = np.linspace(-32, 32, 100000)
    # y4 = x4 / 8
    # z4 = np.sin(x4)
    # grapher.plot(x4, y4, color = 'purple', label = r'$8x-y=0$')
    # grapher.plot(1, 2, 'k.')
    # grapher.ax.text(1.1, 1.8, r'$(a,2a)$')

    # grapher.ax.fill_between(x1, y1, y2,
    #                         facecolor = 'cyan',
    #                         linewidth = 0,
    #                         label     = r'$R$',
    #                         where     = [True
    #                                      if 0 < i < np.pi / 4 else False
    #                                      for i in x1])
    # grapher.ax.fill_between(x1, y1, y3,
    #                         facecolor = 'cyan',
    #                         linewidth = 0,
    #                         label     = r'',
    #                         where     = [True
    #                                      if 1 < i < 2 else False
    #                                      for i in x1])
    # grapher.ax.fill_between(x1, y1, 0,
    #                         facecolor = 'cyan',
    #                         linewidth = 0,
    #                         label     = r'$R$',
    #                         where     = [True
    #                                      if i < 0 else False
    #                                      for i in x1])
    # grapher.ax.fill_between(x2, y2, -4, facecolor = 'cyan',
    #                                     linewidth = 0)

    grapher.configure(axis_labels = (r'$x$', r'$y$', r'$z$'), title = None)
    grapher.axis_fix(axis          = 'x',
                     trigonometric = True,
                     s             = r'\pi',
                     v             = np.pi,
                     first         = -2,
                     last          = 2,
                     step          = 1 / 4)
    grapher.axis_fix(axis          = 'y',
                     trigonometric = False,
                     s             = r'\pi',
                     v             = np.pi,
                     first         = -3,
                     last          = 3,
                     step          = 1)
    grapher.axis_fix(axis          = 'z',
                     trigonometric = False,
                     s             = r'\pi',
                     v             = np.pi,
                     first         = -10,
                     last          = 10,
                     step          = 2)
    # grapher.ax.set_xticklabels([r'$\mu-4\sigma$', r'$\mu-3\sigma$', r'$\mu-2\sigma$', r'$\mu-\sigma$', r'$\mu$', r'$\mu+\sigma$', r'$\mu+2\sigma$', r'$\mu+3\sigma$', r'$\mu+4\sigma$'])
    # grapher.ax.set_yticklabels([r'$-\dfrac{0.1}{\sigma}$', r'$0$', r'$\dfrac{0.1}{\sigma}$', r'$\dfrac{0.2}{\sigma}$', r'$\dfrac{0.3}{\sigma}$', r'$\dfrac{0.4}{\sigma}$', r'$\dfrac{0.5}{\sigma}$', r'$\dfrac{0.5}{\sigma}$'])
    grapher.fig.tight_layout(pad = 3)
    plt.show()

###############################################################################

if __name__ == '__main__':
    main()

