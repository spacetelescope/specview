"""Analysis log.

Parameters
----------
log: Logger
    The logger instance.
"""

from functools import wraps
from collections import namedtuple

_entry = namedtuple('Entry', ['name', 'func', 'args', 'kwargs', 'result'])


class _logger(list):
    """Maintain log of functions called."""


log = _logger()


class Register(object):
    """Register a function to log itself."""

    def __init__(self, controller, func_name=None):
        self._func_name = func_name
        self._controller = controller
        self.echo = lambda obj: self._controller.viewer.console_dock.wgt_console.append_stream(echo_format(obj))

    def __call__(self, func):
        if self._func_name is None:
            self._func_name = func.func_name

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            log.append(_entry(name=self._func_name,
                              func=func,
                              args=args,
                              kwargs=kwargs,
                              result=result))
            self.echo(result)
            return result

        return wrapper

def echo_format(obj):
    return '\nLog result:\n{}\n\n'.format(str(obj))
