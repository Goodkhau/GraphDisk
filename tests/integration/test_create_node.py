import pytest

@pytest.mark.integration
def test_auto_incrementing(cleanUp, metadata, Config):
    graphs_folder = cleanUp
    name = metadata['scenario']



@pytest.mark.integration
def test_auto_incrementing_passing_pk(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_integer_invalid_pk(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_integer_duplicate_pk(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_integer_bulk_nodes(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_string_pk(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_string_empty_pk(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_string_invalid_pk(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_string_duplicate(cleanUp, metadata, Config):
    pass
@pytest.mark.integration
def test_string_bulk_nodes(cleanUp, metadata, Config):
    pass