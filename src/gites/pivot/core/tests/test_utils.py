# encoding: utf-8
"""
gites.pivot.core

Created by mpeeters
Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""

from gites.pivot.core import testing
from gites.pivot.core import utils


class TestUtils(testing.PivotTestCase):

    def test_get_differences(self):
        obj1 = type('obj', (object, ), {'a': 1, 'b': 2, 'c': 3})()
        obj2 = type('obj', (object, ), {'a': 3, 'b': 2, 'c': 1})()
        expected = [('a', 1, 3), ('c', 3, 1)]
        result = utils.get_differences(obj1, obj2, ('a', 'b', 'c'))
        self.assertEqual(expected, result)

    def test_get_differences_with_missing_attributes(self):
        obj1 = type('obj', (object, ), {'a': 1, 'b': 2})()
        obj2 = type('obj', (object, ), {'a': 1})()
        expected = [('b', 2, None)]
        result = utils.get_differences(obj1, obj2, ('a', 'b'))
        self.assertEqual(expected, result)

    def test_get_differences_with_empty_strings(self):
        obj1 = type('obj', (object, ), {'a': ' ', 'b': None})()
        obj2 = type('obj', (object, ), {'a': None, 'b': ''})()
        expected = []
        result = utils.get_differences(obj1, obj2, ('a', 'b'))
        self.assertEqual(expected, result)

    def test_is_equal(self):
        self.assertTrue(utils.is_equal('FOO', 'foo'))
        self.assertFalse(utils.is_equal('foo', None))

    def test_clean_value(self):
        self.assertEqual(None, utils.clean_value(None))
        self.assertEqual('foo', utils.clean_value(' foo '))
