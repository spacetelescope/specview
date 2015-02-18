'''Signals used by specview'''
import warnings

import six

from register_leaf_classes import RegisterLeafClasses
from specview.proto.specviewer import signal_slot


class Signals(signal_slot.Signals):
    def __init__(self, signal_class=None):
        super(Signals, self).__init__()
        if signal_class is not None:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                for signal in signal_class:
                    self.add(signal)

@six.add_metaclass(RegisterLeafClasses)
class Signal(signal_slot.Signal):
    '''Specview signals'''

# Signals related to Data and Models
class ModelRefresh(Signal):
    '''Global reset/re-read all models.

    Notes
    -----
    Use if the specific states of any models become unknown.
    Otherwise, use a more specific signal.
    '''

class ModelAdded(Signal):
    '''New model added'''

class ModelRemoved(Signal):
    '''Model removed.'''


# Signals related to view changes.
# Note: These are intended for the high-level interactions between
# modules. If signalling is needed within a module for detailed
# GUI interaction, the gui-specific signalling should be used.
# I.E. Use PyQt.pyqtsignal()

class ViewportChange(Signal):
    '''Viewport has changed.'''
