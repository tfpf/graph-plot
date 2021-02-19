#! /usr/local/bin/python3.8 -B

import fractions
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import time

###############################################################################

def show_nice_list(items, columns = 3, align_method = 'center'):
    '''\
Display a list in neat columns.

Args:
    items: iterable (each of its elements must have an `__str__' method)
    columns: int (number of columns to arrange `items' in)
    align_method: str (string method name: 'ljust', 'center' or 'rjust')
'''

    # convert iterable into a two-dimensional list
    items = [str(item) for item in items]
    if len(items) % columns != 0:
        items.extend([''] * (columns - len(items) % columns))
    items = [items[i : i + columns] for i in range(0, len(items), columns)]

    # calculate the required width of all columns
    # width of a column is width of longest string in that column plus padding
    widths = [max(len(row[i]) for row in items) + 2 for i in range(columns)]

    for row in items:
        for r, width in zip(row, widths):
            print(getattr(r, align_method)(width, ' '), end = '')
        print()

###############################################################################

def sanitise_discontinuous(y):
    '''\
At a point of essential or jump discontinuity, Matplotlib draws a vertical line
automatically. This vertical line joins the two points around the
discontinuity. Traditionally, in maths, such lines are not drawn. Hence, they
need to be removed from the plot. This is achieved by setting the function
values at the points of discontinuity to NaN.

Args:
    y: iterable (values of the discontinuous function)

Returns:
    np.array with NaN at the points of discontinuity
'''

    # locate points of discontinuity (check where the derivative is large)
    maximum_diff = 5
    y = np.array(y)
    points_of_discontinuity = np.abs(np.r_[[0], np.diff(y)]) > maximum_diff
    y[points_of_discontinuity] = np.nan

    return y

###############################################################################

def graph_ticks(first, last, step, symbol = r'\pi', symval = np.pi):
    r'''
Create a list of LaTeX-formatted strings and an array of floats for values
from one rational multiple of π to another.

>>> graph_ticks(-1, 5, 2)
(['$-\\pi$', '$\\pi$', '$3\\pi$', '$5\\pi$'], array([-3.14159265,  3.14159265,  9.42477796, 15.70796327]))
>>> graph_ticks(-1, -1 / 4, 1 / 4)
(['$-\\pi$', '$-\\dfrac{3\\pi}{4}$', '$-\\dfrac{\\pi}{2}$', '$-\\dfrac{\\pi}{4}$'], array([-3.14159265, -2.35619449, -1.57079633, -0.78539816]))
>>> graph_ticks(-2, 2, 1)
(['$-2\\pi$', '$-\\pi$', '$0$', '$\\pi$', '$2\\pi$'], array([-6.28318531, -3.14159265,  0.        ,  3.14159265,  6.28318531]))

Args:
    first: float (first item in the returned array shall be `first * symval')
    last: float (last item in the returned array shall be `last * symval')
    step: float (array items will increment in steps of `step * symval')
    symbol: str (LaTeX code of the symbol to use instead of π)
    symval: float (numerical value represented by `symbol')

Returns:
    tuple of a list of labels and an array of values indicated by said labels
'''

    coefficients = np.arange(first, last + step / 2, step)

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
        # I found that this is faster than repeated string concatenation
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
A wrapper around Matplotlib to plot publication-quality graphs.

Attributes:
    dim: int (2 for two-dimensional plots, 3 for three-dimensional plots)
    polar: bool (whether the plot is polar or Cartesian)
    xkcd: bool (whether to use the XKCD style or not)
    fig: Matplotlib figure instance
    ax: Matplotlib subplot axes instance

Methods:
    __init__
    __repr__
    __str__
    plot: wrapper around the `plot' method of `ax'
    configure: do makeup
    axis_fix: modify the ticks and labels on the axes so they look nice
    aspect_fix: set the aspect ratio
