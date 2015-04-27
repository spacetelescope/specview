"""Analysis history.

Parameters
----------
history: History
    The history instance.
"""

from functools import wraps
from collections import namedtuple

_entry = namedtuple('Entry', ['name', 'func', 'args', 'kwargs', 'returns'])


class _history(list):
    """Maintain history of functions called."""


history = _history()


class Register(object):
    """Register a function to log itself to history."""

    def __init__(self, func_name=None):
        self._func_name = func_name

    def __call__(self, func):
        if self._func_name is None:
            self._func_name = func.func_name

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            history.append(_entry(name=self._func_name,
                                  func=func,
                                  args=args,
                                  kwargs=kwargs,
                                  returns=result))
            return result

        return wrapper
