"""Plugin loading machinery"""
import importlib
import pkgutil
from inspect import getmembers, isfunction


def plugins():
    """Return plugins as specifically designed for the specview package

    Returns
    -------
    Plugins instances with the imported functions set as methods.
    """
    plugin_pkg = 'specview.plugins'

    return Plugins(plugin_pkg)


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
    def __init__(self, pkg_name):
        modules = import_submodules(pkg_name)
        funcs = [func for module in modules.itervalues()
                 for func in getmembers(module, isfunction)]
        for name, func in funcs:
            if not name.startswith('_'):
                setattr(self, name, func)


def namespace(obj):
    """Return a dictionary of the member methods."""
    result = {name: func for name, func in getmembers(obj, isfunction)}
    return result


def import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results
