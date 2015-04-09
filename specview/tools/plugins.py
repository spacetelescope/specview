"""Plugin loading machinery"""

from inspect import getmembers, isfunction

from specview.plugins import "default_ops"
try:
    from specview.plugins import ops as user_ops
except ImportError:
    user_ops = {}


def decorate_plugins(decorator):
    class Plugin(object):
        """The decorated functions"""
    decorated = Plugin()
    all_funcs = getmembers(default_ops, isfunction) + getmembers(user_ops, isfunction)
    for name, func in all_funcs:
        decorated_func = lambda x, y: decorator(func(x, y))
        setattr(decorated, name, decorated_func)
    return decorated
