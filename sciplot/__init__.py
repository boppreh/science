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

def format_number(n, width, prefix='', suffix=''):
    if (int(width) == width and int(n) == n) or width == 0:
        return '{:,d}'.format(int(n))

    decimal_digits = max(0, int(-math.log10(width)+2), int(-math.log10(abs(n) or 1)))
    format = '{' + ':0,.{}f'.format(decimal_digits) + '}'
    return prefix + format.format(n) + suffix

def min_max_dif(values):
    sorted_values = sorted(set(values))
    if len(sorted_values) < 2:
        return 0, 0
    difs = [abs(b - a) for a, b in zip(sorted_values, sorted_values[1:])]
    return min(difs), sorted_values[-1] - sorted_values[0]

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
    fontsize = 14
    colors = 'cubehelix'
    fig_size = (12, 9)
    xprefix = ''
    xsuffix = ''
    yprefix = ''
    ysuffix = ''
    xlog = False
    ylog = False
    background = '#eeeeee'

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
            return sorted(data.items())
        elif is_list(data):
            data = list(data)
            if len(data) and is_list(data[0]):
                if len(data[0]) == 2:
                    # List of (key, value) pairs.
                    return sorted(data)
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

    def _get_fig_ax(self, fig=None, ax=None):
        if fig:
            assert ax
            return fig, ax
        else:
            fig = pyplot.figure(figsize=self.fig_size)
            ax = pyplot.subplot(111)
            return fig, ax

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

        fig, ax = self._get_fig_ax(fig, ax)

        if self.background is None:
            ax.set_axis_bgcolor('none')
        else:
            ax.set_axis_bgcolor(self.background)

        # Hide frame lines on top and right sides.
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Ensure ticks only on left and bottom, removing top and right ticks.
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

        if self.xlog:
            ax.set_xscale('log')
        if self.ylog:
            ax.set_yscale('log')

        if not hasattr(values[0], '__iter__'):
            _, values_width = min_max_dif(values)
            ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format_number(x, values_width, self.yprefix, self.ysuffix)))

        if not hasattr(keys[0], '__iter__') and keys[0] is not None and not isinstance(keys[0], str):
            _, keys_width = min_max_dif(keys)
            ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format_number(x, keys_width, self.xprefix, self.xsuffix)))

        # Handle non-numeric data on the x-axis.
        if isinstance(keys[0], str):
            # Heuristic to rotate label to fit if necessary.
            rotation = 45 if len(''.join(keys)) > 80 else 0
            s = sorted(set(keys))
            num_keys = [s.index(key) for key in keys]
            ax.set_xticks(num_keys)
            ax.set_xticklabels(keys, rotation=rotation)
            keys = num_keys

        self._draw(keys, values, ax)

        # Must be called *after* drawing the data, otherwise we don't know
        # what to scale to.
        ax.margins(x=.03, y=0.03, tight=True)
        
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)

        ax.grid(self.grid)

        # Resize plot to fill available space.
        fig.tight_layout()

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

    def __add__(self, other):
        return MergedPlots([self, other])

    def __or__(self, other):
        return GridPlots([self, other])

    @property
    def cmap(self):
        return pyplot.get_cmap(self.colors)

class MergedPlots(BasePlot):
    def __init__(self, plots):
        self.plots = plots

    def _draw_plot(self, fig=None, ax=None):
        fig, ax = self._get_fig_ax(fig, ax)
        for plot in self.plots:
            plot._draw_plot(fig, ax)

    def __add__(self, other):
        return MergedPlots(self.plots + [other])
    

class GridPlots(BasePlot):
    nrows = None

    def __init__(self, plots):
        self.plots = plots

    def _draw_plot(self, fig=None, ax=None):
        assert fig is None and ax is None

        if len(self.plots) == 1:
            return self.plots[0].show()

        nrows = self.nrows or int(math.sqrt(len(self.plots)))
        ncols = int(math.ceil(len(self.plots) / nrows))

        fig, axes = pyplot.subplots(nrows=nrows, ncols=ncols)
        for ax, p in zip(axes.flat, self.plots):
            p._draw_plot(fig, ax)

        pyplot.show()
        pyplot.close()

    def __or__(self, other):
        return GridPlots(self.plots + [other])

