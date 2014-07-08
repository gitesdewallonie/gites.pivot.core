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
    attributes
    Exemple:

    obj1.value1 = 10
    obj1.value2 = 'hello'

    obj2.value1 = 20
    obj2.value2 = 'hello'

    return [('value1', 10, 20)]
    """
    diff = []
    for attr in attributes:
        obj1_value = clean_value(getattr(obj1, attr, None))
        obj2_value = clean_value(getattr(obj2, attr, None))
        if is_equal(obj1_value, obj2_value) is False:
            diff.append((attr, obj1_value, obj2_value))
    return diff


def get_best_match(session, obj, mapper, columns):
    if not obj:
        return
    query = session.query(mapper)
    for column in columns:
        map_attr = getattr(mapper, column)
        obj_attr = getattr(obj, column)
        query = query.filter(map_attr == obj_attr)
    result = query.all()
    if len(result) == 1:
        return result[0]


def is_equal(value1, value2):
    """Compare two value and return a boolean"""
    if hasattr(value1, 'lower') and hasattr(value2, 'lower'):
        return value1.lower() == value2.lower()
    return value1 == value2


def clean_value(value):
    """Format value for comparisson"""
    if hasattr(value, 'strip'):
        return value.strip() or None
    if value is False:
        return False
    return value or None


def now():
    return datetime.now()
