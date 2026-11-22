import pytest
import shutil
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def default_teardown():
    yield
    shutil.rmtree(Path.cwd() / "graphs", ignore_errors=True)