'''

    ########################################

    def __init__(self, dim = 2, polar = False, xkcd = False):
        if dim not in {2, 3}:
            raise ValueError('Member \'dim\' of class \'CustomPlot\' must be either 2 or 3.')

        if polar and dim != 2:
            raise ValueError('Member \'dim\' of class \'CustomPlot\' must be 2 if \'polar\' is True.')

        self.fig = plt.figure()
        if polar:
            self.ax = self.fig.add_subplot(1, 1, 1, projection = 'polar')
        elif dim == 2:
            self.ax = self.fig.add_subplot(1, 1, 1)
        else:
            self.ax = self.fig.add_subplot(1, 1, 1, projection = '3d')
            kwargs = {'which':     'major',
                      'labelsize': 'small',
                      'length':    4,
                      'direction': 'in'}
            self.ax.tick_params(axis = 'x', pad = 1, **kwargs)
            self.ax.tick_params(axis = 'y', pad = 1, **kwargs)
            self.ax.tick_params(axis = 'z', pad = 1, **kwargs)
            self.ax.set_facecolor('white')

        self.dim = dim
        self.polar = polar
        self.xkcd = xkcd

        self.fig.canvas.set_window_title(f'graph_{int(time.time())}')

    ########################################

    def __repr__(self):
        return (f'CustomPlot(dim={self.dim}, polar={self.polar}, xkcd={self.xkcd})')

    ########################################

    def __str__(self):
        return (f'<CustomPlot object at {hex(id(self))}>')

    ########################################

    def plot(self, *args, **kwargs):
        '''\
Plot a graph.

This method does the same thing as the `plot' function of Pyplot (`plt.plot'),
but with one small difference: if the arguments are lists or arrays containing
a large number of items, vertical lines at points of discontinuity are removed
(else, the arguments are left unchanged).

