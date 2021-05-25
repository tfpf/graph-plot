import fractions
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.widgets as mwidgets
import numpy as np
import os
import time
import tkinter as tk
import weakref

###############################################################################

_gid = weakref.WeakKeyDictionary()

###############################################################################

def _generate_gid():
    return f'cp_{time.time_ns()}_{np.random.randint(100000, 999999)}'

###############################################################################

def _iprint(items, columns = 3, align_method = 'center'):
    '''\
Display an iterable in neat columns.

Args:
    items: iterable (each of its elements must have an `__str__' method)
    columns: int (number of columns to arrange `items' in)
    align_method: str (string method name: 'ljust', 'center' or 'rjust')
'''

    # Convert the iterable into a two-dimensional list.
    items = list(map(str, items))
    if len(items) % columns != 0:
        items.extend([''] * (columns - len(items) % columns))
    items = [items[i : i + columns] for i in range(0, len(items), columns)]

    # The required width of a column is the width of the longest string in that
    # column plus some extra spaces for padding.
    widths = [max(len(row[i]) for row in items) + 2 for i in range(columns)]

    for row in items:
        for r, width in zip(row, widths):
            print(getattr(r, align_method)(width, ' '), end = '')
        print()

###############################################################################

def _labels_and_ticks(first, last, step, symbol = r'\pi', symval = np.pi):
    r'''
Create a list of LaTeX-formatted strings and a NumPy array of floats for values
from one rational multiple of π (or some other number) to another.

>>> _labels_and_ticks(-1, 5, 2)
(['$-\\pi$', '$\\pi$', '$3\\pi$', '$5\\pi$'], array([-3.14159265,  3.14159265,  9.42477796, 15.70796327]))
>>> _labels_and_ticks(-1, -1 / 4, 1 / 4)
(['$-\\pi$', '$-\\dfrac{3\\pi}{4}$', '$-\\dfrac{\\pi}{2}$', '$-\\dfrac{\\pi}{4}$'], array([-3.14159265, -2.35619449, -1.57079633, -0.78539816]))
>>> _labels_and_ticks(-2, 2, 1)
(['$-2\\pi$', '$-\\pi$', '$0$', '$\\pi$', '$2\\pi$'], array([-6.28318531, -3.14159265,  0.        ,  3.14159265,  6.28318531]))
>>> _labels_and_ticks(2, 4, 1 / 2, symbol = r'\pi/\omega', symval = np.pi / 2)
(['$\\dfrac{2\\pi}{\\omega}$', '$\\dfrac{5\\pi}{2\\omega}$', '$\\dfrac{3\\pi}{\\omega}$', '$\\dfrac{7\\pi}{2\\omega}$', '$\\dfrac{4\\pi}{\\omega}$'], array([3.14159265, 3.92699082, 4.71238898, 5.49778714, 6.28318531]))

Args:
    first: float (first item in the returned array shall be `first * symval')
    last: float (last item in the returned array shall be `last * symval')
    step: float (array items will increment in steps of `step * symval')
    symbol: str (LaTeX code or two slash-separated LaTeX codes of the symbol or
            symbols to use instead of π)
    symval: float (numerical value represented by `symbol')

Returns:
    tuple of a list of labels and a NumPy array of the respective values
'''

    if '/' in symbol:
        s_num, s_den = symbol.split('/')
    else:
        s_num = symbol
        s_den = '1'

    coefficients = np.arange(first, last + step / 2, step)

    # Pre-allocate space for the list because its length is known. As a result,
    # this loop will run approximately twice as fast as it would if items were
    # repeatedly appended to the list.
    labels = [None] * len(coefficients)

    for i, coefficient in enumerate(coefficients):
        value = fractions.Fraction(coefficient).limit_denominator()
        num = value.numerator
        den = value.denominator

        # Case 1: `coefficient' is zero.
        if num == 0:
            labels[i] = '$0$'
            continue

        # Build the string which will be the next item in `labels'. Create a
        # list to store the different parts of the string, and join those
        # parts.
        builder = ['$']

        # Case 2: `coefficient' is non-zero.
        if num < 0:
            builder.append('-')
            num = abs(num)
        is_fraction = den != 1 or s_den != '1'
        if is_fraction:
            builder.append(r'\dfrac{')
        if num != 1:
            builder.append(f'{num}')
        if s_num != '1' or num == 1:
            builder.append(s_num)
        if is_fraction:
            builder.append(r'}{')
        if den != 1:
            builder.append(f'{den}')
        if s_den != '1':
            builder.append(s_den)
        if is_fraction:
            builder.append(r'}')
        builder.append('$')
        labels[i] = ''.join(builder)

    return labels, symval * coefficients

