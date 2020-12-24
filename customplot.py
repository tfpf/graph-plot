#! /usr/local/bin/python3.8 -B

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

matplotlib.rcParams['figure.dpi']          = 120
matplotlib.rcParams['savefig.dpi']         = 200
matplotlib.rcParams['savefig.format']      = 'png'
matplotlib.rcParams['savefig.directory']   = '/mnt/c/Users/vpaij/Pictures/'
matplotlib.rcParams['savefig.orientation'] = 'portrait'

###############################################################################

def show_nice_list(items, columns = 3, align = 'center'):
    '''\
Display a list in neat columns.

Args:
    items: iterable (each of its elements must have an `__str__' method)
    columns: int (number of columns to arrange `items' in)
    align: str ('ljust' for left, 'center' for centre, 'rjust' for right)
'''

    # convert iterable into a two-dimensional list
    items = [str(item) for item in items]
    if len(items) % columns != 0:
        items.extend([''] * (columns - len(items) % columns))
    rows = len(items) // columns
    items = [items[i : i + columns] for i in range(0, len(items), columns)]

    # calculate the required width of all columns
    # width of a column is width of longest string in that column
    widths = [2 + max([len(row[i]) for row in items]) for i in range(columns)]
    for row in items:
        for r, width in zip(row, widths):
            print(getattr(r, align)(width, ' '), end = '', flush = True)
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
    points_of_discontinuity = np.abs(np.r_[[0], np.diff(y)]) > 50
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

    # pre-allocate space for the list because its length is known
    # this is approximately twice as fast as appending repeatedly
    labels = [None] * len(coefficients)

    for i, coefficient in enumerate(coefficients):
        value = fractions.Fraction(coefficient).limit_denominator()
        num = value.numerator
        den = value.denominator

        # case 1: `coefficient' is zero
        if num == 0:
            labels[i] = '$0$'
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
            num = abs(num)
        if den != 1:
            builder.append(r'\dfrac{')
        if num != 1:
            builder.append(f'{num}')
        builder.append(symbol)
        if den != 1:
            builder.append(f'}}{{{den}}}')
        builder.append('$')
        labels[i] = ''.join(builder)

    return labels, symval * coefficients

###############################################################################

