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

is_list = lambda a: hasattr(a, '__iter__') and not isinstance(a, str)

class BasePlot(object):
    grid = False
    title = ''
    xlabel = ''
    ylabel = ''
    fontsize = 14

    @staticmethod
    def _format_data(data):
        if isinstance(data, dict):
            return list(data.items())
        elif is_list(data):
            data = list(data)
            if len(data) and is_list(data[0]):
                if len(data[0]) == 2:
                    return data
                else:
                    return [(None, line) for line in data]
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
        pyplot.style.use('ggplot')
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
            if len(''.join(keys)) > 80:
                # To avoid overlapping labels we use xdate format, which
                # rotates each label 45 degrees counter-clockwise.
                # The minimum number of characters is completely arbitrary.
                fig.autofmt_xdate()
            s = sorted(set(keys))
            num_keys = [s.index(key) for key in keys]
            pyplot.xticks(num_keys, keys)
            keys = num_keys

        self._plot(keys, values, ax)
        self._setup_margins(keys, values, ax)
        
        pyplot.title(self.title)
        pyplot.grid(self.grid)
        pyplot.xlabel(self.xlabel)
        pyplot.ylabel(self.ylabel)

        pyplot.xticks(fontsize=self.fontsize)
        pyplot.yticks(fontsize=self.fontsize)

        fig.tight_layout()

    def _setup_margins(self, keys, values, ax):
        ax.margins(x=.02, y=0.02)

        # Apply Y limits and margins manually to avoid truncating unless
        # absolutely necessary.
        max_data = max(values)
        min_data = min(values)
        distance = (max_data - min_data) or abs(min_data)
        if 0 < distance < 0.01 * min_data:
            pyplot.ylim(min_data - distance * 0.4, max_data + distance * 0.4)
        else:
            if min_data < 0:
                pyplot.ylim(ymin=min_data-distance*0.02)
            else:
                pyplot.ylim(ymin=-distance*0.02)

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

    def _plot(self, keys, values, ax):
        rects = pyplot.bar(keys, values, width=self.bars_width, align='center')
        if len(rects) <= 10:
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.get_yaxis().set_visible(False)
            ax.xaxis.set_ticks_position('none')
            max_height = max(rect.get_height() for rect in rects)
            for rect in rects:
                height = rect.get_height()
                padding = max_height * 0.03
                if height > padding * 2:
                    y = rect.get_y()+height - padding
                else:
                    y = rect.get_y()+height + padding * 2
                value = round(rect.get_y() or height, 4)
                ax.text(rect.get_x() + rect.get_width()/2., y, value, ha='center', va='top', fontsize=self.fontsize)

class Histogram(BarPlot):
    def __init__(self, samples, bin=None, **options):
        data, bin = count(samples, bin)
        self.bars_width = bin
        super().__init__(data, **options)

class ScatterPlot(BasePlot):
    def _plot(self, keys, values, ax):
        pyplot.scatter(keys, values)

class LinePlot(BasePlot):
    fill = True

    def _plot(self, keys, values, ax):
        if self.fill:
            pyplot.fill_between(keys, values)
        else:
            pyplot.plot(keys, values)

class MatrixPlot(BasePlot):
    colors = 'cubehelix'
    def _plot(self, keys, values, ax):
        pyplot.imshow(values, interpolation='nearest', cmap=pyplot.get_cmap(self.colors))

    def _setup_margins(self, keys, values, ax):
        pass
        
def plot(data, **options):
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

def count(samples, bin=None):
    samples_set = sorted(set(samples))
    if bin is None:
        difs = [b - a for a, b in zip(samples_set, samples_set[1:])]
        # Use the smallest difference as bin size, up to a maximum of 40.
        bin = max(min(difs), int((samples_set[-1] - samples_set[0]) / 40))

    data = {k*bin: v for k, v in Counter(int(s/bin) for s in samples).items()}
    return data, bin

if __name__ == '__main__':
    #plot([('Shanghai', 24256800), ('Beijing', 21516000), ('Lagos', 21324000), ('Tokyo', 13297629), ('São Paulo', 11895893)], title='Population by city').show()

    from random import randint, random, sample
    from string import ascii_lowercase
    #Histogram([randint(1000, 1010) for i in range(1000)]).show()
    #plot([(''.join(sample(ascii_lowercase, 5)), random()) for i in range(10)]).show()
    #plot([(randint(0, 100), i * random()) for i in range(10000)]).show()
    #plot([0.1+random() ** 0.5 for i in range(100)]).show()
    plot([[i^j for i in range(100)] for j in range(100)]).show()
