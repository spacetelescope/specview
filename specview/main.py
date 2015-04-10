#!/usr/bin/env python

from os import sys

# TODO: get rid of nasty try/excepts
try:
    from .ui.controller import Controller
    from .ui.ipython.kernel import ipython_kernel_start
except:
    from ui.controller import Controller
    from ui.ipython.kernel import ipython_kernel_start

class SView(Controller):
    """Main entry point"""

    qt_app = None

    def __init__(self, argv=None):
        from specview.ui.qt.pyqt_nonblock import pyqtapplication

        if self.__class__.qt_app is None:
            self.__class__.qt_app = pyqtapplication(argv)

        self._kernel = ipython_kernel_start()
        super(SView, self).__init__(argv)
        self.viewer.show()


def main():
    app_gui = SView(sys.argv)
    sys.exit(app_gui.qt_app.exec_())


if __name__ == '__main__':
    main()
