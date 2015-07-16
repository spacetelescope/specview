import pyqtgraph as pg


class ExtendedFillBetweenItem(pg.FillBetweenItem):
    """
    GraphicsItem filling the space between two PlotDataItems.
    """
    def __init__(self, window=None, *args, **kwargs):
        super(ExtendedFillBetweenItem, self).__init__(*args, **kwargs)
        self.window = window

        print(self.window)

        if self.window is not None:
            self.window.sigRangeChanged.connect(self.updatePath)