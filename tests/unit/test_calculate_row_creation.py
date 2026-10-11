from src.disk_graph import calculateRowCreation

def check(case):
    data, output = case
    new_columns, updated_config = calculateRowCreation(data['columns'], data['config'])
    assert new_columns == output['new_columns']
    assert updated_config == output['updated_config']


def test_empty_config(case):
    check(case)

def test_new_column_in_config(case):
    check(case)

def test_same_name_type(case):
    check(case)

def test_same_name_diff_type(case):
    check(case)