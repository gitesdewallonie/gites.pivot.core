# encoding: utf-8
"""
gites.pivot.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from datetime import datetime


def get_differences(obj1, obj2, attributes):
    """Get the differences between two object limited to a list of given
    attributes"""
    diff = []
    for attr in attributes:
        obj1_value = clean_value(getattr(obj1, attr, None)) or None
        obj2_value = clean_value(getattr(obj2, attr, None)) or None
        if is_equal(obj1_value, obj2_value) is False:
            diff.append((attr, obj1_value, obj2_value))
    return diff


def is_equal(value1, value2):
    """Compare two value and return a boolean"""
    if hasattr(value1, 'lower') and hasattr(value2, 'lower'):
        return value1.lower() == value2.lower()
    return value1 == value2


def clean_value(value):
    """Format value for comparisson"""
    if hasattr(value, 'strip'):
        return value.strip()
    return value


def now():
    return datetime.now()
