from pyqtgraph import FillBetweenItem


class ExtendedFillBetweenItem(FillBetweenItem):
    """
    GraphicsItem filling the space between two PlotDataItems.
    """
    def __init__(self, window=None, **kwargs):
        super(ExtendedFillBetweenItem, self).__init__(**kwargs)
        self.window = window

        if self.window is not None:
            self.window.sigRangeChanged.connect(self.updatePath)
