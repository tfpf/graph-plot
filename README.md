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

## Fonts
Matplotlib allows using fonts of your choice in the plot. For instance, I have
set this program up to use Cochineal. I highly recommend using a good custom
font, because (in my opinion) it can significantly improve the appearance of
your plot.

In case you want nothing to do with fonts, you can ignore this section
entirely. Matplotlib will warn you that Cochineal is not installed (if it
isn't), and fall back to the default font. (Functionality remains unaffected.)

### Using a Custom Font
Let's say you want to use Libre Baskerville.
* Download the font files for Libre Baskerville. (It is a Google font. So, it
will probably be freely available as a package containing four or more files
with the extension `.ttf`, or perhaps `.otf`).
* Create a new directory `~/.fonts/LibreBaskerville` and put the
above-mentioned font files in that directory.
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

### Using a Built-in Font
You have a choice of fonts available out of the box. My suggestion is to use a
serif font. (Once again, only the relevant lines are shown.)
```python
...
font.family: serif
...
mathtext.fontset: dejavuserif
...
```

## XKCD-style Plots
An XKCD-style graph plot looks best when it uses the Humor Sans font. You can
either install it via the command line
```shell
sudo apt install fonts-humor-sans
```

or do it manually, as described in the previous section: by downloading the
font files, putting them in `~/.fonts/HumorSans`, and deleting the Matplotlib
font cache.

## DPI Settings
If the plot doesn't look quite right, try playing around with the DPI parameter
before adjusting anything else. In the file `dandy.mplstyle`, search for
`figure.dpi` and change the value next to it.

In my experience, a value of 120 produces pretty graphs on a 1080p screen,
while a 768p screen requires a value of 96 or so.

## Essential and Jump Discontinuities
There are two types of discontinuities most graph plotters struggle with:
* essential discontinuities (like those in the graph of _y_ = tan _x_); and
* jump discontinuities (like those in the graph of _y_ = sgn _x_).

A vertical line is automatically drawn at each point of discontinuity. This is
simply a result of the plotting algorithm used by graph plotters.

However, CustomPlot ensures that these superfluous vertical lines are erased.
As a side-effect, sometimes, functions with a very large magnitude of slope are
also partially erased. If you face this problem, increase the value of
`maximum_diff` in the file `customplot.py` until you get satisfactory results.