class TimePlot(BasePlot):
    pass

class Network(BasePlot):
    """

    Windows installation instructions: install `pydotplus` and the latest
    version of graphviz from http://www.graphviz.org/pub/graphviz/stable/windows/
    ( http://www.graphviz.org/pub/graphviz/stable/windows/graphviz-2.38.msi
    as of 2016-02). You may have to add `C:\Program Files (x86)\Graphviz2.38\bin`
    to your path manually.
    """
    layout = 'neato'
    node_size = None
    with_labels = None
    directed = False
    arrowstyle = '-|>' # http://matplotlib.org/api/patches_api.html?highlight=fancyarrowpatch#matplotlib.patches.FancyArrowPatch
    node_color = 'r'
    fig_size = (8, 8)

    @property
    def graph(self):
        """
        Returns a NetworkX graph object, useful for checking properties.
        """
        import networkx as nx
        graph = nx.MultiDiGraph()

        for start, end in self.data:
            if end is None:
                graph.add_node(start)
            else:
                graph.add_edge(start, end)

        return graph

    def _draw_dot_plot(self, fig=None, ax=None):
        """
        Uses graphviz's "dot" to generate a PNG image and draw on the given
        fig.
        """
        import networkx

        fig, ax = self._get_fig_ax(fig, ax)
        ax.axis('off')

        png = networkx.drawing.nx_pydot.to_pydot(self.graph).create_png()
        try:
            from cStringIO import StringIO as Buffer
        except ImportError:
            from io import BytesIO as Buffer
        buffer = Buffer()
        buffer.write(png)
        buffer.seek(0)
        ax.imshow(matplotlib.image.imread(buffer))

    def _draw_plot(self, fig=None, ax=None):
        import networkx as nx
        from networkx.drawing.nx_pydot import graphviz_layout, pydot_layout
        from matplotlib.patches import FancyArrowPatch

        graph = self.graph

        # Graphviz is a pain to install in Windows and may not be available.
        # Spring layout is awful, but at least is guaranteed to work.
        try:
            pos = graphviz_layout(graph)
        except:
            pos = nx.spring_layout(graph, iterations=20)
            
        fig, ax = self._get_fig_ax(fig, ax)

        # We are not plotting actual values, hide both axis.
        ax.axis('off')

        # Automatically show labels for small networks.
        if self.with_labels is None and len(self.data) < 10:
            self.with_labels = True
        
        # Increase node size to fit labels.
        if self.node_size is None:
            if self.with_labels:
                self.node_size = 300
            else:
                self.node_size = 20

        nx.draw_networkx_edges(graph, pos, ax=ax, arrows=False)

        if self.directed:
            # Networkx default "directed" visualization just draws a thicker stub at the end.
            # This code adds actual arrow heads, taking care not to overlap the nodes themselves.
            for start, end in self.data:
                if start == end:
                    continue
                start_x, start_y = pos[start]
                end_x, end_y = pos[end]
                angle = math.atan2(end_y-start_y, end_x-start_x)
                distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
                end_pos = (end_x - 0.1 * distance * math.cos(angle), end_y - 0.1 * distance * math.sin(angle))
                ax.add_patch(FancyArrowPatch(posA=(start_x, start_y), posB=end_pos,
                                    color='k', arrowstyle=self.arrowstyle,
                                    mutation_scale=30, connectionstyle="arc3"))

        nx.draw_networkx_nodes(graph, pos, node_size=self.node_size, ax=ax, node_color=self.node_color, cmap=self.cmap)

        if self.with_labels:
            if max(len(str(l)) for l in pos) <= 2:
                nx.draw_networkx_labels(graph, pos, fontsize=self.fontsize, ax=ax)
            else:
                # Large labels don't look because they don't fit. In that case
                # we draw them outside the node, slightly above, with a white
                # box behind.
                for label, (x, y) in pos.items():
                    ax.text(x, y+self.fontsize, label, ha='center', fontsize=self.fontsize, bbox={'color': 'white', 'alpha': 1})

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
                _, max_width = min_max_dif(values)
                value = format_number(rect.get_y() or height, max_width, self.yprefix, self.ysuffix)
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
        if bin is None:
            min_dif, max_dif = min_max_dif(set(samples))
            # Use the smallest difference as bin size, up to a maximum of 40.
            bin = max(min_dif, max_dif / self.max_bins)

        data = {k*bin: v for k, v in Counter(int(s/bin) for s in samples).items()}
        self.bars_width = bin
        BarPlot.__init__(self, data, **options)