The signature of this method is the same as that of the `plot' function of
Pyplot.
'''

        try:
            if len(args[0]) > 1000 and not self.xkcd:
                args = tuple(sanitise_discontinuous(arg) for arg in args)
        except TypeError:
            pass
        finally:
            self.ax.plot(*args, **kwargs)

    ########################################

    def configure(self, axis_labels = ('$x$', '$y$', '$z$'), title = None):
        '''\
Label the coordinate axes. Give the plot a title. Add a legend. Draw grid
lines.

Args:
    axis_labels: tuple (strings to use to label the coordinate axes)
    title: str (title of the graph)
'''

        # axis labels
        # in three-dimensional plots, the axis labels and tick labels overlap
        # hence, a blank line is added before each axis label
        if self.dim == 2:
            self.ax.set_xlabel(axis_labels[0])
            if self.polar:
                self.ax.set_ylabel(axis_labels[1], rotation = 0)
            else:
                self.ax.set_ylabel(axis_labels[1], rotation = 90)
        else:
            for i, axis in enumerate('xyz'):
                getattr(self.ax, f'set_{axis}label')(f'\n{axis_labels[i]}', linespacing = 3)

        # for polar plots, show a visual of the angular and radial axes
        # this is required because the labels cannot be drawn on the figure
        if self.polar:
            kwargs = {'arrowstyle': 'Simple, tail_width = 0.5, head_width = 4, head_length = 8',
                      'clip_on':    False,
                      'transform':  self.ax.transAxes}
            angular = mpl.patches.FancyArrowPatch((1.3, 0.4), (1.3, 0.6), connectionstyle = 'arc3, rad = 0.15', **kwargs)
            self.ax.add_patch(angular)
            self.ax.xaxis.set_label_coords(1.32, 0.6)
            radial = mpl.patches.FancyArrowPatch((1.25, 0.5), (1.35, 0.5), **kwargs)
            self.ax.add_patch(radial)
            self.ax.yaxis.set_label_coords(1.35, 0.47)
            self.ax.set_rlabel_position(0)

        # main title (this is displayed above the plot)
        if title is not None:
            self.ax.set_title(title)

        # legend
        if self.ax.get_legend_handles_labels() != ([], []):
            kwargs = {'loc': 'best'}
            if self.polar:
                kwargs['bbox_to_anchor'] = (1.3, 1)
            if not self.xkcd and (self.polar or self.dim == 3):
                kwargs['facecolor'] = 'lightgray'
            self.ax.legend(**kwargs)

        # if this is a two-dimensional plot, draw thick coordinate axes
        # this does not work as expected in three-dimensional plots
        if self.dim == 2 and not self.polar and not self.xkcd:
            kwargs = {'alpha': 0.6, 'linewidth': 1.2, 'color': 'gray'}
            self.ax.axhline(**kwargs)
            self.ax.axvline(**kwargs)

        # enable grid
        # minor grid takes too much memory in three-dimensional plots
        if not self.xkcd:
            if self.dim == 2:
                self.ax.grid(b = True, which = 'major', linewidth = 0.8, linestyle = ':')
                self.ax.grid(b = True, which = 'minor', linewidth = 0.1, linestyle = '-')
                self.ax.minorticks_on()
            else:
                self.ax.grid(b = True, which = 'major', linewidth = 0.3, linestyle = '-')

        # remove the top and right borders in case of an XKCD-style plot
        # this will make it resemble Randall Munroe's graphs somewhat
        if self.xkcd and not self.polar:
            self.ax.spines['right'].set_color('none')
            self.ax.spines['top'].set_color('none')
            self.ax.xaxis.set_ticks_position('bottom')

    ########################################

    def axis_fix(self, axis = None, symbolic = False, s = r'\pi', v = np.pi, first = None, last = None, step = None):
        '''\
Set the ticks on the specified axis of coordinates. Limit this axis to the
range of values given.

In three-dimensional plots, these limits are not respected. Matplotlib adds a
small delta to the axis range. (The relevant code can be found in the
`_get_coord_info' method of the three-dimensional axes object in
`mpl_toolkits'.) To have strict axis limits, you must modify the source code.

Args:
    axis: str (which axis to modify: 'x', 'y' or 'z')
    symbolic: bool (whether ticks are at rational multiples of `v')
    s: str (LaTeX code of the symbol to use instead of π)
    v: float (numerical value represented by `s')
    first: float (grid start point)
    last: float (grid end point)
    step: float (grid gap)
'''

        if self.xkcd or axis == 'z' and self.dim == 2:
            return

        labels_getter = getattr(self.ax, f'get_{axis}ticklabels')
        labels_setter = getattr(self.ax, f'set_{axis}ticklabels')
        limits_setter = getattr(self.ax, f'set_{axis}lim')
        ticks_setter  = getattr(self.ax, f'set_{axis}ticks')

        # case 1: grid lines at rational multiples of `v'
        if symbolic:
            if None in {first, last, step}:
                raise ValueError('When \'symbolic\' is True, \'first\', \'last\' and \'step\' must not be None.')

            labels, ticks = graph_ticks(first, last, step, s, v)

            # see if this is a polar plot in which the angle goes from 0 to 2π
            # if yes, do not draw the label for 2π (as it overlaps with 0)
            # further, do not put the first and last labels on the radial axis
            if self.polar:
                if axis == 'x' and first == 0 and last == 2:
                    labels, ticks = labels[: -1], ticks[: -1]
                elif axis == 'y':
                    labels[0] = labels[-1] = ''
            ticks_setter(ticks)
            labels_setter(labels)
            limits_setter(v * first, v * last)

        # case 2: grid lines at the values provided in the arguments
        else:
            if None not in {first, last, step}:
                ticks_setter(np.arange(first, last + step / 2, step))
            if None not in {first, last}:
                limits_setter(first, last)

            # do the same thing as in the `symbolic' case for polar plots
            # i.e. do not put the first and last labels on the radial axis
            self.fig.canvas.draw()
            if self.polar and axis == 'y':
                labels = [l.get_text() for l in labels_getter()]
                labels[0] = labels[-1] = ''
                labels_setter(labels)

    ########################################

    def aspect_fix(self, aspect_ratio):
        '''\
Set the aspect ratio of the axes object. If this is a two-dimensional Cartesian
plot, the ratio of the scales on the axes will be set to the given value (if it
is non-zero). If this is a two-dimensional polar plot, nothing happens.

For three-dimensional plots, an aspect ratio does not make sense, because there
are three axes. Hence, in this case, the scales on the axes will be made equal
if the given value is non-zero.

Args:
    aspect_ratio: float (ratio of x-axis scale to y-axis scale)
'''

        if aspect_ratio != 0 and not self.polar:
            if self.dim == 2:
                self.ax.set_aspect(aspect = aspect_ratio, adjustable = 'box')
            else:
                limits = np.array([getattr(self.ax, f'get_{axis}lim')() for axis in 'xyz'])
                self.ax.set_box_aspect(np.ptp(limits, axis = 1))

###############################################################################

def main():
    mpl.rcParams['savefig.directory'] = '/mnt/c/Users/vpaij/Pictures/'
    plt.style.use('dandy.mplstyle')

    grapher = CustomPlot(dim = 2, polar = False, xkcd = False)
    grapher.axis_fix(axis     = 'x',
                     symbolic = False,
                     s        = r'\pi',
                     v        = np.pi,
                     first    = -6,
                     last     = 6,
                     step     = 1)
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
                     first    = -5,
                     last     = 8,
                     step     = 1)

    # t = np.linspace(0, 2 * np.pi, 10000)
    x1 = np.linspace(-20, 20, 10000)
    y1 = x1 / 2
    z1 = x1
    grapher.plot(x1, y1, color = 'red', label = r'$x-2y=0$')
    # grapher.plot(x1, y1, color = 'red', linestyle = 'none', marker = 'o', label = 'Observed Variation in Refractive Index of Water-Alcohol Mixture')
    # grapher.ax.text(8.05, 0.337, r'equivalence point', size = 'large')

    # x2 = [8, 8.1]
    # y2 = [0.12, 0.27]
    # z2 = x2
    # grapher.plot(x2, y2, color = 'C0', label = r'')

    # x3 = [8.2, 8.3]
    # y3 = [0.25, 0.09]
    # z3 = x3
    # grapher.plot(x3, y3, color = 'C0', label = r'')

    # x4 = [8.1, 8.14, 8.2]
    # y4 = [0.27, 0.33, 0.25]
    # z4 = x4
    # grapher.plot(x4, y4, color = 'C0', linestyle = ':', label = r'')

    # grapher.ax.fill_between(x1, y1, y2, facecolor = 'cyan', linewidth = 0, label = r'$R$')
    # grapher.ax.fill_between(x1, 1, 2, facecolor = 'cyan', linewidth = 0, label = '$R$', where = [True if 0 < i < 0.5 else False for i in x1])
    # grapher.ax.fill_between(x1, y1, 1, facecolor = 'cyan', linewidth = 0, label = '', where = [True if 0.5 < i < 1 else False for i in x1])

    # X, Z = np.meshgrid(np.linspace(0, 4, 100), np.linspace(-3, 3, 100))
    # Y = np.sqrt(4 - (X - 2) ** 2)
    # surf = grapher.ax.plot_surface(X, Y, Z, linewidth = 0, color = '#009F00', shade = False, alpha = 0.9, antialiased = True, label = r'$(x-2)^2+y^2=4$'); surf._facecolors2d = surf._edgecolors2d = None
    # surf = grapher.ax.plot_surface(X, -Y, Z, linewidth = 0, color = '#009F00', shade = False, alpha = 0.9, antialiased = True); surf._facecolors2d = surf._edgecolors2d = None

    # T, P = np.meshgrid(np.linspace(0, np.pi, 100), np.linspace(0, 2 * np.pi, 100))
    # X = 2 * np.cos(T)
    # Y = np.sqrt(2) * np.sin(T) * np.cos(P)
    # Z = 2 * np.sin(T) * np.sin(P)
    # surf = grapher.ax.plot_surface(X, Y, Z, linewidth = 0, color = 'lightgreen', antialiased = True, label = r'$x^2+2y^2+z^2=4$'); surf._facecolors2d = surf._edgecolors2d = None

    # X, Y = np.meshgrid(np.linspace(0, 8, 1000), np.linspace(-5, 5, 1000))
    # Z = np.log(X) - Y
    # Z[Z < -5] = -5
    # surf = grapher.ax.plot_surface(X, Y, Z, linewidth = 0, color = 'skyblue', antialiased = True, label = r'$z=\log\,x-y$'); surf._facecolors2d = surf._edgecolors2d = None
    # grapher.fig.colorbar(surf, shrink = 0.5, aspect = 5)

    grapher.configure(axis_labels = (r'$x$', r'$y$', r'$z$'), title = None)
    grapher.aspect_fix(1)
    # grapher.ax.set_xticklabels([r'$\mu-4\sigma$', r'$\mu-3\sigma$', r'$\mu-2\sigma$', r'$\mu-\sigma$', r'$\mu$', r'$\mu+\sigma$', r'$\mu+2\sigma$', r'$\mu+3\sigma$', r'$\mu+4\sigma$'])
    # grapher.ax.set_yticklabels([r'$0$', r'$\dfrac{0.1}{\sigma}$', r'$\dfrac{0.2}{\sigma}$', r'$\dfrac{0.3}{\sigma}$', r'$\dfrac{0.4}{\sigma}$'])
    grapher.fig.tight_layout(pad = 2)
    plt.show()
    plt.close(grapher.fig)

###############################################################################

if __name__ == '__main__':
    main()