###############################################################################

def _get_axes_size_in_inches(ax):
    bbox = ax.get_window_extent()
    transformed = bbox.transformed(ax.figure.dpi_scale_trans.inverted())
    return transformed.width, transformed.height

###############################################################################

def _draw_polar_patches(event):
    '''\
Draw arrow patches to show the angular and radial axes of coordinates of all
polar plots in the figure. The sizes of these arrow patches must be independent
of the size of the figure. Hence, this function is connected to the resize
event of the appropriate Matplotlib figure canvas instance, so that the arrows
can be redrawn when the canvas is resized.

Finally, labels on the axes of coordinates are made visible.

Args:
    event: Matplotlib event (the event which triggered this function)
'''

    canvas = event.canvas
    fig = canvas.figure

    # Stop the event loop (if it is already running). If this is not done, a
    # RuntimeError may be raised when `plt.pause' is called.
    canvas.stop_event_loop()

    # When the canvas is resized, Matplotlib axes are also resized. Delay for
    # some time to allow this to happen.
    plt.pause(0.1)

    for ax in fig.axes:
        if ax.name != 'polar':
            continue

        # Remove the previously added arrow patches (if any). Do not remove any
        # other patches.
        gid = _gid[fig]
        comparer = lambda patch: patch.get_gid() == gid
        patches_to_remove = list(filter(comparer, ax.patches))
        for patch in patches_to_remove:
            patch.remove()

        # Obtain the current size of the Matplotlib axes instance. This is used
        # to calculate the sizes of the arrows.
        ax_width_inches, ax_height_inches = _get_axes_size_in_inches(ax)

        # This is the centre of the arrow patches in axes coordinates. (Axes
        # coordinates: [0, 0] is the lower left corner of the Matplotlib axes,
        # and [1, 1], the upper right.)
        x = 1 + 0.8 / ax_width_inches
        y = 0.5

        arrow_height_inches = 1
        ht = arrow_height_inches / ax_height_inches
        xlabel_offset_inches = 0.175
        wd = xlabel_offset_inches / ax_width_inches
        kwargs = {'posA':            (x, y - ht / 2),
                  'posB':            (x, y + ht / 2),
                  'arrowstyle':      'Simple, tail_width = 0.6, head_width = 4, head_length = 8',
                  'connectionstyle': 'arc3, rad = 0.15',
                  'clip_on':         False,
                  'transform':       ax.transAxes,
                  'gid':             gid}
        angular = mpatches.FancyArrowPatch(**kwargs)
        ax.add_patch(angular)
        ax.xaxis.set_label_coords(x + wd, y + ht / 2)

        arrow_length_inches = 0.6
        wd = arrow_length_inches / ax_width_inches
        ylabel_offset_inches = -0.25
        ht = ylabel_offset_inches / ax_height_inches
        kwargs = {'posA':            (x - wd / 3, y),
                  'posB':            (x + 2 * wd / 3, y),
                  'arrowstyle':      'Simple, tail_width = 0.6, head_width = 4, head_length = 8',
                  'clip_on':         False,
                  'transform':       ax.transAxes,
                  'gid':             gid}
        radial = mpatches.FancyArrowPatch(**kwargs)
        ax.add_patch(radial)
        ax.yaxis.set_label_coords(x + wd / 2, y + ht)

        ax.xaxis.label.set_visible(True)
        ax.yaxis.label.set_visible(True)

###############################################################################

