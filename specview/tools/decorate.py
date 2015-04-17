"""Decorators to assist plugin integration"""
from functools import wraps

# Setup references that will be re-assigned when
# the plugins are imported.
controller = None


def display_result(func):
    """Display result of func immediately."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        item = controller.add_data_set(result)
        controller.create_display(item)
        return item

    return wrapper
