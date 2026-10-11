import pytest
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def cleanUp():
    graphs_folder = Path(__file__).parent / 'graphs'

    yield graphs_folder

    shutil.rmtree(graphs_folder)
    graphs_folder.mkdir(parents=True, exist_ok=True)

@pytest.fixture
def metadata(request):
    return {
        "scenario": request.node.name
    }