def sanitise(y, maximum_diff = 5):
    '''\
At a point of essential or jump discontinuity, Matplotlib draws a vertical line
automatically. This vertical line joins the two points around the
discontinuity. Traditionally, in maths, such lines are not drawn. Hence, they
must removed from the plot. This is achieved by setting the function values at
the points of discontinuity to NaN.

Args:
    y: iterable (values of the discontinuous function)
    maximum_diff: float (the maximum permissible derivative of `y')

Returns:
    NumPy array with NaN at the points of discontinuity
'''

    y = np.array(y)
    points_of_discontinuity = np.abs(np.r_[[0], np.diff(y)]) > maximum_diff
    y[points_of_discontinuity] = np.nan

    return y

###############################################################################

def limit(ax, coordaxis = None, symbolic = False, s = r'\pi', v = np.pi, first = None, last = None, step = None):
    '''\
Limit the specified axis of coordinates to the range given. Draw grid lines as
indicated.

In three-dimensional plots, these limits on the axes of coordinates are not
respected. Matplotlib automatically modifies them by a small amount (the
relevant code can be found in the `_get_coord_info' method of
mpl_toolkits/mplot3d/axis3d.py as of version 3.3.4 of Matplotlib). If you don't
like this, you must modify the source code.

Args:
    ax: Matplotlib axes instance
    coordaxis: str (which axis of coordinates to limit: 'x', 'y' or 'z')
    symbolic: bool (whether ticks are at rational multiples of `v')
    s: str (LaTeX code or two slash-separated LaTeX codes of the symbol or
       symbols to use instead of π)
    v: float (numerical value represented by `s')
    first: float (tick start point)
    last: float (tick end point)
    step: float (tick spacing)

Returns:
    bool, indicating whether this function did something or returned early
'''

    if coordaxis == 'z' and ax.name != '3d':
        return False

    labels_getter = getattr(ax, f'get_{coordaxis}ticklabels')
    labels_setter = getattr(ax, f'set_{coordaxis}ticklabels')
    limits_setter = getattr(ax, f'set_{coordaxis}lim')
    ticks_getter  = getattr(ax, f'get_{coordaxis}ticks')
    ticks_setter  = getattr(ax, f'set_{coordaxis}ticks')
    axis          = getattr(ax, f'{coordaxis}axis')

    # Case 1: use symbolic tick labels.
    if symbolic:
        if any(arg is None for arg in [first, last, step]):
            raise ValueError('If argument "symbolic" is True, arguments "first", "last" and "step" must not be None.')

        labels, ticks = _labels_and_ticks(first, last, step, s, v)

        # In polar plots, the angular axis may go from 0 to 2π. In that case,
        # do not draw the label for 2π. (Otherwise, it'll overlap with that for
        # 0). Further, do not draw the first and last labels on the radial
        # axis. (This reduces cluttering.)
        if ax.name == 'polar':
            if coordaxis == 'x' and first == 0 and last == 2:
                labels, ticks = labels[: -1], ticks[: -1]
            elif coordaxis == 'y':
                labels[0] = labels[-1] = ''

        ticks_setter(ticks)
        labels_setter(labels)
        limits_setter(v * first, v * last)

        # If the x-axis labels will contain fractions, increase the padding
        # slightly. Do not do this for polar plots (the spacing is already
        # quite good). Do not do this for three-dimensional plots, either
        # (Matplotlib messes up the spacing).
        if ax.name == 'rectilinear' and coordaxis == 'x' and not all(isinstance(t, int) for t in [first, last, step]):
            ax.tick_params(axis = coordaxis, which = 'major', pad = 20)
            for tick in labels_getter():
                tick.set_horizontalalignment('center')
                tick.set_verticalalignment('center')

    # Case 2: allow tick labels to be set automatically.
    else:
        if all(arg is not None for arg in [first, last, step]):
            ticks_setter(np.arange(first, last + step / 2, step))
        if all(arg is not None for arg in [first, last]):
            limits_setter(first, last)

        # Generate the axis labels in case they were erased because of a
        # previous call to this function.
        axis.set_major_formatter(mticker.ScalarFormatter())

        # Like in case 1, do not draw the first and last labels on the radial
        # axis. However, if `step' has not been provided, Matplotlib may not
        # start labelling the radial axis from zero. So, check the first tick
        # before doing this.
        ax.figure.canvas.draw()
        if ax.name == 'polar' and coordaxis == 'y':
            labels = [l.get_text() for l in labels_getter()]
            ticks = ticks_getter()
            if ticks[0] == 0:
                labels[0] = ''
            labels[-1] = ''
            labels_setter(labels)

    return True

