"""
Matplotlib. Wrapper. Smart. Tufte. Pythonic.

You can use either the plot classes (BarPlot, MatrixPlot, Histogram, etc) or
call `plot(data)` and let it figure out what to do. This library tries its best
to automatically do the right thing.

If you get
"FutureWarning: elementwise comparison failed; returning scalar
instead, but in the future will perform elementwise comparison"
It's not my fault. Check https://github.com/matplotlib/matplotlib/issues/5209 .
A fix should be released soon
"""

import matplotlib
from matplotlib import pyplot
from collections import defaultdict, Counter
import math

# For flexibility purposes we accept a lot of data formats.
# This helps distinguishing them.
is_list = lambda a: hasattr(a, '__iter__') and not isinstance(a, str)

# Use ggplot style, which I personally find much better than the default.
pyplot.style.use('ggplot')

# Draws axis ticks outside the axis line. Not necessary if using ggplot style.
#matplotlib.rcParams['xtick.direction'] = 'out'
#matplotlib.rcParams['ytick.direction'] = 'out'

class BasePlot(object):
    """
    BasePlot doesn't actually draw anything, but configures general layout,
    formats data to a list of (key, value) tuples, and implements the
    `show` and `save` methods.
    """
    grid = False
    title = ''
    xlabel = ''
    ylabel = ''

    @staticmethod
    def _format_data(data):
        """
        Given an arbitrary data set, tries to reshape it to [(key, value)].

        Accepted formats:
        - [1, 2, 3] -> [(0, 1), (1, 2), (2, 3)]
        - [(5, 1), (10, 2), (11, 3)] -> [(5, 1), (10, 2), (11, 3)]
        - [('a', 1), ('b', 2), ('c', 3)] -> [('a', 1), ('b', 2), ('c', 3)]
        - {5: 1, 10: 2, 11: 3} -> [(5, 1), (10, 2), (11, 3)]
        - {'a': 1, 'b': 2, 'c': 3} -> [('a', 1), ('b', 2), ('c', 3)]
        - [[1, 2, 3], [4, 5, 6], [7, 8, 9]] -> [(None, [1,...]), (None, [4,...]),...]
        """
        if isinstance(data, dict):
            # Dictionary.
            return list(data.items())
        elif is_list(data):
            data = list(data)
            if len(data) and is_list(data[0]):
                if len(data[0]) == 2:
                    # List of (key, value) pairs.
                    return data
                else:
                    # Matrix.
                    return [(None, line) for line in data]
            else:
                # List of values.
                return list(enumerate(data))
        else:
            raise ValueError('Unexpected data type {}'.format(type(data)))

    def __init__(self, data, **options):
        self.data = self._format_data(data)
        self._apply_options(options)

    def _apply_options(self, options):
        """ Loads settings from the given dictionary. """
        for option, value in options.items():
            if not hasattr(self, option):
                raise ValueError('Invalid option: {}'.format(option))
            setattr(self, option, value)

    def _draw_plot(self, fig=None, ax=None):
        """
        Make or configure the `figure` and `plot` instances, with correct
        spacing, ticks, labels, etc.
        """
        keys = [a for a, b in self.data]
        values = [b for a, b in self.data]

        if fig is None:
            fig = pyplot.figure(figsize=(12, 9))
            ax = pyplot.subplot(111)

        # Hide frame lines on top and right sides.
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Ensure ticks only on left and bottom, removing top and right ticks.
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

        # Show full value in ticks, instead of using an offset.
        ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter(useOffset=False))
        ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter(useOffset=False))

        # Handle non-numeric data on the x-axis.
        if isinstance(keys[0], str):
            # Heuristic to rotate label to fit if necessary.
            rotation = 30 if len(''.join(keys)) > 80 else 0
            s = sorted(set(keys))
            num_keys = [s.index(key) for key in keys]
            ax.set_xticks(num_keys)
            ax.set_xticklabels(keys, rotation=rotation)
            keys = num_keys

        self._draw(keys, values, ax)
        # For unknown reasons must be called *after* drawing. Otherwise the
        # scale goes completely bonkers and doesn't show the data.
        self._setup_margins(keys, values, ax)
        
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        ax.grid(self.grid)

        # Resize plot to fill available space.
        fig.tight_layout()

    def _setup_margins(self, keys, values, ax):
        """ Gives a little space between the data and the axis. """
        ax.margins(x=.02, y=0.02)

        # Apply Y limits and margins manually to avoid truncating unless
        # absolutely necessary. All magical constants were eyeballed.
        max_data = max(values)
        min_data = min(values)
        distance = (max_data - min_data) or abs(min_data)
        if 0 < distance < 0.01 * min_data:
            ax.set_ylim(min_data - distance * 0.4, max_data + distance * 0.4)
        else:
            if min_data < 0:
                ax.set_ylim(ymin=min_data-distance*0.02)
            else:
                ax.set_ylim(ymin=-distance*0.02)

    def show(self):
        """
        Opens a GUI window showing the plot, blocking the call until the window is closed.
        """
        self._draw_plot()
        pyplot.show()
        pyplot.close()

    def save(self, path):
        """
        Saves the current plot to the given path. The format is decided based
        on the extension. PDF format is available and generates vector
        graphics.
        """
        self._draw_plot()
        # Remove extraneous whitespace.
        pyplot.savefig(path, bbox_inches="tight")

class TimePlot(BasePlot):
    pass

