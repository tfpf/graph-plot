import fractions
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.projections as mprojections
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import multiprocessing as mp
import numpy as np
import platform
import time
import tkinter as tk
import tkinter.font as tkfont
import tkinter.ttk as ttk
import weakref

###############################################################################

_gid = weakref.WeakKeyDictionary()

_system = platform.system()
if _system == 'Darwin':
    mpl.use('TkAgg')

###############################################################################

def _font_tuple():
    font_family = mpl.rcParams['font.family'][0]
    if _system == 'Darwin':
        font_size = 18
    else:
        font_size = 12
    font_style = tkfont.NORMAL

    return (font_family, font_size, font_style)

###############################################################################

def _iprint(items, columns=3, align_method='center'):
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
        # other patches. Since the original list (namely `ax.patches') gets
        # mutated whenever any patch is removed, make a shallow copy of it.
        gid = _gid[fig]
        for patch in ax.patches.copy():
            if patch.get_gid() == gid:
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

        # If the x-axis labels will contain fractions, increase the padding
        # slightly. Do not do this for polar plots (the spacing is already
        # quite good). Do not do this for three-dimensional plots, either
        # (Matplotlib messes up the spacing).
        if ax.name == 'rectilinear' and coordaxis == 'x' and not all(isinstance(t, int) for t in [first, last, step]):
            ax.tick_params(axis=coordaxis, which='major', pad=20)
            for label in labels_getter():
                label.set_horizontalalignment('center')
                label.set_verticalalignment('center')
        else:
            ax.tick_params(axis=coordaxis, which='major', pad=9.9)

    # Case 2: allow tick labels to be set automatically.
    else:
        if all(arg is not None for arg in [first, last, step]):
            ticks_setter(np.arange(first, last + step / 2, step))
        if all(arg is not None for arg in [first, last]):
            limits_setter(first, last)

        # Generate the axis labels in case they were erased because of a
        # previous call to this function.
        if ax.name in {'rectilinear', '3d'} or ax.name == 'polar' and coordaxis == 'y':
            axis.set_major_formatter(mticker.ScalarFormatter())
        elif ax.name == 'polar' and coordaxis == 'x':
            axis.set_major_formatter(mprojections.polar.ThetaFormatter())

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

def polish(ax, labels=None, title=None, suptitle=None):
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
        ax.xaxis.set_tick_params(pad=1, **kwargs)
        ax.yaxis.set_tick_params(pad=1, **kwargs)
        ax.zaxis.set_tick_params(pad=1, **kwargs)
        ax.set_facecolor('white')

        # A new line character is used here because the `labelpad' argument
        # does not work.
        for label, coordaxis in zip(labels, 'xyz'):
            getattr(ax, f'set_{coordaxis}label')(f'\n{label}', labelpad=10, linespacing=3)

    elif ax.name == 'rectilinear':
        kwargs = {'alpha': 0.6, 'linewidth': 1.2, 'color': 'gray'}
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
        ax.grid(b=True, which='major', linewidth=0.8, linestyle=':')
        ax.grid(b=True, which='minor', linewidth=0.1, linestyle='-')
        ax.minorticks_on()
    elif ax.name == '3d':
        ax.grid(b=True, which='major', linewidth=0.3, linestyle='-')

    # Key a unique ID with the figure instance in the global weak key
    # dictionary. Doing so ensures that the following operations are performed
    # only once.
    fig = ax.figure
    canvas = fig.canvas
    if any(_ax.name == 'polar' for _ax in fig.axes) and fig not in _gid:
        _gid[fig] = f'cp_{time.time_ns()}_{np.random.randint(100, 999)}'

        # Connect the resize event of the canvas to a callback which
        # illustrates the axes of coordinates of all polar graphs (if any) in
        # this figure.
        canvas.mpl_connect('resize_event', _draw_polar_patches)

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
    ax: Matplotlib axes instance
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

class _Frame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, bg='#333333', relief=tk.RAISED)

class _Label(tk.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, bg='#333333', fg='#CCCCCC', font=_font_tuple())

