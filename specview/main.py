#!/usr/bin/env python

from os import sys, path

from specview.ui.controller import Controller


class SView(Controller):
    """Main entry point"""

    qt_app = None

    def __init__(self, argv=None):
        from specview.ui.qt.pyqt_nonblock import pyqtapplication

        if self.__class__.qt_app is None:
            self.__class__.qt_app = pyqtapplication(argv)

        super(SView, self).__init__()
        self.viewer.show()

        
def main():
    app_gui = SView(sys.argv)
    sys.exit(app_gui.qt_app.exec_())


if __name__ == '__main__':
    main()
