# STATS


# GRAPHS
from types import GeneratorType
import matplotlib
from matplotlib import pyplot

class Plot:
    @staticmethod
    def count(samples, bins=None, *args, **kwargs):
        if bins is None:
            bins = 1
        if isinstance(bins, int):
            bins = range(0, max(samples), bins)

        data = {k: 0 for k in bins}
        for sample in samples:
            if sample >= bins[-1]:
                bin = bins[-1]
            else:
                bin = next(bin_start
                    for bin_start, bin_end in zip(bins, bins[1:])
                    if bin_start <= sample < bin_end)
            data[bin] += 1

        plot = Plot(data, *args, **kwargs)
        plot.bars_width = [bin_end - bin_start for bin_start, bin_end in zip(bins, bins[1:])] + [bins[-1] - bins[-2]]
        return plot

    def __init__(self, data, grid=False, bars=False, title='', xlabel='', ylabel=''):
        if isinstance(data, (list, tuple, GeneratorType, range)):
            data = dict(enumerate(data))
        self.data = data
        self.grid = grid
        self.bars = bars
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.bars_width = 1
        self.title = title

    def _make_figure(self):
        if self.bars:
            fn = pyplot.bar
            args = {'width': self.bars_width}
        else:
            fn = pyplot.plot
            args = {}
        matplotlib.rcParams['xtick.direction'] = 'out'
        matplotlib.rcParams['ytick.direction'] = 'out'
        fn(list(self.data.keys()), list(self.data.values()), **args)
        pyplot.title(self.title)
        pyplot.grid(self.grid)
        pyplot.xlabel(self.xlabel)
        pyplot.ylabel(self.ylabel)

    def show(self):
        self._make_figure()
        pyplot.show()
        pyplot.close()

    def save(self, path):
        self._make_figure()
        pyplot.savefig(path)

def count(samples, bin_size=1):
    pass

if __name__ == '__main__':
    Plot.count([1, 1, 1, 2, 3, 1, 2, 6, 8, 5, 3, 1, 102], grid=True, bars=True, title='asdf').show()
    
    exit()
    
    from matplotlib.pyplot import figure, show
    from numpy import arange, sin, pi

    t = arange(0.0, 1.0, 0.01)

    fig = figure(1)

    ax1 = fig.add_subplot(211)
    ax1.plot(t, sin(2*pi*t))
    ax1.grid(True)
    ax1.set_ylim((-2, 2))
    ax1.set_ylabel('1 Hz')
    ax1.set_title('A sine wave or two')

    for label in ax1.get_xticklabels():
        label.set_color('r')


    ax2 = fig.add_subplot(212)
    ax2.plot(t, sin(2*2*pi*t))
    ax2.grid(True)
    ax2.set_ylim((-2, 2))
    l = ax2.set_xlabel('Hi mom')
    l.set_color('g')
    l.set_fontsize('large')

    show()
