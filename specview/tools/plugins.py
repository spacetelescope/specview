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
        # Gather functions
        modules = import_submodules(pkg_name)
        funcs = [func for module in modules.itervalues()
                 for func in getmembers(module, isfunction)
                 if not func[0].startswith('_')]

        # Make functions available.
        for name, func in funcs:
            setattr(self, name, func)
        self.namespace = funcs


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
