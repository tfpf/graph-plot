#! /usr/local/bin/python3.8 -B

import fractions
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import time

# GUI and non-GUI backends for Matplotlib
# print(mpl.rcsetup.interactive_bk)
# print(mpl.rcsetup.non_interactive_bk)
mpl.use('TkAgg')

mpl.rcParams['figure.dpi']          = 120
mpl.rcParams['savefig.dpi']         = 200
mpl.rcParams['savefig.format']      = 'png'
mpl.rcParams['savefig.directory']   = '/mnt/c/Users/vpaij/Pictures/'
mpl.rcParams['savefig.orientation'] = 'portrait'

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
At a point of jump discontinuity, a vertical line is drawn automatically. This
vertical line joins the two points around the point of discontinuity.
Traditionally, in maths, these vertical lines are not drawn. Hence, they need
to be removed from the plot. This is achieved by setting the values at the
points of discontinuity to NaN.

Args:
    y: iterable (values of the discontinuous function)

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
Create a list of tick values and labels at intervals of `step * np.pi'.

>>> graph_ticks(-1, 5, 2)
(['$-\\pi$', '$\\pi$', '$3\\pi$', '$5\\pi$'], array([-3.14159265,  3.14159265,  9.42477796, 15.70796327]))
>>> graph_ticks(-1, -1 / 4, 1 / 4)
(['$-\\pi$', '$-\\dfrac{3\\pi}{4}$', '$-\\dfrac{\\pi}{2}$', '$-\\dfrac{\\pi}{4}$'], array([-3.14159265, -2.35619449, -1.57079633, -0.78539816]))
>>> graph_ticks(-2, 2, 1)
(['$-2\\pi$', '$-\\pi$', '$0$', '$\\pi$', '$2\\pi$'], array([-6.28318531, -3.14159265,  0.        ,  3.14159265,  6.28318531]))

The above results can be verified by using the `doctest' module. To properly
represent the output so that `doctest' may correctly read them, this docstring
has been marked as a raw string.

What's required is a list of LaTeX-formatted strings for numbers going from one
rational multiple of pi to another, and an `np.array' of the respective values.

