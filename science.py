"""
Matplotlib. Wrapper. Smart. Tufte. Pythonic.

If you get
"FutureWarning: elementwise comparison failed; returning scalar
instead, but in the future will perform elementwise comparison"
It's not my fault. Check https://github.com/matplotlib/matplotlib/issues/5209 .
A fix should be released soon
"""

import matplotlib
from matplotlib import pyplot
from collections import defaultdict, Counter

class BasePlot(object):
    grid = False
    title = ''
    xlabel = ''
    ylabel = ''

    @staticmethod
    def _format_data(data):
        is_list = lambda a: hasattr(a, '__iter__') and not isinstance(a, str)
        if isinstance(data, dict):
            return list(data.items())
        elif is_list(data):
            data = list(data)
            if len(data) and is_list(data[0]):
                return data
            else:
                return list(enumerate(data))
        else:
            raise ValueError('Unexpected data type {}'.format(type(data)))

    def __init__(self, data, **options):
        self.data = self._format_data(data)
        self._apply_options(options)

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

        # Show full value in ticks, instead of using an offset.
        ax.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter(useOffset=False))
        ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter(useOffset=False))

        if isinstance(keys[0], str):
            s = sorted(set(keys))
            num_keys = [s.index(key) for key in keys]
            pyplot.xticks(num_keys, keys)
            keys = num_keys
        self._plot(keys, values)

        ax.margins(x=.02, y=0.02)

        # Apply Y limits and margins manually to avoid truncating unless
        # absolutely necessary.
        max_data = max(values)
        min_data = min(values)
        distance = (max_data - min_data) or abs(min_data)
        if 0 < distance < 0.01 * min_data:
            pyplot.ylim(min_data - distance * 0.4, max_data + distance * 0.4)
        else:
            pyplot.ylim(ymin=-distance*0.02)

        pyplot.title(self.title)
        pyplot.grid(self.grid)
        pyplot.xlabel(self.xlabel)
        pyplot.ylabel(self.ylabel)

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

class BarPlot(BasePlot):
    bars_width = 0.9

    def _plot(self, keys, values):
        pyplot.bar(keys, values, width=self.bars_width, align='center')

class Histogram(BarPlot):
    def __init__(self, samples, bin=None, **options):
        samples_set = sorted(set(samples))
        if bin is None:
            difs = [b - a for a, b in zip(samples_set, samples_set[1:])]
            # Use the smallest difference as bin size, up to a maximum of 40.
            bin = max(min(difs), int((samples_set[-1] - samples_set[0]) / 40))

        data = {k*bin: v for k, v in Counter(int(s/bin) for s in samples).items()}
        self.bars_width = bin
        super().__init__(data, **options)

class ScatterPlot(BasePlot):
    def _plot(self, keys, values):
        pyplot.scatter(keys, values)

class LinePlot(BasePlot):
    fill = False

    def _plot(self, keys, values):
        if self.fill:
            pyplot.fill_between(keys, values)
        else:
            pyplot.plot(keys, values)

        
def plot(data, **options):
    data = BasePlot._format_data(data)
    if not len(data):
        return LinePlot(data, **options)

    keys = [a for a, b in data]
    if len(keys) != len(set(keys)):
        return ScatterPlot(data, **options)
    elif isinstance(data[0][0], str):
        return BarPlot(data, **options)
    else:
        return LinePlot(data, **options)

if __name__ == '__main__':
    #BarPlot({'Shanghai': 24256800, 'Beijing': 21516000, 'Lagos': 21324000, 'Tokyo': 13297629, 'São Paulo': 11895893}).show()

    from random import randint, random
    plot([('John', 3.5), ('Mary', 4), ('Charlie', 2.2)]).show()
    #Histogram([1000100, 1000200, 1000300, 1000100, 1000150, 1000520, 1000300]).show()
    #plot([(randint(0, 100), i * random()) for i in range(10000)]).show()
    #Plot({'a': 100, 'b': 500}).show()
