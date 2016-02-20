"""
Matplotlib. Wrapper. Smart. Tufte. Pythonic.
"""

from types import GeneratorType
import matplotlib
from matplotlib import pyplot
from collections import defaultdict, Counter

class BasePlot(object):
    grid = False
    title = ''
    xlabel = ''
    ylabel = ''

    def __init__(self, data, options):
        self.data = self._format_data(data)
        self._apply_options(options)

    def _format_data(self, data):
        is_list = lambda a: isinstance(a, (list, tuple, GeneratorType, range))
        if is_list(data):
            data = list(data)
            if len(data) and is_list(data[0]):
                return data
            else:
                return enumerate(data)
        elif isinstance(data, dict):
            return list(data.items())
        else:
            raise ValueError('Unexpected data type {}'.format(type(data)))

    def _apply_options(self, options):
        for option, value in options.items():
            if not hasattr(self, option):
                raise ValueError('Invalid option: {}'.format(option))
            setattr(self, option, value)

    def _make_figure(self):
        keys = [a for a, b in self.data]
        values = [b for a, b in self.data]

        matplotlib.rcParams['xtick.direction'] = 'out'
        matplotlib.rcParams['ytick.direction'] = 'out'

        fig = pyplot.figure(figsize=(12, 9))
        ax = pyplot.subplot(111)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        # Ensure ticks only on left and bottom, removing top and right ticks.
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

        args = {}

        self._plot(keys, values)

        pyplot.title(self.title)
        pyplot.grid(self.grid)
        pyplot.xlabel(self.xlabel)
        pyplot.ylabel(self.ylabel)
        max_data = max(values)
        min_data = min(values)
        # Avoid trncating Y axis unless absolutely necessary.
        distance = max_data - min_data
        if distance > 0.01 * min_data:
            pyplot.ylim(0, max_data)
        else:
            pyplot.ylim(min_data - distance * 0.3, max_data + distance * 0.3)

        # Fix x-axis, including final bar if necessary.
        pyplot.xlim(min(keys), max(keys)+self.bars_width)

        # Show full value in ticks, instead of using an offset.
        ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter(useOffset=False))
        ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter(useOffset=False))

        pyplot.xticks(fontsize=14)
        pyplot.yticks(fontsize=14)

        fig.tight_layout()

    def show(self):
        self._make_figure()
        pyplot.show()
        pyplot.close()

    def save(self, path):
        self._make_figure()
        # Remove extraneous whitespace.
        pyplot.savefig(path, bbox_inches="tight")

class TimePlot(BasePlot):
    pass

class Histogram(BasePlot):
    def __init__(self, samples, bin=None, **options):
        samples_set = sorted(set(samples))
        if bin is None:
            difs = [b - a for a, b in zip(samples_set, samples_set[1:])]
            # Use the smallest difference as bin size, up to a maximum of 40.
            bin = max(min(difs), (samples_set[-1] - samples_set[0]) / 40)

        data = {k*bin: v for k, v in Counter(int(s/bin) for s in samples).items()}
        self.bars_width = bin
        super().__init__(data, options)

    def _plot(self, keys, values):
        pyplot.bar(keys, values, width=self.bars_width)

class ScatterPlot(BasePlot):
    pass

class LinePlot(BasePlot):
    """
    self.fill:
            fn = pyplot.fill_between
    """

    @staticmethod
    def count(samples, bins=None, **options):
        
        return plot

    def __init__(self, data, title='', xlabel='', ylabel='', **options):
        

        self.data = data
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        
        

if __name__ == '__main__':
    from random import randint, random
    #Histogram([100100, 100200, 100300, 100100, 100150, 100520, 100300]).show()
    Histogram([random()+1 for i in range(100)]).show()
    #Plot({'a': 100, 'b': 500}).show()
