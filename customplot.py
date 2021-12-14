import fractions
import io
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.projections as mprojections
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import platform
import sys
import threading
import time
import weakref

try:
    import curses
    has_curses = True
except ImportError:
    has_curses = False

###############################################################################

_gid = weakref.WeakKeyDictionary()

###############################################################################

def iprint(items, columns=3, align_method='center'):
    '''\
Display an iterable in neat columns.

Args:
    items: iterable (each of its elements must have an `__str__' method)
    columns: int (number of columns to arrange `items' in)
    align_method: str (string method name: 'ljust', 'center' or 'rjust')
'''

    # Convert the iterable into a two-dimensional list.
    items = list(map(str, items))
    num_items = len(items)
    if num_items % columns:
        items.extend([''] * (columns - num_items % columns))
    items = [items[i : i + columns] for i in range(0, len(items), columns)]

    # The required width of a column is the width of the longest string in that
    # column plus some extra spaces for padding.
    widths = [max(len(row[i]) for row in items) + 2 for i in range(columns)]

    for row in items:
        for r, width in zip(row, widths):
            print(getattr(r, align_method)(width, ' '), end='')
        print()

###############################################################################

def _labels_and_ticks(first, last, step, symbol=r'\pi', symval=np.pi):
    r'''
Create a list of LaTeX-formatted strings and a NumPy array of floats for values
from one rational multiple of π (or some other number) to another.

>>> _labels_and_ticks(-1, 5, 2)
(['$-\\pi$', '$\\pi$', '$3\\pi$', '$5\\pi$'], array([-3.14159265,  3.14159265,  9.42477796, 15.70796327]))
>>> _labels_and_ticks(-1, -1 / 4, 1 / 4)
(['$-\\pi$', '$-\\dfrac{3\\pi}{4}$', '$-\\dfrac{\\pi}{2}$', '$-\\dfrac{\\pi}{4}$'], array([-3.14159265, -2.35619449, -1.57079633, -0.78539816]))
>>> _labels_and_ticks(-2, 2, 1)
(['$-2\\pi$', '$-\\pi$', '$0$', '$\\pi$', '$2\\pi$'], array([-6.28318531, -3.14159265,  0.        ,  3.14159265,  6.28318531]))
>>> _labels_and_ticks(2, 4, 1 / 2, symbol=r'\pi/\omega', symval=np.pi / 2)
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

    try:
        s_num, s_den = symbol.split('/')
    except ValueError:
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

    return (labels, symval * coefficients)

###############################################################################

def _get_axes_size_in_inches(ax):
    bbox = ax.get_window_extent()
    transformed = bbox.transformed(ax.figure.dpi_scale_trans.inverted())

    return (transformed.width, transformed.height)

###############################################################################

def _schedule_draw_polar_patches(event):
    '''\
Set the flag in the global weak key dictionary indicating that the polar
patches in one or more polar axes in this figure have to be updated.

This function is triggered when the canvas is resized. It is not possible to
actually redraw the polar patches here, because doing so requires that the
resize operation has been completed.

Args:
    event: Matplotlib event (the event which triggered this function)
'''

    fig = event.canvas.figure
    _gid[fig][1] = True

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
    [gid, needs_redraw] = _gid[fig]
    if not needs_redraw:
        return

    _gid[fig][1] = False

    for ax in fig.axes:
        if ax.name != 'polar':
            continue

        # Remove the previously added arrow patches (if any). Do not remove any
        # other patches. Since the original list (namely `ax.patches') gets
        # mutated whenever any patch is removed, make a shallow copy of it.
        for patch in ax.patches[:]:
            if patch.get_gid() == gid:
                patch.remove()

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
                  'arrowstyle':      'Simple, tail_width=0.6, head_width=4, head_length=8',
                  'connectionstyle': 'arc3, rad=0.15',
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
                  'arrowstyle':      'Simple, tail_width=0.6, head_width=4, head_length=8',
                  'clip_on':         False,
                  'transform':       ax.transAxes,
                  'gid':             gid}
        radial = mpatches.FancyArrowPatch(**kwargs)
        ax.add_patch(radial)
        ax.yaxis.set_label_coords(x + wd / 2, y + ht)

        ax.xaxis.label.set_visible(True)
        ax.yaxis.label.set_visible(True)

        canvas.draw_idle()

###############################################################################

def sanitise(y, maximum_diff=5):
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

def limit(ax, coordaxis=None, symbolic=False, s=r'\pi', v=np.pi, first=None, last=None, step=None):
    '''\
