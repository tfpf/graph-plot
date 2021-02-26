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

def sanitise_discontinuous(y, maximum_diff = 5):
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

def get_ax_size_inches(ax):
    '''\
Obtain the size of a Matplotlib axes instance in inches.

Args:
    ax: Matplotlib axes instance

Returns:
    tuple of the width and height of `ax' in inches
'''

    bbox = ax.get_window_extent().transformed(ax.figure.dpi_scale_trans.inverted())
    return bbox.width, bbox.height

###############################################################################

def limit(ax, coordaxis = None, symbolic = False, s = r'\pi', v = np.pi, first = None, last = None, step = None):
    '''\
Limit the axis of coordinates to the range given. Draw grid lines as specified.

In three-dimensional plots, these limits on the axes of coordinates are not
respected. Matplotlib adds a small delta to the axis range. (The relevant code
can be found in the `_get_coord_info' method of the three-dimensional axes
object in `mpl_toolkits'.) To have strict axis limits, you must modify the
source code.

Args:
    ax: Matplotlib axes instance
    coordaxis: str (which axis of coordinates to limit: 'x', 'y' or 'z')
    symbolic: bool (whether ticks are at rational multiples of `v')
    s: str (LaTeX code of the symbol to use instead of π)
    v: float (numerical value represented by `s')
    first: float (tick start point)
    last: float (tick end point)
    step: float (tick spacing)
'''

    if coordaxis == 'z' and ax.name == 'rectilinear':
        return

    labels_getter = getattr(ax, f'get_{coordaxis}ticklabels')
    labels_setter = getattr(ax, f'set_{coordaxis}ticklabels')
    limits_setter = getattr(ax, f'set_{coordaxis}lim')
    ticks_setter  = getattr(ax, f'set_{coordaxis}ticks')

    # case 1: use symbolic labels
    if symbolic:
        if None in {first, last, step}:
            raise ValueError('When \'symbolic\' is True, \'first\', \'last\' and \'step\' must not be None.')

        labels, ticks = graph_ticks(first, last, step, s, v)

        # in polar plots, the anglular axis may go from 0 to 2π
        # in which case, do not draw the label for 2π (as it overlaps with 0)
        # further, do not put the first and last labels on the radial axis
        if ax.name == 'polar':
            if coordaxis == 'x' and first == 0 and last == 2:
                labels, ticks = labels[: -1], ticks[: -1]
            elif coordaxis == 'y':
                labels[0] = labels[-1] = ''

        ticks_setter(ticks)
        labels_setter(labels)
        limits_setter(v * first, v * last)

    # case 2: allow labels to be set automatically
    else:
        if None not in {first, last, step}:
            ticks_setter(np.arange(first, last + step / 2, step))
        if None not in {first, last}:
            limits_setter(first, last)

        # same as what was done in case 1 for polar plots
        # do not put the first and last labels on the radial axis
        ax.figure.canvas.draw()
        if ax.name == 'polar' and coordaxis == 'y':
            labels = [l.get_text() for l in labels_getter()]
            labels[0] = labels[-1] = ''
            labels_setter(labels)

###############################################################################