class _Entry(tk.Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, bg='#333333', fg='#CCCCCC', insertbackground='#CCCCCC',
                         disabledbackground='#CCCCCC', font=_font_tuple())

class _Checkbutton(tk.Checkbutton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, bg='#333333', borderwidth=0, highlightthickness=0)

class _Style(ttk.Style):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme_create('customplot', parent='alt',
                          settings={'TNotebook.Tab':
                                    {'configure': {'background': '#333333',
                                                   'foreground': '#CCCCCC',
                                                   'font':       _font_tuple(),
                                                   'padding':    [10, 5]},
                                     'map':       {'background': [('selected', '#CCCCCC')],
                                                   'foreground': [('selected', '#333333')]}},
                                    'TNotebook':
                                    {'configure': {'background':  '#333333',
                                                   'foreground':  '#CCCCCC',
                                                   'font':        _font_tuple(),
                                                   'tabposition': tk.NSEW}}})

###############################################################################

class _Interactive(_Frame):
    '''\
Interactively adjust some plot elements of a Matplotlib axes instance via a
GUI window.

Constructor Args:
    fig: matplotlib.figure.Figure
    parent: tkinter.Tk or tkinter.Toplevel
    queue: multiprocessing.Queue
'''

    padx, pady = 10, 10
    headers = ['Symbolic', 'Symbol', 'Value', 'Limits', 'Label']

    ###########################################################################

    def __init__(self, fig, parent, queue=None):
        super().__init__(parent)
        self.fig = fig
        self.queue = queue
        self.widgets = [{} for _ in range(len(fig.axes))]

        icon_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x14\x00\x00\x00\x14\x08\x06\x00\x00\x00\x8d\x89\x1d\r\x00\x00\x00IIDATx\x9cc\xfc\xff\xff?\x039`\xd6\xad\xd7X52\x91e\x1a\x1e@u\x03Y\xde\xc9\xaabu\xba\xd0\xe3\xdb\x8c\xe4\x188\xf8\xbd<\xf8\rd\xc1'\xa9\xbc\xc9\x17k\x84\xdd\xf5\xdb\x8c3\xc2\x06\xbf\x97G\r\x1c5pX\x1a\x08\x00\xdfj\x0e\x87\x02\xbc\xb5L\x00\x00\x00\x00IEND\xaeB`\x82"
        parent.iconphoto(True, tk.PhotoImage(data=icon_data))
        parent.resizable(False, False)
        parent.title(f'Options for {fig.canvas.manager.get_window_title()} at 0x{id(self.fig):X}')

        style = _Style(parent)
        style.theme_use('customplot')

        self.notebook = ttk.Notebook(self)

        # Create one notebook page for each Matplotlib axes in the figure.
        for i, ax in enumerate(self.fig.axes):
            frame = _Frame(self.notebook)
            frame.grid_columnconfigure(0, weight=1)

            # Upper part of the page. Allows the user to manipulate the axes of
            # coordinates.
            upper = _Frame(frame, borderwidth=3)

            # Header labels for the same.
            for j, header in enumerate(self.headers, 1):
                row_header = _Label(upper, text=header)
                row_header.grid(row=j, column=0, padx=self.padx, pady=self.pady)
            for j, coordaxis in enumerate('xyz', 1):
                column_header = _Label(upper, text=f'{coordaxis}-axis')
                column_header.grid(row=0, column=j, padx=self.padx, pady=self.pady)

            # Widgets organised according to above headers.
            for j, coordaxis in enumerate('xyz', 1):
                check_variable = tk.BooleanVar()
                check_button = _Checkbutton(upper, variable=check_variable, offvalue=False, onvalue=True)
                check_button.configure(command=self.put_axes_data)
                check_button.grid(row=1, column=j, padx=self.padx, pady=self.pady)
                self.widgets[i][f'{coordaxis},Symbolic'] = check_variable

                for k, header in enumerate(self.headers[1 :], 2):
                    entry = _Entry(upper)
                    entry.bind('<Return>', self.focus_out)
                    entry.bind('<FocusOut>', self.put_axes_data)
                    entry.grid(row=k, column=j, padx=self.padx, pady=self.pady)
                    self.widgets[i][f'{coordaxis},{header}'] = entry

            # Set defaults for some of the above entries.
            for coordaxis in 'xyz':
                try:
                    self.widgets[i][f'{coordaxis},Label'].insert(0, getattr(ax, f'get_{coordaxis}label')())
                    self.widgets[i][f'{coordaxis},Symbol'].insert(0, r'\pi')
                    self.widgets[i][f'{coordaxis},Value'].insert(0, f'{np.pi}')
                except AttributeError:
                    pass

            upper.grid(row=0, sticky=tk.NSEW)
            upper.grid_columnconfigure(0, weight=1)
            upper.grid_columnconfigure(1, weight=1)
            upper.grid_columnconfigure(2, weight=1)
            upper.grid_columnconfigure(3, weight=1)

            # Lower part of the page. Allows the user to place Matplotlib text
            # objects. This will not be provided for three-dimensional plots,
            # because the `set_position' method of `Text3D' objects does not
            # work as expected
            if ax.texts and ax.name != '3d':
                lower = _Frame(frame, borderwidth=3)

                # Header labels and entries.
                for j, text in enumerate(ax.texts):
                    prompt = _Label(lower, text=f'Location of {text.get_text()}')
                    prompt.grid(row=j, column=0, padx=self.padx, pady=self.pady)
                    response = _Entry(lower, name=f'{j}')
                    response.insert(0, ' '.join(f'{coord}' for coord in text.get_position()))
                    response.bind('<Return>', self.focus_out)
                    response.bind('<FocusOut>', self.put_text_data)
                    response.grid(row=j, column=1, padx=self.padx, pady=self.pady)

                    lower.grid_rowconfigure(j, weight=1)

                lower.grid(row=1, sticky=tk.NSEW)
                lower.grid_columnconfigure(0, weight=1)
                lower.grid_columnconfigure(1, weight=1)

            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(1, weight=1)
            self.notebook.add(frame, text='')

        self.notebook.pack()
        self.pack()
        self.update()

        titles = [None] * len(fig.axes)
        for i, ax in enumerate(fig.axes):
            title = ax.get_title()
            if not title or title.isspace():
                titles[i] = '<untitled>'
            else:
                titles[i] = title

        # The sum of the widths of the titles of the notebook tabs must not
        # exceed a certain fraction of the width of the window.
        width = self.winfo_width() * 0.9

        # During each iteration of the below loop, truncate the widest title.
        # Keep doing this until the condition described above is satisfied.
        measurer = lambda title: tkfont.Font(font=_font_tuple()).measure(title)
        measures = list(map(measurer, titles))
        while sum(measures) > width:
            i = measures.index(max(measures))
            halfway = len(titles[i]) // 2
            titles[i] = f'{titles[i][: halfway - 1]}…{titles[i][halfway + 2 :]}'
            measures = list(map(measurer, titles))

        for i in range(len(fig.axes)):
            self.notebook.tab(i, text=titles[i])
        self.update()

    ###########################################################################

    def focus_out(self, event):
        self.notebook.focus_set()

    ###########################################################################

    def put_axes_data(self, event=None):
        i = self.notebook.index('current')
        data = {key: val.get() for key, val in self.widgets[i].items()}
        data['index'] = i

        if mpl.get_backend() in {'TkAgg', 'TkCairo'}:
            _set_axes_data(self.fig, data)
        else:
            self.queue.put(data)

    ###########################################################################

    def put_text_data(self, event):
        entry = event.widget
        coords = entry.get()
        j = int(entry.winfo_name())
        i = self.notebook.index('current')
        data = (i, j, coords)

        if mpl.get_backend() in {'TkAgg', 'TkCairo'}:
            _set_text_data(self.fig, data)
        else:
            self.queue.put(data)

