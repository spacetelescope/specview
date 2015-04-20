"""Data operations"""
from specview.tools import decorate

# Stats functions
from specview.analysis.statistics import stats, eq_width, extract


# Basic math
@decorate.display_result
def add(a, b):
    """Add items"""
    return a + b


@decorate.display_result
def subtract(a, b):
    return a - b


@decorate.display_result
def multiply(a, b):
    return a * b


@decorate.display_result
def divide(a, b):
    return a / b
