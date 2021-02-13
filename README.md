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
It is possible to use a font of your choice in the plot. For instance, I have
set this program up to use Cochineal and Cascadia Code. If you don't have these
fonts installed, Matplotlib will fall back to the default fonts and issue a
warning. (Functionality remains unaffected.)

Let's say you want to use a font called MyAwesomeFont. This is what you have to
do.
* Download MyAwesomeFont. It will probably be available as a package containing
four or more files with the extension `.otf` (or perhaps `.ttf`).
* Put these files in `~/.fonts/MyAwesomeFont` (do not modify the files).
* Find out where Matplotlib stores its cache.
```python
import matplotlib
print(matplotlib.get_cachedir())
```
* Delete all font-related cache files in that location.
* Open the file `dandy.mplstyle` and search for `Cochineal`. Replace it,
wherever it appears, with `MyAwesomeFont`. Also replace `Cascadia Code` with
`MyAwesomeFont`. In other words, the contents of `dandy.mplstyle` should be
something like this.
```
...
font.family: MyAwesomeFont
...
mathtext.cal: MyAwesomeFont
mathtext.rm : MyAwesomeFont
mathtext.tt : MyAwesomeFont
mathtext.it : MyAwesomeFont:italic
mathtext.bf : MyAwesomeFont:bold
mathtext.sf : MyAwesomeFont
...
```

After this, any text in any new graph you plot will use MyAwesomeFont.

On the other hand, if you don't want to use a custom font and are okay with the
defaults, but also want to remove the warnings issued because of missing fonts,
ignore the previous instructions and modify `dandy.mplstyle` to look something
like this.
```
...
font.family: serif
...
mathtext.fontset: cm
...
```

### DPI Settings
If the plot doesn't look quite right, try playing around with the DPI settings.
You can see how this is used in the file `examples.py`.

### Essential Discontinuities and Jump Discontinuities
There are two types of discontinuities most graph plotters struggle with:
* essential discontinuitues (like those in the graph of y = tan x); and
* jump discontinuitues (like those in the graph of y = sgn x).

A vertical line is automatically drawn at each point of discontinuity. This is
simply a result of the plotting algorithm used by graph plotters.

However, CustomPlot ensures that these superfluous vertical lines are erased.
As a side-effect, sometimes, functions with a very large magnitude of slope are
also partially erased. If you face this problem, increase the value of
`maximum_diff` in the file `customplot.py` until you get satisfactory results.

