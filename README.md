# customplot
A wrapper around Matplotlib; it can be used to plot beautiful,
publication-quality graphs.

# Requirements
* Python (version 3.8 or higher)
* Matplotlib (version 3.0 or higher)
* NumPy (version 1.17 or higher)

# Usage
There are a few examples provided. They should make everything clear.

# Notes

## Custom Fonts
It is possible to use a font of your choice in the plot. This is how you can do
it. (Let's say you want to use the Cochineal font.)
* Download the OTF files. (TTF files will also work.)
* Put these files in `~/.fonts/Cochineal` (do not modify the files).
* Find out where Matplotlib stores its cache.
```python
import matplotlib
print(matplotlib.get_cachedir())
```
* Delete all font-related cache files in that location.
* Open the file `dandy.mplstyle` and search for `font.family`. Set this to
`Cochineal`. In the same file, also set all `mathtext` parameters to
`Cochineal`.

After this, any text in any new graph you plot will be in Cochineal.

## DPI Settings
If the plot doesn't look quite right, try playing around with the DPI settings.
You can find it in the file `dandy.mplstyle` (search for `figure.dpi`).


