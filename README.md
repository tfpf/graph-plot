# CustomPlot
A wrapper around Matplotlib; it can be used to plot beautiful,
publication-quality graphs.

# Requirements
* Python (version 3.8 or higher)
* Matplotlib (version 3.3.3 or higher)
* NumPy (version 1.17 or higher)

# Usage
There are a few examples provided. They should make everything clear.

# Notes

### Custom Fonts
It is possible to use a font of your choice in the plot. For instance, I have
set this program up to use Cochineal and Cascadia Code.

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

### DPI Settings
If the plot doesn't look quite right, try playing around with the DPI settings.
You can see how this is used in the file `example.py`.

### Essential Discontinuities
In case your graph has essential discontinuities (also called infinite
discontinuities), like those present in the graph of y = tan x, a superfluous
vertical line is automatically drawn at each point of discontinuity. This is
simply a result of the plotting algorithm used by graph plotters.

However, CustomPlot ensures that these superfluous lines are erased. As a
side-effect, sometimes, functions with a very large magnitude of slope are also
partially erased. If you face this problem, try increasing the value of
`maximum_diff` in the file `customplot.py`.