def draw_polar_axes_patches(ax, labels):
    '''\
Show the angular and radial coordinate axes of a polar plot using arrow
patches. The sizes of these arrow patches must be independent of the size of
the figure. Hence, this function connected to the resize event of the
appropriate Matplotlib figure instance. It is called automatically when the
figure is resized, and previously added patches are removed before adding new
ones.

Args:
    ax: Matplotlib axes instance
    labels: tuple (strings to label the axes of coordinates)
'''

    # when the figure containing `ax' is resized, `ax' is also resized
    # delay for some time to allow this to happen
    plt.pause(0.5)

    # remove the previously added patches (if any)
    for patch in ax.patches:
        patch.remove()
    ax.patches = []

    # centre of the arrow patches in axes coordinates
    # i.e. [0, 0] is the lower left of the axes, and [1, 1], upper right
    x, y = [1.25, 0.5]

    # obtain the size of the Matplotlib axes
    # use this to control the sizes of the arrows
    ax_width_inches, ax_height_inches = get_ax_size_inches(ax)

    # angular axis arrow patch calculations
    arrow_height_inches = 1
    ht = arrow_height_inches / ax_height_inches
    xlabel_offset_inches = 0.175
    wd = xlabel_offset_inches / ax_width_inches
    kwargs = {'posA':            (x, y - ht / 2),
              'posB':            (x, y + ht / 2),
              'arrowstyle':      'Simple, tail_width = 0.6, head_width = 4, head_length = 8',
              'connectionstyle': 'arc3, rad = 0.15',
              'clip_on':         False,
              'transform':       ax.transAxes}
    angular = mpl.patches.FancyArrowPatch(**kwargs)
    ax.add_patch(angular)
    ax.xaxis.set_label_coords(x + wd, y + ht / 2)

    # radial axis arrow patch calculations
    arrow_length_inches = 0.6
    wd = arrow_length_inches / ax_width_inches
    ylabel_offset_inches = -0.25
    ht = ylabel_offset_inches / ax_height_inches
    kwargs = {'posA':            (x - wd / 2, y),
              'posB':            (x + wd / 2, y),
              'arrowstyle':      'Simple, tail_width = 0.6, head_width = 4, head_length = 8',
              'clip_on':         False,
              'transform':       ax.transAxes}
    radial = mpl.patches.FancyArrowPatch(**kwargs)
    ax.add_patch(radial)
    ax.yaxis.set_label_coords(x + wd / 2, y + ht)

    # axis labels
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1], rotation = 0)

###############################################################################

def polish(ax, labels = ('$x$', '$y$', '$z$'), title = None, suptitle = None):
    '''\
Label the coordinate axes. Give the plot a title. Add a legend. Draw grid
lines.

Args:
    ax: Matplotlib axes instance
    labels: tuple (strings to label the axes of coordinates)
    title: str (title of the graph plotted in `ax')
    suptitle: str (title of the figure `ax' is in)
'''

    # improvements for three-dimensional plots
    if ax.name == '3d':
        kwargs = {'which':     'major',
                  'labelsize': 'small',
                  'length':    4,
                  'direction': 'in'}
        ax.tick_params(axis = 'x', pad = 1, **kwargs)
        ax.tick_params(axis = 'y', pad = 1, **kwargs)
        ax.tick_params(axis = 'z', pad = 1, **kwargs)
        ax.set_facecolor('white')

    # improvements for polar plots
    if ax.name == 'polar':
        ax.set_rlabel_position(0)
        # draw_polar_axes_patches(ax, labels)
        if 'resize_event' not in ax.figure.canvas.callbacks.callbacks:
            callback = lambda event: draw_polar_axes_patches(ax, labels)
            ax.figure.canvas.mpl_connect('resize_event', callback)

    # axis labels for three-dimensional plots
    # a blank line is added to prevent axis and tick labels from overlapping
    if ax.name == '3d':
        for label, coordaxis in zip(labels, 'xyz'):
            getattr(ax, f'set_{coordaxis}label')(f'\n{label}', linespacing = 3)

    # axis labels for two-dimensional Cartesian plots
    # the labels for polar plots are set in `draw_polar_axes_patches'
    elif ax.name == 'rectilinear':
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1], rotation = 90)

    # titles
    if title is not None:
        ax.set_title(title)
    if suptitle is not None:
        ax.figure.suptitle(suptitle)
        ax.figure.canvas.set_window_title(suptitle)
    else:
        ax.figure.canvas.set_window_title(f'graph_{int(time.time())}')

    # legend
    if ax.get_legend_handles_labels() != ([], []):
        kwargs = {'loc': 'best'}
        if ax.name == 'polar':
            kwargs['loc'] = 'lower left'
            kwargs['bbox_to_anchor'] = (1, 1)
        if ax.name in {'polar', '3d'}:
            kwargs['facecolor'] = 'lightgray'
        ax.legend(**kwargs)

    # if this is a Cartesian two-dimensional plot, draw thick coordinate axes
    # this does not work as expected in three-dimensional plots
    if ax.name == 'rectilinear':
        kwargs = {'alpha': 0.6, 'linewidth': 1.2, 'color': 'gray'}
        ax.axhline(**kwargs)
        ax.axvline(**kwargs)

    # enable grid
    # minor grid doesn't look very good in three-dimensional plots
    if ax.name in {'rectilinear', 'polar'}:
        ax.grid(b = True, which = 'major', linewidth = 0.8, linestyle = ':')
        ax.grid(b = True, which = 'minor', linewidth = 0.1, linestyle = '-')
        ax.minorticks_on()
    elif ax.name == '3d':
        ax.grid(b = True, which = 'major', linewidth = 0.3, linestyle = '-')