###############################################################################

def polish(ax, labels = None, title = None, suptitle = None):
    '''\
Label the axes of coordinates. Give the plot a title. Add a legend. Draw grid
lines. Make some minor appearance enhancements.

Args:
    ax: Matplotlib axes instance
    labels: tuple (strings to label the axes of coordinates)
    title: str (title of the graph plotted in `ax')
    suptitle: str (title of the figure `ax' is in)
'''

    if labels is None:
        if ax.name in {'rectilinear', '3d'}:
            labels = ('$x$', '$y$', '$z$')
        elif ax.name == 'polar':
            labels = (r'$\theta$', '$r$')

    if ax.name == '3d':
        kwargs = {'which':     'major',
                  'labelsize': 'small',
                  'length':    4,
                  'direction': 'in'}
        ax.xaxis.set_tick_params(pad = 1, **kwargs)
        ax.yaxis.set_tick_params(pad = 1, **kwargs)
        ax.zaxis.set_tick_params(pad = 1, **kwargs)
        ax.set_facecolor('white')

        # A new line character is used here because the `labelpad' argument
        # does not work.
        for label, coordaxis in zip(labels, 'xyz'):
            getattr(ax, f'set_{coordaxis}label')(f'\n{label}', labelpad = 10, linespacing = 3)

    elif ax.name == 'rectilinear':
        kwargs = {'alpha': 0.6, 'linewidth': 1.2, 'color': 'gray'}
        ax.axhline(**kwargs)
        ax.axvline(**kwargs)
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1], rotation = 90)

    # The labels of the polar axes of coordinates will initially not be
    # visible. They will be made visible after they have been placed in their
    # correct locations by a callback.
    elif ax.name == 'polar':
        ax.set_rlabel_position(0)
        ax.set_xlabel(labels[0], visible = False)
        ax.set_ylabel(labels[1], rotation = 0, visible = False)

    # Minor grid lines don't look good in three-dimensional plots.
    if ax.name in {'rectilinear', 'polar'}:
        ax.grid(b = True, which = 'major', linewidth = 0.8, linestyle = ':')
        ax.grid(b = True, which = 'minor', linewidth = 0.1, linestyle = '-')
        ax.minorticks_on()
    elif ax.name == '3d':
        ax.grid(b = True, which = 'major', linewidth = 0.3, linestyle = '-')

    # Key a unique ID with the figure instance in the global WeakKeyDictionary.
    fig = ax.figure
    canvas = fig.canvas
    gid = _generate_gid()
    if fig not in _gid:
        _gid[fig] = gid

        # Connect the resize event of the canvas to a callback which does some
        # additional beautification.
        if ax.name == 'polar':
            canvas.mpl_connect('resize_event', _draw_polar_patches)
            canvas.resize_event()

    if title is not None:
        ax.set_title(title)
    if suptitle is not None:
        fig.suptitle(suptitle)

    if ax.get_legend_handles_labels() != ([], []):
        kwargs = {'loc': 'best'}
        if ax.name == 'polar':
            kwargs['loc'] = 'lower left'
            kwargs['bbox_to_anchor'] = (1, 1)
        if ax.name in {'polar', '3d'}:
            kwargs['facecolor'] = 'lightgray'
        ax.legend(**kwargs)

    # Maximise the figure window.
    manager = canvas.manager
    backend = mpl.get_backend()
    if backend in {'TkAgg', 'TkCairo'}:
        if os.name == 'nt':
            manager.window.state('zoomed')
        else:
            manager.resize(*manager.window.maxsize())
    elif backend in {'GTK3Agg', 'GTK3Cairo'}:
        manager.window.maximize()
    elif backend in {'WXAgg', 'WXCairo'}:
        manager.frame.Maximize(True)
    elif backend in {'Qt5Agg', 'Qt5Cairo'}:
        manager.window.showMaximized()

