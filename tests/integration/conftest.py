import pytest
import shutil
import json
from pathlib import Path

class ConfigClass:
    def update(self, path, config):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        with open(path, "w") as file:
            json.dump(config, file)

    def read(self, path):
        try:
            with open(path, 'r', encoding="utf-8") as file:
                return json.load(file)
        except:
            return None

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

@pytest.fixture
def Config(request):
    return ConfigClass()