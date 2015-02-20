'''Signals used by specview'''
import six
import warnings

from register_leaf_classes import RegisterLeafClasses
import signal_slot

class Signals(signal_slot.Signals):
    '''The signal container that allows autoregistring of a
    set of predefined signals.
    '''
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

class SignalNoArgs(Signal):
    '''Subclassed signals take no arguments.'''

    def emit(self):
        '''Signal takes no arguments.'''
        super(SignalNoArgs, self).emit()


# Signals related to Data and Models
class ModelRefresh(SignalNoArgs):
    '''Global reset/re-read all models.'''


class ModelAdded(SignalNoArgs):
    '''New model added'''

class ModelRemoved(SignalNoArgs):
    '''Model removed.'''


# Signals related to view changes.
# Note: These are intended for the high-level interactions between
# modules. If signaling is needed within a module for detailed
# GUI interaction, the gui-specific signalling should be used.
# I.E. Use PyQt.pyqtsignal()

class ViewportChange(SignalNoArgs):
    '''Viewport has changed.'''