###############################################################################

def aspect(ax, ratio = 0):
    '''\
Set the aspect ratio. If `ax' is being used for two-dimensional Cartesian
plots, the ratio of the scales on the x-axis and y-axis will be set to `ratio'
(if it is non-zero). If `ax' is being used for two-dimensional polar plots,
nothing happens.

For three-dimensional plots, an aspect ratio does not make sense, because there
are three axes of coordinates. Hence, in this case, the scales on those axes
will be made equal if `ratio' is any non-zero number.

Args:
    ax: Matplotlib axes instance
    ratio: float (ratio of the scale on the x-axis to that on the y-axis)
'''

    if ratio == 0:
        return

    if ax.name == 'rectilinear':
        ax.set_aspect(aspect = ratio, adjustable = 'box')
    elif ax.name == '3d':
        limits = np.array([getattr(ax, f'get_{coordaxis}lim')() for coordaxis in 'xyz'])
        ax.set_box_aspect(np.ptp(limits, axis = 1))

###############################################################################

class _Frame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, bg = '#333333', borderwidth = 3, relief = tk.RAISED)

class _Label(tk.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, bg = '#333333', fg = '#CCCCCC')

class _Entry(tk.Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, bg = '#333333', fg = '#CCCCCC', insertbackground = '#CCCCCC')

class _Checkbutton(tk.Checkbutton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, bg = '#333333', borderwidth = 0, highlightthickness = 0)

###############################################################################