###############################################################################

class _InteractiveWrapper(mp.Process):
    def __init__(self, fig, queue):
        super().__init__()
        self.fig = fig
        self.queue = queue
    def run(self):
        root = tk.Tk()
        _Interactive(self.fig, root, self.queue)
        root.mainloop()

###############################################################################

def _set_axes_data(fig, data):
    ax = fig.axes[data['index']]

    for coordaxis in 'xyz':
        try:
            getattr(ax, f'set_{coordaxis}label')(data[f'{coordaxis},Label'])
        except AttributeError:
            pass

        # Disable symbolic labelling if the symbol value is not specified.
        symbolic = data[f'{coordaxis},Symbolic']
        try:
            v = float(eval(data[f'{coordaxis},Value']))
        except (NameError, SyntaxError, ValueError):
            symbolic = False
            v = 0

        # Disable symbolic labelling if no symbol is specified.
        s = data[f'{coordaxis},Symbol']
        if s == '':
            symbolic = False

        try:
            first, last, step = [float(eval(i)) for i in data[f'{coordaxis},Limits'].split()]
            limit(ax, coordaxis, symbolic, s, v, first, last, step)
        except (NameError, SyntaxError, ValueError, ZeroDivisionError):
            pass

    if fig.stale:
        fig.canvas.draw()

