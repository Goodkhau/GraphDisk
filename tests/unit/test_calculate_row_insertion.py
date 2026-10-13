import pytest

from src.disk_graph.db.pysqlite3.interface import calculateRowInsertion

def check(case):
    data, output = case
    new_columns, updated_config = calculateRowInsertion(data['columns'], data['row_data'])
    assert new_columns == output['placeholder']
    assert updated_config == output['insert_data']

@pytest.mark.unit
def test_empty_insertion(case):
    check(case)

@pytest.mark.unit
def test_half_column_supplied(case):
    check(case)

@pytest.mark.unit
def test_all_column_supplied(case):
    check(case)

@pytest.mark.unit
def test_excess_data_discarded_partial(case):
    check(case)

@pytest.mark.unit
def test_excess_data_discarded_full(case):
    check(case)