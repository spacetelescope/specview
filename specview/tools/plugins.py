"""Plugin loading machinery"""
import importlib
import pkgutil
from inspect import getmembers, isfunction

from ..core.log import Register

def plugins(namespace):
    """Return plugins as specifically designed for the specview package

    Parameters
    ----------
    namespace: dict
        The namespace context for the plugins

    Returns
    -------
    Plugins instances with the imported functions set as methods.
    """
    plugin_pkg = 'specview.plugins'
    submodule = 'decorate'

    return Plugins(package=plugin_pkg,
                   namespace=namespace,
                   submodule=submodule)


class Plugins(object):
    """Import a set of modules and set the defined functions as methods.

    Parameters
    ----------
    package: str
        The root name of the namespace package

    namespace: dict
        The context in which the plugins will run.

    submodule: str
        Submodule to place the namespace.

    Attributes
    ----------
    All the functions in the imported modules.
    """
    def __init__(self, package, namespace=None, submodule=None):
        # Gather functions
        modules = import_submodules(package=package,
                                    namespace=namespace,
                                    submodule=submodule)
        funcs = [(name, Register(func_name=name)(func)) for module in modules.itervalues()
                 for (name, func) in getmembers(module, isfunction)
                 if not name.startswith('_')]

        # Make functions available.
        for name, func in funcs:
            setattr(self, name, func)
        self.namespace = funcs


def import_submodules(package, recursive=True, namespace=None, submodule=None):
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
        try:
            ns_module = getattr(results[full_name], submodule)
        except AttributeError:
            ns_module = results[full_name]
        ns_module.__dict__.update(namespace)
        if recursive and is_pkg:
            results.update(import_submodules(full_name,
                                             namespace=namespace,
                                             submodule=submodule))
    return results
