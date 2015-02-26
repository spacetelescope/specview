import sys

from specview.ui.controller import Controller

class SpecView(Controller):
    '''Run the GUI interactively.'''

    app = None

    def __init__(self, argv=None):
        from specview.ui.qt.pyqt_nonblock import pyqtapplication

        if self.__class__.app is None:
            self.__class__.app = pyqtapplication(argv)

        super(SpecView, self).__init__()
        self.viewer.show()


if __name__ == '__main__':
    sv = SpecView(sys.argv)

    sys.exit(sv.app.exec_())