###############################################################################

def aspect(ax, ratio = 0):
    '''\
Set the aspect ratio. If this is a two-dimensional Cartesian plot, the ratio of
the scales on the axes will be set to the given value (if it is non-zero). If
this is a two-dimensional polar plot, nothing happens.

For three-dimensional plots, an aspect ratio does not make sense, because there
are three axes. Hence, in this case, the scales on the axes will be made equal
if the given value is non-zero.
'''

    if ratio == 0:
        return

    if ax.name == 'rectilinear':
        ax.set_aspect(aspect = ratio, adjustable = 'box')
    elif ax.name == '3d':
        limits = np.array([getattr(ax, f'get_{coordaxis}lim')() for coordaxis in 'xyz'])
        ax.set_box_aspect(np.ptp(limits, axis = 1))

###############################################################################

def main():
    mpl.rcParams['savefig.directory'] = '/mnt/c/Users/vpaij/Pictures/'
    plt.style.use('dandy.mplstyle')

    ax = plt.figure().add_subplot(1, 1, 1)
    limit(ax, 'x', symbolic = False,
                   s        = r'\pi',
                   v        = np.pi,
                   first    = -8,
                   last     = 8,
                   step     = 1)
    limit(ax, 'y', symbolic = False,
                   s        = r'\pi',
                   v        = np.pi,
                   first    = -2,
                   last     = 6,
                   step     = 1)
    limit(ax, 'z', symbolic = False,
                   s        = r'\pi',
                   v        = np.pi,
                   first    = -1,
                   last     = 2,
                   step     = 1)

    x1 = np.linspace(-20, 20, 10000)
    y1 = (x1 ** 2) ** (1 / 3)
    z1 = x1
    ax.plot(x1, y1, color = 'red', label = r'$y=x^{2/3}$')
    # ax.plot(0, 0, color = 'red', mfc = 'red', linestyle = 'none', marker = 'o', label = '')
    # ax.text(0, 0, r'origin', size = 'large')

    # ax.fill_between(x1, y1, 0, facecolor = 'cyan', linewidth = 0, label = r'$R$')
    ax.fill_between(x1, y1, 0, facecolor = 'cyan', linewidth = 0, label = '$R$', where = [True if 0 < i < 2 else False for i in x1])
    # ax.fill_between(x1, y1, 1, facecolor = 'cyan', linewidth = 0, label = '', where = [True if 0.5 < i < 1 else False for i in x1])

    polish(ax, (r'$x$', r'$y$', r'$z$'), 'Fractional Power', None)
    aspect(ax, 1)

    # ax.set_xticklabels([r'$\mu-4\sigma$', r'$\mu-3\sigma$', r'$\mu-2\sigma$', r'$\mu-\sigma$', r'$\mu$', r'$\mu+\sigma$', r'$\mu+2\sigma$', r'$\mu+3\sigma$', r'$\mu+4\sigma$'])
    # ax.set_xticklabels([r'$\mu-4\sigma$', r'$\mu-3\sigma$', r'$\mu-2\sigma$', r'$\mu-\sigma$', r'$\mu$', r'$\mu+\sigma$', r'$\mu+2\sigma$', r'$\mu+3\sigma$', r'$\mu+4\sigma$'])
    # ax.set_yticklabels([r'$0$', r'$\dfrac{0.1}{\sigma}$', r'$\dfrac{0.2}{\sigma}$', r'$\dfrac{0.3}{\sigma}$', r'$\dfrac{0.4}{\sigma}$'])

    ax.figure.tight_layout(pad = 2)
    plt.show()

###############################################################################

if __name__ == '__main__':
    main()

