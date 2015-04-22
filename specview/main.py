#!/usr/bin/env python
from os import sys
from os.path import expanduser
import argparse


# Where to find plugins
_plugin_paths = [expanduser('~/.specview')]

# TODO: get rid of nasty try/excepts
try:
    from .ui.controller import Controller
    from .ui.ipython.kernel import ipython_kernel_start
except:
    from ui.controller import Controller
    from ui.ipython.kernel import ipython_kernel_start


class SView(Controller):
    """Main entry point

    Parameters
    ---------
    file_path: str
        File to initially open

    argv: [str,]
        Command line arguments, mainly for Qt's main application.
    """

    qt_app = None

    _plugin_path_added = False

    def __init__(self, filename=None, argv=None):
        # Setup plugin search path.
        if not self.__class__._plugin_path_added:
            for path in reversed(_plugin_paths):
                sys.path.insert(1, path)
            self.__class__._plugin_path_added = True

        # Start the Qt application, if necessary.
        if self.__class__.qt_app is None:
            from specview.ui.qt.pyqt_nonblock import pyqtapplication
            self.__class__.qt_app = pyqtapplication(argv)

        # Start up the GUI.
        self._kernel = ipython_kernel_start()
        super(SView, self).__init__()
        self.viewer.show()
        if filename is not None:
            self.open_file(filename)


def main():
    """Main entry from command line instances."""

    args = _define_arguments(sys.argv[1:])
    app_gui = SView(filename=args.datafile)
    sys.exit(app_gui.qt_app.exec_())


def _define_arguments(argv=None):
    """Define the command line arguments"""
    parser = argparse.ArgumentParser('Interactive spectral exploration.')
    parser.add_argument('datafile', nargs='?',
                        help='Initial file to display.')

    return parser.parse_args(argv)

if __name__ == '__main__':
    main()
