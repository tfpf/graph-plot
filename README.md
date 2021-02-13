# CustomPlot
A wrapper around Matplotlib; it can be used to plot beautiful,
publication-quality graphs.

# Requirements
* Python (version 3.8 or higher)
* Matplotlib (version 3.3.3 or higher)
* NumPy (version 1.17 or higher)

# Usage
Clone or download this repository. Open a terminal window to the clone or
download location. Several examples provided in `examples.py` should make
everything clear. Run it
```shell
python3 examples.py
```
and tinker with the code if you'd like to.

A good way to start plotting your own graphs might be to copy parts of the code
in `examples.py` and make modifications to the copy.

# Notes

### Custom Fonts
Matplotlib allows using fonts of your choice in the plot. For instance, I have
set this program up to use Cochineal. If you don't have this font installed,
Matplotlib will fall back to the default fonts and issue a warning.
(Functionality remains unaffected.) I highly recommend using a good custom
font, because (in my opinion) it can significantly improve the appearance of
your plot.

Let's say you want to use Libre Baskerville. Here are the steps.
* Download the font files for Libre Baskerville. (It is a Google font. So, it
will probably be freely available as a package containing four or more files
with the extension `.ttf` (or perhaps `.otf`).
* Create a directory `~/.fonts/LibreBaskerville` and put those files there.
* Find out where Matplotlib stores its cache.
```python
import matplotlib
print(matplotlib.get_cachedir())
```
* Delete all font-related cache files in that location.
* Open the file `dandy.mplstyle` and search for `Cochineal`. Replace it,
wherever it appears, with `Libre Baskerville`. In other words, the contents of
`dandy.mplstyle` should be something like this. (Only the relevant lines are
shown.)
```python
...
font.family: Libre Baskerville
...
mathtext.cal: Libre Baskerville:bold:italic
mathtext.rm : Libre Baskerville
mathtext.tt : Libre Baskerville
mathtext.it : Libre Baskerville:italic
mathtext.bf : Libre Baskerville:bold
mathtext.sf : Libre Baskerville
...
```

After this, any text in any new graph you plot will use Libre Baskerville. If
you feel confident, you can experiment with different fonts (i.e. a monospace
font for `mathtext.tt`, a calligraphy font for `mathtext.cal` and a sans-serif
font for `mathtext.sf`).

Alternatively, if you don't want to use a custom font and are okay with the
defaults, but also want to remove the warnings issued because of missing fonts,
ignore the previous instructions and modify `dandy.mplstyle` to look something
like this. (Once again, only the relevant lines are shown.)
```python
...
font.family: serif
...
mathtext.fontset: cm
...
```

### DPI Settings
If the plot doesn't look quite right, try playing around with the DPI parameter
before adjusting anything else. In the file `dandy.mplstyle`, search for
`figure.dpi` and change the number next to it.

### Essential Discontinuities and Jump Discontinuities
There are two types of discontinuities most graph plotters struggle with:
* essential discontinuities (like those in the graph of _y_ = tan _x_); and
* jump discontinuities (like those in the graph of _y_ = sgn _x_).

A vertical line is automatically drawn at each point of discontinuity. This is
simply a result of the plotting algorithm used by graph plotters.

However, CustomPlot ensures that these superfluous vertical lines are erased.
As a side-effect, sometimes, functions with a very large magnitude of slope are
also partially erased. If you face this problem, increase the value of
`maximum_diff` in the file `customplot.py` until you get satisfactory results.