class ScatterPlot(BasePlot):
    color = None
    
    """ Draws a small circle on the (x, y) position of each data point. """
    def _draw(self, keys, values, ax):
        ax.scatter(keys, values, color=self.color)

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
    def _draw(self, keys, values, ax):
        im = ax.imshow(values, interpolation='nearest', cmap=self.cmap)
        pyplot.colorbar(im, ax=ax)

    def _setup_margins(self, keys, values, ax):
        pass
        
def plot(data, **options):
    """
    Given the raw data, selects the most appropriate type of plot and
    constructs it with the given options. Note: because of data ambiguity,
    some graph types are not selected automatically, such as Histogram
    or Network.
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

    plots = list(plots)

    if len(plots) == 1:
        return plots[0].show()

    plots = list(plots)
    if nrows == None:
        nrows = int(math.sqrt(len(plots)))
    ncols = int(math.ceil(len(plots) / nrows))

    fig, axes = pyplot.subplots(nrows=nrows, ncols=ncols)
    for ax, p in zip(axes.flat, plots):
        p._draw_plot(fig, ax)

    pyplot.show()
    pyplot.close()

def merge(*plots):
    fig = pyplot.figure(figsize=(12, 9))
    ax = pyplot.subplot(111)

    for p in plots:
    	p._draw_plot(fig, ax)

    pyplot.show()
    pyplot.close()

if __name__ == '__main__':
    from random import randint, random, sample, choice, shuffle
    from string import ascii_lowercase, ascii_uppercase

    #merge(plot(range(10)), plot(range(10, 0, -1)))
    #(plot(range(10)) + plot(range(10, 0, -1)) | plot(range(20, 0, -2))).show()
    #exit()
    # show_grid([Network(zip(range(100), sample(range(100), 100))) for i in range(9)])

    plots = [
        plot([('Shanghai', 24256800), ('Beijing', 21516000), ('Lagos', 21324000), ('Tokyo', 13297629), ('Sao Paulo', 11895893)]),
        Histogram([random()*random()+random() for i in range(1000)]),
        Histogram([randint(1000, 1010) for i in range(1000)]),
        plot([(''.join(sample(ascii_lowercase, 5)), random()) for i in range(17)]),
        plot([(choice('abcde'), random()*i) for i in range(50)], grid=True),
        plot([(randint(0, 100), i * random()) for i in range(100)]),
        plot([random()-0.5 for i in range(100)]),
        plot([100000+i*random() for i in range(100)], fill=True, grid=True, yprefix='$'),
        plot([[i^j for i in range(250)] for j in range(150)]),
        Network([(i, randint(1, 100)) for i in range(100)]),
        Network([(choice('ABCDEFGHI'), choice('ABCDEFGHI')) for i in range(15)], directed=True, with_labels=True),
        Network({'Alice': 'Bob', 'Bob': 'Charlie', 'Charlie': 'Alice', 'Eve': None}),
    ]
    show_grid(plots)
