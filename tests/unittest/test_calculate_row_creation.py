import unittest

from tests.unittest.get_data import get_data
from src.disk_graph import calculateRowCreation

class TestCalculateRowCreation(unittest.TestCase):
    def test_empty_config(self):
        data, output = get_data(type(self).__name__, self._testMethodName)

        new_columns, updated_config = calculateRowCreation(data['columns'], data['config'])
        self.assertEqual(new_columns, output['new_columns'])
        self.assertEqual(updated_config, output['updated_config'])