class CustomPlot:
    '''\
A class to easily plot two- and three-dimensional line graphs.

Attributes:
    dim: str ('2d' for two-dimensional plots, '3d' for three-dimensional plots)
    aspect_ratio: float (ratio of scales on the coordinate axes)
    fig: Matplotlib figure instance
    ax: Matplotlib subplot axes instance

Methods:
    __init__
    __repr__
    __str__
    plot: wrapper for the actual plot function provided by Matplotlib
    configure: do makeup
    axis_fix: modify the ticks and labels on the axes so they look nice
'''

    ########################################

    def __init__(self, dim = '2d', aspect_ratio = 0):
        if dim not in {'2d', '3d'}:
            raise ValueError('Member \'dim\' of class \'CustomPlot\' must be either \'2d\' or \'3d\'.')

        # the figure has been created after applying the plot style
        # this is necessary for the plot style to get applied correctly
        if dim == '2d':
            # plt.style.use(['classic', 'seaborn-poster'])
            plt.style.use(['bmh', 'seaborn-poster', 'candy.mplstyle'])
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(1, 1, 1)
        else:
            plt.style.use('classic')
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(1, 1, 1, projection = '3d')

        self.dim = dim
        self.aspect_ratio = aspect_ratio
        self.fig.canvas.set_window_title(f'graph_{int(time.time())}')

    ########################################

    def __repr__(self):
        return (f'CustomPlot(dim=\'{self.dim}\', aspect_ratio={self.aspect_ratio})')

    ########################################

    def __str__(self):
        return (f'CustomPlot(dim=\'{self.dim}\', aspect_ratio={self.aspect_ratio})')

    ########################################

    def plot(self, *args, **kwargs):
        '''\
Wrapper for plotting a graph.

If the arguments are lists or arrays containing a large number of items,
vertical lines at points of discontinuity are removed. Else, the arguments are
left unchanged. Then, these arguments get passed to the function which actually
plots the graph.
'''

        try:
            if len(args[0]) > 1000:
                args = tuple(sanitise_discontinuous(arg) for arg in args)
        except TypeError:
            pass
        finally:
            self.ax.plot(*args, **kwargs)

    ########################################

    def configure(self, axis_labels = ('$x$', '$y$', '$z$'), title = None):
        '''\
Do makeup.

Args:
    axis_labels: tuple (strings to use to label the coordinate axes
    title: str (title of the graph)
'''

        # set the relative scale of the coordinate axes
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

        # if this is a two-dimensional plot, draw thick coordinate axes
        # this does not work as expected in three-dimensional plots
        if self.dim == '2d':
            kwargs = {'alpha': 0.6, 'linewidth': 1.2, 'color': 'gray'}
            self.ax.axhline(**kwargs)
            self.ax.axvline(**kwargs)

        # enable grid
        # minor grid takes too much memory in three-dimensional plots
        self.ax.grid(b = True, which = 'major', linewidth = 0.8)
        if self.dim == '2d':
            self.ax.grid(b = True, which = 'minor', linewidth = 0.2)
            self.ax.minorticks_on()

    ########################################

    def axis_fix(self, axis = None, symbolic = False, s = r'\pi', v = np.pi, first = None, last = None, step = None):
        '''\
Modify the labels and ticks on the specified axis of coordinates. Note that the
limits on the axis must necessarily be set after setting the axis ticks. This
is because floating point precision issues might introduce an extra tick beyond
the last point (`last') to be displayed. This extra tick is eliminated by
simply specifying in the axis limit that the axis must end at `last'.

Args:
    axis: str (which axis to modify: 'x', 'y' or 'z')
    symbolic: bool (whether ticks are at rational multiples of `v')
    s: str (symbol to use instead of the symbol for pi)
    v: float (numerical value of `s')
    first: float (grid start point)
    last: float (grid end point)
    step: float (grid gap)
'''

        if axis == 'z' and self.dim == '2d':
            return

        limits_set_function = getattr(self.ax, f'set_{axis}lim')
        labels_get_function = getattr(self.ax, f'get_{axis}ticklabels')
        labels_set_function = getattr(self.ax, f'set_{axis}ticklabels')
        ticks_set_function  = getattr(self.ax, f'set_{axis}ticks')

        # case 1: grid lines at rational multiples of `v'
        if symbolic:
            if None in {first, last, step}:
                raise ValueError('When \'symbolic\' is True, \'first\', \'last\' and \'step\' must not be None.')

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
    try:
        dimension = sys.argv[1]
    except IndexError:
        dimension = '2d'

    grapher = CustomPlot(dim = dimension, aspect_ratio = 1 / 1)

    ########################################

    t = np.linspace(-np.pi, np.pi, 100000)
    x1 = np.linspace(-32, 32, 100000)
    y1 = x1 * np.cos(x1) ** 2 / np.sin(x1)
    z1 = np.sin(x1)
    grapher.plot(x1, y1, color = 'red', label = r'$y=\dfrac{x\,\cos^2x}{\sin\,x}$')
    # grapher.plot([2 * np.cos(i * np.pi / 8) for i in range(1, 14, 4)], [2 * np.sin(i * np.pi / 8) for i in range(1, 14, 4)], linestyle = 'none', marker = 'o', markerfacecolor = 'black', markeredgecolor = 'black', markersize = 4, fillstyle = 'none', label = r'$z^4=16i$')
    # grapher.ax.text(0.83, 0.739, r'$(0.739,0.739)$')

    # x2 = np.linspace(-32, 32, 100000)
    # y2 = x2
    # z2 = np.sin(x2)
    # grapher.plot(x2, y2, color = 'blue', label = r'$y=x$')

    # x3 = np.linspace(0, 32, 100000)
    # y3 = x3
    # z3 = np.sin(x3)
    # grapher.plot(x3, y3, color = 'green', label = r'$y=\dfrac{1}{x}$')

    # x4 = np.linspace(-32, 32, 100000)
    # y4 = x4 / 8
    # z4 = np.sin(x4)
    # grapher.plot(x4, y4, color = 'purple', label = r'$8x-y=0$')

    # grapher.ax.fill_between(x1, y1, 0,  facecolor = 'cyan', linewidth = 0, label = '$R$', where = [True if i < 0 else False for i in x1])
    # grapher.ax.fill_between(x1, y1, y3, facecolor = 'cyan', linewidth = 0, label = '',    where = [True if 1 < i < 2 else False for i in x1])
    # grapher.ax.fill_between(x1, y1, 0,  facecolor = 'cyan', linewidth = 0, label = '$R$', where = [True if i < 0 else False for i in x1])

    grapher.configure(axis_labels = ('$x$', '$y$', '$z$'), title = None)
    grapher.axis_fix(axis     = 'x',
                     symbolic = True,
                     s        = r'\pi',
                     v        = np.pi,
                     first    = -2,
                     last     = 2,
                     step     = 1 / 4)
    grapher.axis_fix(axis     = 'y',
                     symbolic = False,
                     s        = r'\pi',
                     v        = np.pi,
                     first    = -3,
                     last     = 3,
                     step     = 1)
    grapher.axis_fix(axis     = 'z',
                     symbolic = False,
                     s        = r'\pi',
                     v        = np.pi,
                     first    = -10,
                     last     = 10,
                     step     = 2)
    # grapher.ax.set_xticklabels([r'$\mu-4\sigma$', r'$\mu-3\sigma$', r'$\mu-2\sigma$', r'$\mu-\sigma$', r'$\mu$', r'$\mu+\sigma$', r'$\mu+2\sigma$', r'$\mu+3\sigma$', r'$\mu+4\sigma$'])
    # grapher.ax.set_yticklabels([r'$0$', r'$\dfrac{0.1}{\sigma}$', r'$\dfrac{0.2}{\sigma}$', r'$\dfrac{0.3}{\sigma}$', r'$\dfrac{0.4}{\sigma}$'])
    grapher.fig.tight_layout(pad = 2)
    plt.show()

###############################################################################

if __name__ == '__main__':
    main()