class BarPlot(BasePlot):
    """
    Simple graph of rectangular bars. By default there is a small padding
    between the bars. If there are fewer than `max_direct_labels` data points,
    the y-values are rendered at the top of each bar and the y-axis omitted.
    """
    bars_width = 0.9
    max_direct_labels = 10

    def _draw(self, keys, values, ax):
        """ Draws the bar plot and transfers y-values to bars if possible. """
        rects = ax.bar(keys, values, width=self.bars_width, align='center')

        # If there are few bars, hide the Y-axis and put value labels directly
        # on the bars themselves.
        if len(rects) <= self.max_direct_labels:
            # hide both spines, but keep X-axis labels.
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.get_yaxis().set_visible(False)
            ax.xaxis.set_ticks_position('none')
            # Uses rect geometry to figure out where to place labels. Attempts
            # to place at the top of the bar, still inside the fill, but some
            # bars are too short (or negative) and the label must be placed
            # outside.
            max_height = max(rect.get_height() for rect in rects)
            for rect in rects:
                height = rect.get_height()
                padding = max_height * 0.03
                if height > padding * 2:
                    y = rect.get_y()+height - padding
                else:
                    y = rect.get_y()+height + padding * 2
                value = round(rect.get_y() or height, 4)
                ax.text(rect.get_x() + rect.get_width()/2., y, value, ha='center', va='top')

class Histogram(BarPlot):
    """
    A BarPlot that automatically counts distribution from the given data
    samples, and displays with no padding between bars.
    """
    max_bins = 40
    def __init__(self, samples, bin=None, **options):
        """
        Creates a new histogram from the given samples. `bin` is the size of
        each class, used to aggregate values, and defaults to an
        algorithmically chosen value with up to `self.max_bins` bins.
        """
        samples_set = sorted(set(samples))
        if bin is None:
            difs = [b - a for a, b in zip(samples_set, samples_set[1:])]
            min_dif = min(difs)
            max_dif = samples_set[-1] - samples_set[0]
            # Use the smallest difference as bin size, up to a maximum of 40.
            bin = max(min_dif, max_dif / self.max_bins)

        data = {k*bin: v for k, v in Counter(int(s/bin) for s in samples).items()}
        self.bars_width = bin
        super().__init__(data, **options)

class ScatterPlot(BasePlot):
    """ Draws a small circle on the (x, y) position of each data point. """
    def _draw(self, keys, values, ax):
        ax.scatter(keys, values)

class LinePlot(BasePlot):
    """
    Like ScatterPlot, but draws a line between the data points. If `self.fill`
    is True, the line forms a solid area up to the x-axis.
    """
    fill = False

    def _draw(self, keys, values, ax):
        if self.fill:
            ax.fill_between(keys, values)
        else:
            ax.plot(keys, values)

class MatrixPlot(BasePlot):
    """
    A 2D plot of intensity values. Data must be a list of lists or equivalent.
    `self.colors` is the colormap ( http://matplotlib.org/examples/color/colormaps_reference.html ).
    """
    colors = 'cubehelix'
    def _draw(self, keys, values, ax):
        im = ax.imshow(values, interpolation='nearest', cmap=pyplot.get_cmap(self.colors))
        pyplot.colorbar(im, ax=ax)

    def _setup_margins(self, keys, values, ax):
        pass
        
def plot(data, **options):
    """
    Given the raw data, selects the most appropriate type of plot and
    constructs it with the given options. Note: it does not count
    occurrences from samples. Use the `Histogram` class for that.
    """
    data = BasePlot._format_data(data)
    if not len(data):
        return LinePlot(data, **options)

    keys = [a for a, b in data]
    if is_list(data[0][1]) and len(data[0][1]) > 2:
        return MatrixPlot(data, **options)
    elif len(keys) != len(set(keys)):
        return ScatterPlot(data, **options)
    elif isinstance(data[0][0], str):
        return BarPlot(data, **options)
    else:
        return LinePlot(data, **options)

def show_grid(plots, nrows=None):
    """
    Given a list or a matrix of plots, draws them in a grid layout and displays
    in a GUI window. If the list is flat, number of rows and columns is deduced
    automatically.
    """
    if is_list(plots[0]):
        nrows = len(plots)
        plots = sum(plots, [])

    if len(plots) == 1:
        return plots[0].show()

    plots = list(plots)
    if nrows == None:
        nrows = int(math.sqrt(len(plots)))
    ncols = math.ceil(len(plots) / nrows)

    fig, axes = pyplot.subplots(nrows=nrows, ncols=ncols)
    for ax, p in zip(axes.flat, plots):
        p._draw_plot(fig, ax)

    pyplot.show()
    pyplot.close()

if __name__ == '__main__':
    from random import randint, random, sample, choice
    from string import ascii_lowercase

    plots = [
        plot([('Shanghai', 24256800), ('Beijing', 21516000), ('Lagos', 21324000), ('Tokyo', 13297629), ('São Paulo', 11895893)]),
        Histogram([random()*random()+random() for i in range(1000)]),
        Histogram([randint(1000, 1010) for i in range(1000)]),
        plot([(''.join(sample(ascii_lowercase, 5)), random()) for i in range(17)]),
        plot([(choice('abcde'), random()*i) for i in range(50)]),
        plot([(randint(0, 100), i * random()) for i in range(100)]),
        plot([random()-0.5 for i in range(100)]),
        plot([1+i*random() for i in range(100)], fill=True),
        plot([[i^j for i in range(250)] for j in range(150)]),
    ]
    show_grid(plots)
    
