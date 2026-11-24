from typing import Any

import pytest

from src.disk_graph import calculateColumnCreation

def check(case: tuple[dict[str, Any], dict[str, Any]]):
    data, output = case
    new_columns, updated_config = calculateColumnCreation(data['columns'], data['config'])
    assert new_columns == output['new_columns']
    assert updated_config == output['updated_config']

@pytest.mark.unit
def test_empty_config(case):
    raise Exception()
    check(case)

@pytest.mark.unit
def test_new_column_in_config(case):
    check(case)

@pytest.mark.unit
def test_same_name_type(case):
    check(case)

@pytest.mark.unit
def test_same_name_diff_type(case):
    check(case)