###############################################################################

def _set_text_data(fig, data):
    i, j, coords = data

    try:
        coords = tuple(float(eval(coord)) for coord in coords.split())
        fig.axes[i].texts[j].set_position(coords)
    except (IndexError, NameError, SyntaxError, ValueError):
        pass

    if fig.stale:
        fig.canvas.draw()

###############################################################################

def show(fig=None):
    '''\
Display one or more figures.

If this function is called without arguments, it is similar to calling
`matplotlib.pyplot.show': all figures will be displayed. The difference is that
these figures will all be maximised.

If this function is called with an existing figure as an argument, that figure
will be displayed, along with an interactive GUI, which can be used to
manipulate some plot elements of all axes in said figure.

Args:
    fig: matplotlib.figure.Figure
'''

    if fig is None:
        figs = map(plt.figure, plt.get_fignums())
    else:
        figs = [fig]

    # Maximise the figure or figures. (This is not the same as going
    # fullscreen.)
    backend = mpl.get_backend()
    if backend in {'TkAgg', 'TkCairo'}:
        if _system in {'Darwin', 'Windows'}:
            for _fig in figs:
                _fig.show()
                _fig.canvas.manager.window.state('zoomed')
        else:
            for _fig in figs:
                _fig.canvas.manager.window.attributes('-zoomed', True)
    elif backend in {'GTK3Agg', 'GTK3Cairo'}:
        for _fig in figs:
            _fig.canvas.manager.window.maximize()
    elif backend in {'WXAgg', 'WXCairo'}:
        for _fig in figs:
            _fig.canvas.manager.frame.Maximize(True)
    elif backend in {'Qt5Agg', 'Qt5Cairo'}:
        for _fig in figs:
            _fig.canvas.manager.window.showMaximized()

    if fig is None:
        plt.show()
        return

    canvas = fig.canvas
    fig.show()

    # If Matplotlib is using a Tkinter-based backend, make the interactive GUI
    # a child window of the figure.
    if backend in {'TkAgg', 'TkCairo'}:
        toplevel = tk.Toplevel(canvas.get_tk_widget())
        interactive = _Interactive(fig, toplevel)
        interactive.after(2000, toplevel.lift)
        plt.show()

    # If Matplotlib is not using a Tkinter-based backend, run the interactive
    # GUI in a separate process. It will communicate with this process via a
    # queue.
    else:
        queue = mp.Queue()
        interactive_wrapper = _InteractiveWrapper(fig, queue)
        interactive_wrapper.start()

        while plt.fignum_exists(fig.number):
            canvas.start_event_loop(0.1)
            if queue.empty():
                continue

            data = queue.get()
            if isinstance(data, tuple):
                _set_text_data(fig, data)
            else:
                _set_axes_data(fig, data)

    # Once the figure is closed, the interactive GUI should be closed
    # automatically.
    try:
        interactive_wrapper.terminate()
    except NameError:
        pass

