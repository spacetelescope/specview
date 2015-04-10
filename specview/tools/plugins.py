"""Plugin loading machinery"""
from inspect import getmembers, isfunction


def plugins():
    """Return plugins as specifically designed for the specview package

    Returns
    -------
    Plugins instances with the imported functions set as methods.
    """
    _plugin_pkg = 'specview.plugins'
    _default_plugins = ['default_ops']
    _user_plugins = ['ops']

    return Plugins(_plugin_pkg, _default_plugins + _user_plugins)


class Plugins(object):
    """Import a set of modules and set the defined functions as methods.

    Parameters
    ----------
    pkg_name: str
        The root name of the namespace package

    modules_names: [str,]
        The list of module names to be imported.

    Attributes
    ----------
    All the functions in the imported modules.
    """
    def __init__(self, pkg_name, module_names):
        modules = []
        for module_name in module_names:
            try:
                modules.append(__import__('.'.join([pkg_name, module_name]),
                                          fromlist=module_name))
            except ImportError:
                pass
        funcs = [func for module in modules
                 for func in getmembers(module, isfunction)]
        for name, func in funcs:
            setattr(self, name, func)
