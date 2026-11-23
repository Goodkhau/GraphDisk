import pytest

from disk_graph import ColumnType, parseConfig

def check(input: dict[str, str | ColumnType], output: dict[str, str]):
    parsed_config = parseConfig(input)
    assert parsed_config == output

@pytest.mark.unit
def test_passing_column_type():
    check(
        input={
            "id": ColumnType.String,
            "test_column_1": ColumnType.Bytes,
            "test_column_2": ColumnType.Integer,
            "test_column_3": ColumnType.Float
        },
        output={
            "id": ColumnType.String.name,
            "test_column_1": ColumnType.Bytes.name,
            "test_column_2": ColumnType.Integer.name,
            "test_column_3": ColumnType.Float.name
        }
    )

@pytest.mark.unit
def test_passing_column_name():
    check(
        input={
            "id": ColumnType.String.name,
            "test_column_1": ColumnType.Bytes.name,
            "test_column_2": ColumnType.Integer.name,
            "test_column_3": ColumnType.Float.name
        },
        output={
            "id": ColumnType.String.name,
            "test_column_1": ColumnType.Bytes.name,
            "test_column_2": ColumnType.Integer.name,
            "test_column_3": ColumnType.Float.name
        }
    )

@pytest.mark.unit
def test_passing_non_column_type():
    non_column_type = "not a column type"
    check(
        input={
            "id": non_column_type,
            "test_column_1": non_column_type,
        },
        output={
            "id": non_column_type,
            "test_column_1": non_column_type,
        }
    )

@pytest.mark.unit
def test_passing_non_column_type_mixed():
    non_column_type = "not a column type"
    check(
        input={
            "id": ColumnType.String,
            "test_column_1": non_column_type,
            "test_column_2": ColumnType.Integer.name,
        },
        output={
            "id": ColumnType.String.name,
            "test_column_1": non_column_type,
            "test_column_2": ColumnType.Integer.name,
        }
    )