Args:
    first: float (first item in the returned array shall be `first * symval')
    last: float (last item in the returned array shall be `last * symval')
    step: float (array items will increment in steps of `step * symval')
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
    plot: wrapper for the actual plot function provided by Matplotlib
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

        # the figure has to be created after setting the plot style
        # this is necessary for the plot style to get applied correctly
        if xkcd:
            plt.xkcd()
        else:
            plt.style.use('candy.mplstyle')
        self.fig = plt.figure()

        if polar:
            self.ax = self.fig.add_subplot(1, 1, 1, projection = 'polar')
        elif dim == 2:
            self.ax = self.fig.add_subplot(1, 1, 1)
        else:
            self.ax = self.fig.add_subplot(1, 1, 1, projection = '3d')
            self.ax.tick_params(axis = 'both', labelsize = 'small', pad = 1)
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
        return (f'CustomPlot(dim={self.dim}, polar={self.polar}, xkcd={self.xkcd})')

    ########################################

    def plot(self, *args, **kwargs):
        '''\
Wrapper for plotting a graph.

If the arguments are lists or arrays containing a large number of items,
vertical lines at points of discontinuity are removed. Else, the arguments are
left unchanged. Then, these arguments get passed to the function which actually
plots the graph. Hence, the signature of this function is the same as that of
the `plot' function of Matplotlib.
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
Do makeup.

Args:
    axis_labels: tuple (strings to use to label the coordinate axes
    title: str (title of the graph)
'''

        kwargs = {'loc': 'best'}
        if self.polar or self.dim == 3:
            kwargs['facecolor'] = 'lightgray'
        self.ax.legend(**kwargs)
        self.ax.set_xlabel(axis_labels[0])
        if self.polar:
            self.ax.set_ylabel(axis_labels[1], rotation = 0)
        else:
            self.ax.set_ylabel(axis_labels[1])
        if self.polar:
            R = self.ax.get_ylim()[1] * 1.5
            kwargs = {'arrowstyle': 'Simple, tail_width = 0.5, head_width = 4, head_length = 8', 'clip_on': False}
            angular = mpl.patches.FancyArrowPatch((-0.1, R), (0.1, R), connectionstyle = 'arc3, rad = 0.15', **kwargs)
            self.ax.add_patch(angular)
            self.ax.xaxis.set_label_coords(0.11, 1.03 * R, transform = self.ax.transData)
            radial = mpl.patches.FancyArrowPatch((0, 0.95 * R), (0, 1.05 * R), **kwargs)
            self.ax.add_patch(radial)
            self.ax.yaxis.set_label_coords(-0.01, 1.06 * R, transform = self.ax.transData)
        if self.dim == 3:
            self.ax.set_zlabel(axis_labels[2])
        if title is not None:
            self.ax.set_title(title)

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

        # this will not work if the user plots a polar graph in XKCD style
        # hence, wrapping it in a `try' block
        if self.xkcd:
            try:
                self.ax.spines['right'].set_color('none')
                self.ax.spines['top'].set_color('none')
                self.ax.xaxis.set_ticks_position('bottom')
            except KeyError:
                pass

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

        if self.xkcd or axis == 'z' and self.dim == 2:
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

            # if this is a polar plot, ignore the last label and tick
            # this is because an angle of 0 is the same as an angle of 2pi
            if self.polar:
                if axis == 'x':
                    labels, ticks = labels[: -1], ticks[: -1]
                else:
                    labels[0] = labels[-1] = ''
            ticks_set_function(ticks)
            labels_set_function(labels)
            limits_set_function(v * first, v * last)

        # case 2: grid lines at the values provided in the arguments
        else:
            if None not in {first, last, step}:
                ticks_set_function(np.arange(first, last + step, step))
            if None not in {first, last}:
                limits_set_function(first, last)
            self.fig.canvas.draw()

            # if this is a polar plot, the angular axis labels contain the degree symbol
            # hence, remove it and add LaTeX's own degree symbol
            labels = [l.get_text() for l in labels_get_function()]
            if self.polar and axis == 'x':
                labels = [f'${l[: -1]}' r'^{\circ}$' for l in labels]
            else:
                labels = [f'${l}$' for l in labels]
            if self.polar and axis == 'y':
                labels[0] = labels[-1] = ''
            labels_set_function(labels)

    ########################################

    def aspect_fix(self, aspect_ratio):
        '''\
Set the aspect ratio of the axes object. If this is a two-dimensional Cartesian
plot, the ratio of the scales on the axes will be set to the given value (if it
is non-zero). If this is two-dimensional polar plot, or if this is an XKCD-style
plot, nothing happens.

For three-dimensional plots, an aspect ratio does not make sense, because there
are three axes. Hence, in this case, the scales on the axes will be made equal
if the given value is non-zero.
'''

        if aspect_ratio != 0 and not self.polar and not self.xkcd:
            if self.dim == 2:
                self.ax.set_aspect(aspect = aspect_ratio, adjustable = 'box')
            else:
                limits = np.array([getattr(self.ax, f'get_{axis}lim')() for axis in 'xyz'])
                self.ax.set_box_aspect(np.ptp(limits, axis = 1))

###############################################################################

def main():
    grapher = CustomPlot(dim = 2, polar = True, xkcd = False)
    grapher.axis_fix(axis     = 'x',
                     symbolic = True,
                     s        = r'\pi',
                     v        = np.pi,
                     first    = 0,
                     last     = 2,
                     step     = 1 / 8)
    grapher.axis_fix(axis     = 'y',
                     symbolic = False,
                     s        = r'\pi',
                     v        = np.pi,
                     first    = 0,
                     last     = 4,
                     step     = 1)
    grapher.axis_fix(axis     = 'z',
                     symbolic = False,
                     s        = r'\pi',
                     v        = np.pi,
                     first    = -2,
                     last     = 2,
                     step     = 1)

    t = np.linspace(-np.pi, np.pi, 100000)
    x1 = np.linspace(0, 2 * np.pi, 100000)
    y1 = 1 - np.cos(x1)
    z1 = x1
    grapher.plot(x1, y1, color = 'red', label = r'$r=1-\cos\,\theta$')
    # grapher.plot(range(-8, 9), [2] * 17, linestyle = 'none', marker = 'o', markerfacecolor = 'white', markeredgecolor = 'blue', markersize = 4, fillstyle = 'none', label = r'')
    # grapher.ax.text(0.83, 0.739, r'$(0.739,0.739)$')

    # x2 = np.linspace(-32, 32, 100000)
    # y2 = np.tan(x2) + 1 / np.cos(x2)
    # z2 = np.sin(x2)
    # grapher.plot(x2, y2, color = 'blue', label = r'$y=\tan\,x+\sec\,x$')

    # x3 = np.linspace(0, 32, 100000)
    # y3 = x3
    # z3 = np.sin(x3)
    # grapher.plot(x3, y3, color = 'green', label = r'$y=\dfrac{1}{x}$')

    # x4 = np.linspace(-32, 32, 100000)
    # y4 = x4 / 8
    # z4 = np.sin(x4)
    # grapher.plot(x4, y4, color = 'purple', label = r'$8x-y=0$')

    grapher.ax.fill_between(x1, y1, 0,  facecolor = 'cyan', linewidth = 0, label = '')
    # grapher.ax.fill_between(x1, y1, y3, facecolor = 'cyan', linewidth = 0, label = '$R$', where = [True if 1 < i < 2 else False for i in x1])
    # grapher.ax.fill_between(x1, y1, 0,  facecolor = 'cyan', linewidth = 0, label = '$R$', where = [True if i < 0 else False for i in x1])

    # X, Y = np.meshgrid(np.linspace(-8, 8, 1000), np.linspace(-8, 8, 1000))
    # Z = np.abs(X) + np.abs(Y)
    # surf = grapher.ax.plot_surface(X, Y, Z, linewidth = 0, color = 'skyblue', antialiased = True, label = r'$z=|x|+|y|$')
    # surf._facecolors2d = None
    # surf._edgecolors2d = None
    # grapher.fig.colorbar(surf, shrink = 0.5, aspect = 5)

    grapher.configure(axis_labels = (r'$\theta$', r'$r$', r'$z$'), title = None)
    grapher.aspect_fix(1)
    # grapher.ax.set_xticklabels([r'$\mu-4\sigma$', r'$\mu-3\sigma$', r'$\mu-2\sigma$', r'$\mu-\sigma$', r'$\mu$', r'$\mu+\sigma$', r'$\mu+2\sigma$', r'$\mu+3\sigma$', r'$\mu+4\sigma$'])
    # grapher.ax.set_yticklabels([r'$0$', r'$\dfrac{0.1}{\sigma}$', r'$\dfrac{0.2}{\sigma}$', r'$\dfrac{0.3}{\sigma}$', r'$\dfrac{0.4}{\sigma}$'])
    grapher.fig.tight_layout(pad = 2)
    plt.show()
    plt.close(grapher.fig)

###############################################################################

if __name__ == '__main__':
    main()