class AxesOptions(_Frame):
    '''\
Interactively adjust some plot elements of a Matplotlib axes instance via a
GUI. This feature is experimental and may not be developed further.

Args:
    parent: tkinter.Tk or tkinter.Toplevel (master window)
    ax: Matplotlib axes instance
'''

    padx, pady = 10, 10

    ###########################################################################

    def __init__(self, parent, ax):
        super().__init__(parent)
        self.pack()

        self._ax = ax
        self._fig = ax.figure
        self._canvas = self._fig.canvas
        self._title = self._canvas.get_window_title()
        self._coordaxes = 'xyz'
        self._headers = ['Symbolic', 'Symbol', 'Value', 'Limits', 'Label']
        self._widgets = dict()

        parent.resizable(False, False)
        parent.title(f'{self.__class__.__name__} for {self._title} at 0x{id(self._ax):X}')

        # Upper part of the window, which will allow the user to manipulate the
        # axes of coordinates.
        upper_frame = _Frame(self)
        upper_frame.grid(row = 0, padx = self.padx, pady = self.pady)

        # Create header labels.
        for i, header in enumerate(self._headers, 1):
            row_header = _Label(upper_frame, text = header)
            row_header.grid(row = i, column = 0, padx = self.padx, pady = self.pady)
        for i, coordaxis in enumerate(self._coordaxes, 1):
            column_header = _Label(upper_frame, text = f'{coordaxis}-axis')
            column_header.grid(row = 0, column = i, padx = self.padx, pady = self.pady)

        # Create widgets where data will be entered. The first item is a
        # checkbox; the rest are entries. (Which is why I chose to write nested
        # loops rather than use `itertools.product'.) Put each widget into a
        # dictionary so that it can be looked up easily in the callback.
        for i, coordaxis in enumerate(self._coordaxes, 1):
            name = f'{coordaxis},Symbolic'
            check_variable = tk.BooleanVar()
            check_button = _Checkbutton(upper_frame, variable = check_variable, offvalue = False, onvalue = True)
            check_button.configure(command = getattr(self, f'_modify_{coordaxis}axis_parameters'))
            check_button.grid(row = 1, column = i, padx = self.padx, pady = self.pady)
            self._widgets[name] = check_variable

            for j, header in enumerate(self._headers[1 :], 2):
                name = f'{coordaxis},{header}'
                entry = _Entry(upper_frame, name = name)
                entry.bind('<Return>', self._unfocus_from_widget)
                entry.bind('<FocusOut>', self._modify_axis_parameters)
                entry.grid(row = j, column = i, padx = self.padx, pady = self.pady)
                self._widgets[name] = entry

        # Set defaults for some of the above entries.
        for coordaxis in self._coordaxes:
            self._widgets[f'{coordaxis},Symbol'].insert(0, r'\pi')
            self._widgets[f'{coordaxis},Value'].insert(0, f'{np.pi}')
            try:
                self._widgets[f'{coordaxis},Label'].insert(0, getattr(ax, f'get_{coordaxis}label')())
            except AttributeError:
                pass

        # Middle part of the window, which will allow the user to place
        # Matplotlib text instances.
        if ax.texts != []:
            lower_frame = _Frame(self)
            lower_frame.grid(row = 1, padx = self.padx, pady = self.pady)

        # Create headers and entries for the above.
        for i, text in enumerate(ax.texts):
            label = _Label(lower_frame, text = f'Location of {text.get_text()}')
            label.grid(row = i, column = 0, padx = self.padx, pady = self.pady)

            entry = _Entry(lower_frame, name = f'{i}')
            entry.bind('<Return>', self._unfocus_from_widget)
            entry.bind('<FocusOut>', self._set_text_location)
            entry.grid(row = i, column = 1, padx = self.padx, pady = self.pady)

        # Entry containing the name of the file to which the figure will be
        # saved.
        entry = _Entry(self, width = 70)
        entry.bind('<Return>', self._save_to_file)
        entry.insert(0, os.path.join(mpl.rcParams['savefig.directory'], f'{self._title}.png'))
        entry.grid(row = 2, padx = self.padx, pady = self.pady)

    ###########################################################################

    def _modify_xaxis_parameters(self):
        self._modify_axis_parameters(name = 'x,Symbolic')

    ###########################################################################

    def _modify_yaxis_parameters(self):
        self._modify_axis_parameters(name = 'y,Symbolic')

    ###########################################################################

    def _modify_zaxis_parameters(self):
        self._modify_axis_parameters(name = 'z,Symbolic')

    ###########################################################################

    def _modify_axis_parameters(self, event = None, name = None):

        # Either `event' will be None or `name' will be None, but both will not
        # simultaneously be None.
        if event is not None:
            entry = event.widget
            name = entry.winfo_name()
        coordaxis, header = name.split(',')

        # If the user is trying to set the label of a coordinate axis, `event'
        # is guaranteed to not be None. Hence, `entry' is available to use.
        if header == 'Label':
            try:
                getattr(self._ax, f'set_{coordaxis}label')(entry.get())
            except AttributeError:
                return
            else:
                self._update_canvas()
                return

        # Disable symbolic labelling if a valid number is not specified.
        symbolic = self._widgets[f'{coordaxis},Symbolic'].get()
        try:
            v = float(self._widgets[f'{coordaxis},Value'].get())
        except ValueError:
            symbolic = False
            v = 0

        # Disable symbolic labelling if no symbol is specified.
        s = self._widgets[f'{coordaxis},Symbol'].get()
        if s == '':
            symbolic = False

        try:
            first, last, step = map(float, self._widgets[f'{coordaxis},Limits'].get().split())
        except ValueError:
            return

        if limit(self._ax, coordaxis, symbolic, s, v, first, last, step):
            self._update_canvas()

    ###########################################################################

    def _set_text_location(self, event):
        entry = event.widget
        name = entry.winfo_name()
        text = self._ax.texts[int(name)]

        try:
            coords = tuple(map(float, entry.get().split()))
            text.set_position(coords)
        except (ValueError, IndexError):
            return

        self._update_canvas()

    ###########################################################################

    def _save_to_file(self, event):
        entry = event.widget

        try:
            self._fig.savefig(entry.get())
        except FileNotFoundError:
            return
        else:
            self.focus_set()

    ###########################################################################

    def _unfocus_from_widget(self, event):
        self.focus_set()

    ###########################################################################

    def _update_canvas(self):
        self._canvas.draw()
        plt.pause(0.1)