Limit the specified axis of coordinates to the range given. Draw grid lines as
indicated.

In three-dimensional plots, these limits on the axes of coordinates are not
respected. Matplotlib automatically modifies them by a small amount (the
relevant code can be found in the `_get_coord_info' method of
mpl_toolkits/mplot3d/axis3d.py as of version 3.3.4 of Matplotlib). If you don't
like this, you must modify the source code.

Args:
    ax: matplotlib.axes.Axes
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

        if ax.name == 'polar':

            # Does the angular axis go from 0 to 2π? If yes, remove the last
            # tick and label (i.e. the ones for 2π). Otherwise, they will
            # overlap with the first tick and label (i.e. the ones for 0).
            if coordaxis == 'x' and first == 0 and np.isclose(last * v, 2 * np.pi):
                labels, ticks = labels[: -1], ticks[: -1]

            # Remove the last label on the radial axis. Remove the first label
            # if it marks zero.
            elif coordaxis == 'y':
                if first == 0:
                    labels[0] = ''
                labels[-1] = ''

        ticks_setter(ticks)
        labels_setter(labels)
        limits_setter(v * first, v * last)

        # If the x-axis labels will contain fractions, adjust the tick padding.
        if coordaxis == 'x':
            if not all(t == int(t) for t in [first, last, step]):
                if ax.name == 'rectilinear':
                    ax.tick_params(axis=coordaxis, which='major', pad=mpl.rcParams['xtick.major.pad'] * 3.2)
                    for label in labels_getter():
                        label.set_verticalalignment('center')
                elif ax.name == 'polar':
                    ax.tick_params(axis=coordaxis, which='major', pad=mpl.rcParams['xtick.major.pad'] * 2)
                    for label in labels_getter():
                        label.set_verticalalignment('center')
            else:
                ax.tick_params(axis=coordaxis, which='major', pad=mpl.rcParams['xtick.major.pad'])
                for label in labels_getter():
                    label.set_verticalalignment('top')

    # Case 2: allow tick labels to be set automatically.
    else:
        if all(arg is not None for arg in [first, last, step]):
            ticks_setter(np.arange(first, last + step / 2, step))
        if all(arg is not None for arg in [first, last]):
            limits_setter(first, last)

        # Generate the axis tick labels in case they were erased because of a
        # previous call to this function.
        if ax.name in {'rectilinear', '3d'} or ax.name == 'polar' and coordaxis == 'y':
            axis.set_major_formatter(mticker.ScalarFormatter())
        elif ax.name == 'polar' and coordaxis == 'x':
            axis.set_major_formatter(mprojections.polar.ThetaFormatter())
        if coordaxis == 'x':
            if ax.name == 'polar':
                ax.tick_params(axis=coordaxis, which='major', pad=mpl.rcParams['xtick.major.pad'] * 1.5)
                for label in labels_getter():
                    label.set_verticalalignment('center')
            else:
                ax.tick_params(axis=coordaxis, which='major', pad=mpl.rcParams['xtick.major.pad'])
                for label in labels_getter():
                    label.set_verticalalignment('top')

        if ax.name == 'polar':
            ax.figure.canvas.draw()
            ticks = ticks_getter()
            labels = [label.get_text() for label in labels_getter()]

            # Just like in case 1. With the difference that `ticks' is used
            # instead of `first' and `last' to check the limits.
            if coordaxis == 'x' and ticks[0] == 0 and np.isclose(ticks[-1], 2 * np.pi):
                labels, ticks = labels[: -1], ticks[: -1]
                ticks_setter(ticks)
                labels_setter(labels)

            # Again, just like case 1.
            elif coordaxis == 'y':
                if ticks[0] == 0:
                    labels[0] = ''
                labels[-1] = ''
                ticks_setter(ticks)
                labels_setter(labels)

    return True

###############################################################################

def polish(ax, labels=None, title=None, suptitle=None, windowtitle=None):
    '''\
Label the axes of coordinates. Give the plot a title. Add a legend. Draw grid
lines. Make some minor appearance enhancements.

Args:
    ax: matplotlib.axes.Axes
    labels: tuple (strings to label the axes of coordinates)
    title: str (title of the graph plotted in `ax')
    suptitle: str (title of the figure `ax' is in)
    windowtitle: str (title of the window `figure' is in)
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
        ax.xaxis.set_tick_params(pad=1, **kwargs)
        ax.yaxis.set_tick_params(pad=1, **kwargs)
        ax.zaxis.set_tick_params(pad=1, **kwargs)
        ax.set_facecolor('white')

        for label, coordaxis in zip(labels, 'xyz'):
            getattr(ax, f'set_{coordaxis}label')(label, labelpad=10)

    elif ax.name == 'rectilinear':
        kwargs = {'alpha': 0.6, 'linewidth': mpl.rcParams['axes.linewidth']}
        if mpl.rcParams['axes.edgecolor'] == '#CCCCCC':
            kwargs['color'] = '#BBBBBB'
        else:
            kwargs['color'] = 'gray'
        ax.axhline(**kwargs)
        ax.axvline(**kwargs)
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1], rotation=90)

    # The labels of the polar axes of coordinates will initially not be
    # visible. They will be made visible after they have been placed in their
    # correct locations by a callback.
    elif ax.name == 'polar':
        ax.set_rlabel_position(0)
        ax.set_xlabel(labels[0], visible=False)
        ax.set_ylabel(labels[1], rotation=0, visible=False)

    # Minor grid lines don't look good in three-dimensional plots.
    if ax.name in {'rectilinear', 'polar'}:
        ax.grid(b=True, which='major', linewidth=0.5, linestyle=':')
        ax.grid(b=True, which='minor', linewidth=0.0625, linestyle='-')
        ax.minorticks_on()
    elif ax.name == '3d':
        ax.grid(b=True, which='major', linewidth=mpl.rcParams['grid.linewidth'], linestyle='-')

    # Key a unique ID with the figure instance in the global weak key
    # dictionary. Doing so ensures that the following operations are performed
    # only once.
    fig = ax.figure
    canvas = fig.canvas
    if any(_ax.name == 'polar' for _ax in fig.axes) and fig not in _gid:
        timefmt = '%Y-%m-%d_%H-%M-%S'
        _gid[fig] = [f'cp_{time.strftime(timefmt)}_{np.random.randint(100, 999)}', True]
        canvas.mpl_connect('resize_event', _schedule_draw_polar_patches)
        canvas.mpl_connect('axes_enter_event', _draw_polar_patches)
        canvas.mpl_connect('axes_leave_event', _draw_polar_patches)
        canvas.mpl_connect('figure_enter_event', _draw_polar_patches)
        canvas.mpl_connect('figure_leave_event', _draw_polar_patches)

    if title is not None:
        ax.set_title(title)
    if suptitle is not None:
        fig.suptitle(suptitle)
    if windowtitle is not None:
        canvas.manager.set_window_title(windowtitle)

    if ax.get_legend_handles_labels() != ([], []):
        kwargs = {'loc': 'best'}
        if ax.name == 'polar':
            kwargs['loc'] = 'lower left'
            kwargs['bbox_to_anchor'] = (1, 1)
        ax.legend(**kwargs)

###############################################################################

def aspect(ax, ratio=0):
    '''\
Set the aspect ratio. If `ax' is being used for two-dimensional Cartesian
plots, the ratio of the scales on the x-axis and y-axis will be set to `ratio'
(if it is non-zero). If `ax' is being used for two-dimensional polar plots,
nothing happens.

For three-dimensional plots, an aspect ratio does not make sense, because there
are three axes of coordinates. Hence, in this case, the scales on those axes
will be made equal if `ratio' is any non-zero number.

Args:
    ax: matplotlib.axes.Axes
    ratio: float (ratio of the scale on the x-axis to that on the y-axis)
'''

    if ratio == 0:
        return

    if ax.name == 'rectilinear':
        ax.set_aspect(aspect=ratio, adjustable='box')
    elif ax.name == '3d':
        limits = np.array([getattr(ax, f'get_{coordaxis}lim')() for coordaxis in 'xyz'])
        ax.set_box_aspect(np.ptp(limits, axis=1))

###############################################################################

class _Interactive(threading.Thread):
    '''\
Interactively adjust some plot elements of a Matplotlib axes instance using a
curses GUI running in a separate thread. This does not work with Tkinter-based
backends.

Members:
    fig: matplotlib.figure.Figure
    canvas: matplotlib.backends.backend_*.FigureCanvas*
    manager: matplotlib.backends.backend_*.FigureManager*
    page_num: int (current Matplotlib axes for which options are displayed)
    pages: int (number of Matplotlib axes in `fig')
    data: dict (stores the information entered in the GUI)
    headers: list
    coordaxes: list
    tmp_stderr: io.StringIO (standard error buffer used when the GUI is active)
    stdscr: curses.window
    height: int
    width: int
    column_width: int
    dividers: list

Methods:
    __init__
    redirect_streams
    restore_streams
    run
    join
    draw_GUI
    process_keystroke
    update
    main
'''

    ###########################################################################

    def __init__(self, fig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fig = fig
        self.canvas = fig.canvas
        self.manager = fig.canvas.manager
        self.page_num = 0
        self.pages = len(fig.axes)
        self.data = [{} for _ in fig.axes]
        self.headers = ['Symbolic', 'Symbol', 'Value', 'Limits', 'Label']
        self.coordaxes = ['x', 'y', 'z']

        # Initialise the contents with some useful defaults.
        for i in range(self.pages):
            for coordaxis in self.coordaxes:
                self.data[i][f'Symbolic,{coordaxis}'] = ''
                self.data[i][f'Symbol,{coordaxis}'] = r'\pi'
                self.data[i][f'Value,{coordaxis}'] = f'{np.pi}'
                self.data[i][f'Limits,{coordaxis}'] = ''
                try:
                    self.data[i][f'Label,{coordaxis}'] = getattr(self.fig.axes[i], f'get_{coordaxis}label')()
                except AttributeError:
                    self.data[i][f'Label,{coordaxis}'] = ''

        self.redirect_streams()

    ###########################################################################

    def redirect_streams(self):
        sys.stderr = self.tmp_stderr = io.StringIO()

    ###########################################################################

    def restore_streams(self):
        value = self.tmp_stderr.getvalue()
        self.tmp_stderr.close()
        sys.stderr = sys.__stderr__
        sys.stderr.write(value)

    ###########################################################################

    def run(self):
        curses.wrapper(self.main)

    ###########################################################################

    def join(self, *args):
        super().join(*args)
        self.restore_streams()

    ###########################################################################

    def draw_GUI(self):
        row = 0

        # Title identifying the figure.
        title = f'Options for {self.manager.get_window_title()} at 0x{id(self.fig):X}'
        self.stdscr.addstr(row, 0, title.center(self.width), curses.A_BOLD)
        row += 1

        # Subtitle identifying the axes.
        subtitle = f'Axes {self.page_num + 1}/{self.pages}: {self.fig.axes[self.page_num].get_title()}'
        self.stdscr.addstr(row, 0, subtitle.center(self.width), curses.A_BOLD)
        row += 2

        # Calculations for drawing the margins.
        header_column_width = 10
        while (self.width - header_column_width) % 3:
            header_column_width += 1
        self.column_width = (self.width - header_column_width - 3) // 3
        self.dividers = [header_column_width + i * (self.column_width + 1) for i in range(3)]

        # Margins.
        self.stdscr.addstr(row, 0, '-' * self.width)
        self.stdscr.addstr(row + 2, 0, '-' * self.width)
        row += 1
        for i in range(7):
            for d in self.dividers:
                self.stdscr.addstr(row + i, d, '|')
        self.stdscr.addstr(row + i + 1, 0, '-' * self.width)

        # Headers.
        for d, coordaxis in zip(self.dividers, self.coordaxes):
            self.stdscr.addstr(row, d + 1, f'{coordaxis} axis'.center(self.column_width), curses.A_BOLD)
        row += 2
        self.start_row = row
        for i, header in enumerate(self.headers):
            self.stdscr.addstr(row + i, 0, header.center(header_column_width), curses.A_BOLD)

        # Write the current contents to the GUI.
        for i, header in enumerate(self.headers):
            for d, coordaxis in zip(self.dividers, self.coordaxes):
                content = self.data[self.page_num][f'{header},{coordaxis}']
                self.stdscr.addstr(self.start_row + i, d + 1, content.center(self.column_width))

        # Usage instructions.
        self.stdscr.addstr(self.height - 5, 0, 'Page Down  ', curses.A_BOLD)
        self.stdscr.addstr('Next Axes')
        self.stdscr.addstr(self.height - 4, 0, 'Page Up    ', curses.A_BOLD)
        self.stdscr.addstr('Previous Axes')
        self.stdscr.addstr(self.height - 3, 0, 'Arrow Keys ', curses.A_BOLD)
        self.stdscr.addstr('Move Cursor')
        self.stdscr.addstr(self.height - 2, 0, 'Enter      ', curses.A_BOLD)
        self.stdscr.addstr('Update Plot')
        self.stdscr.addstr(self.height - 1, 0, 'Escape     ', curses.A_BOLD)
        self.stdscr.addstr('Quit')
        self.stdscr.move(self.start_row, self.dividers[0] + 1)

    ###########################################################################

    def process_keystroke(self, k):
        '''\
Whenever a valid key is pressed, perform the appropriate action.

Args:
    k: int (code of the key which was pressed)
'''

        if k is None:
            return

        (cursor_y, cursor_x) = self.stdscr.getyx()

        # Arrow keys.
        if k in {curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT}:
            if k == curses.KEY_UP and cursor_y > 0:
                cursor_y -= 1
            elif k == curses.KEY_DOWN and cursor_y < self.height - 1:
                cursor_y += 1
            elif k == curses.KEY_LEFT and cursor_x > 0:
                cursor_x -= 1
            elif k == curses.KEY_RIGHT and cursor_x < self.width - 1:
                cursor_x += 1
            self.stdscr.move(cursor_y, cursor_x)
            return

        # Home and End keys.
        if k == curses.KEY_HOME:
            self.stdscr.move(cursor_y, 0)
            return
        if k == curses.KEY_END:
            self.stdscr.move(cursor_y, self.width - 1)
            return

        # Page Up and Page Down keys.
        if k in {curses.KEY_NPAGE, curses.KEY_PPAGE}:
            if k == curses.KEY_NPAGE:
                self.page_num = (self.page_num + 1) % self.pages
            else:
                self.page_num = (self.page_num - 1) % self.pages
            self.draw_GUI()
            self.stdscr.move(cursor_y, cursor_x)
            return

        # Backspace key.
        if (k == curses.KEY_BACKSPACE
                and self.start_row <= cursor_y < self.start_row + 5
                and cursor_x > self.dividers[0] + 1
                and cursor_x != self.dividers[1] + 1
                and cursor_x != self.dividers[2] + 1):
            self.stdscr.addstr(cursor_y, cursor_x, '\b \b')
            return

        # A subset of the set of printable characters.
        c = chr(k)
        if (c in 'abcdefghijklmnopqrstuvwxyz' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' '0123456789' ' \\/$.-{}'
                and self.start_row <= cursor_y < self.start_row + 5
                and cursor_x > self.dividers[0]
                and cursor_x != self.dividers[1]
                and cursor_x != self.dividers[2]
                and cursor_x < self.width - 1):
            self.stdscr.addstr(cursor_y, cursor_x, c)
            return

        # Enter key. Write the data in the GUI to the dictionary and update the
        # plot.
        if k in {curses.KEY_ENTER, ord('\n'), ord('\r')}:
            for i, header in enumerate(self.headers):
               for d, coordaxis in zip(self.dividers, self.coordaxes):
                   self.data[self.page_num][f'{header},{coordaxis}'] = self.stdscr.instr(
                                                                           self.start_row + i,
                                                                           d + 1,
                                                                           self.column_width).decode().strip()
            self.stdscr.move(cursor_y, cursor_x)
            self.update()
            return

    ###########################################################################

    def update(self):
        '''\
Update the Matplotlib axes using the information entered in the GUI.
'''

        for coordaxis in self.coordaxes:
            ax = self.fig.axes[self.page_num]

            # Read the label.
            lbl = self.data[self.page_num][f'Label,{coordaxis}']
            try:
                getattr(ax, f'set_{coordaxis}label')(lbl)
            except AttributeError:
                pass

            # Read the limits and symbols.
            try:
                (first, last, step) = map(float, self.data[self.page_num][f'Limits,{coordaxis}'].split())
            except ValueError:
                continue
            symbolic = bool(self.data[self.page_num][f'Symbolic,{coordaxis}'])
            s = self.data[self.page_num][f'Symbol,{coordaxis}']
            if not s:
                symbolic = False
            try:
                v = float(self.data[self.page_num][f'Value,{coordaxis}'])
            except ValueError:
                v = 0
                symbolic = False
            limit(ax, coordaxis, symbolic, s, v, first, last, step)

        self.canvas.draw_idle()

    ###########################################################################

    def main(self, stdscr):
        '''\
Implement the main GUI loop.
'''

        self.stdscr = stdscr
        (self.height, self.width) = stdscr.getmaxyx()
        stdscr.clear()
        stdscr.refresh()
        self.draw_GUI()

        k = None
        while True:
            self.process_keystroke(k)
            stdscr.refresh()

            # Exit if the Escape key is pressed.
            k = stdscr.getch()
            if k == 27:
                return

            if self.fig.number not in plt.get_fignums():
                message = ('Cannot update a figure which has been closed.')
                raise RuntimeWarning(message)
                return

###############################################################################

def _maximise(fig):
    '''\
Maximise a figure window. (This is not the same as going full-screen.)

Args:
    fig: matplotlib.figure.Figure
'''

    backend = mpl.get_backend()
    manager = fig.canvas.manager
    if backend in {'TkAgg', 'TkCairo'}:
        if platform.system() in {'Darwin', 'Windows'}:
            manager.window.state('zoomed')
        else: # 'Linux'
            manager.window.attributes('-zoomed', True)
    elif backend in {'GTK3Agg', 'GTK3Cairo'}:
        manager.window.maximize()
    elif backend in {'WXAgg', 'WXCairo'}:
        fig.show()
        manager.frame.Maximize(True)
    elif backend in {'Qt5Agg', 'Qt5Cairo'}:
        manager.window.showMaximized()

###############################################################################

def show(fig=None):
    '''\
Display one or more figures.

If this function is called without arguments, it is similar to calling
`matplotlib.pyplot.show': all figures will be displayed.

If this function is called with an existing figure as an argument, that figure
will be displayed, along with an interactive GUI, which can be used to
manipulate some plot elements of all axes in said figure. This GUI will be
emulated in the terminal, so ensure that you don't write anything to standard
output while the GUI is active. Using this feature requires that curses be
installed.

Args:
    fig: matplotlib.figure.Figure
'''

    if fig is None:
        figs = map(plt.figure, plt.get_fignums())
    else:
        figs = [fig]
    for _fig in figs:
        _maximise(_fig)

    if fig is None:
        plt.show()
        return

    if not has_curses:
        message = ('The curses module could not be imported, so the '
                   'interactive plotting feature is unavailable.')
        raise RuntimeWarning(message)
        plt.show()
        return

    interactive = _Interactive(fig)
    interactive.start()
    plt.show()
    interactive.join()

