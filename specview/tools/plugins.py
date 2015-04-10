"""Plugin loading machinery"""
from inspect import getmembers, isfunction


def plugins():
    """Return plugins as specifically designed for the specview package

    Returns
    -------
    Plugins instances with the imported functions set as methods.
    """
    plugin_pkg = 'specview.plugins'
    default_plugins = ['default_ops']
    user_plugins = ['ops']

    return Plugins(plugin_pkg, default_plugins + user_plugins)


class Plugins(object):
    """Import a set of modules and set the defined functions as methods.

    Parameters
    ----------
    pkg_name: str
        The root name of the namespace package

    modules_names: [str,]
        The list of module names to be imported.

    hander: function(x)
        A function that needs to be applied to the result
        of any plugin. This is so the main app can control
        how results are handled. Default is a simple passthrough.

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


def namespace(plugins):
    """Return a dictionary of the member methods."""
    result = {name: func for name, func  in getmembers(plugins, isfunction)}
    return result

def decorate(plugins, decorator):
    """Return a dictionary of the member methods,
    surrounded with the decorator"""
    result = {}
    for name, func in namespace(plugins):
        decorated = lambda *args, **kwargs: decorator(func(*args, **kwargs))
        result[name] = decorated
    return result
