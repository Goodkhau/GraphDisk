from pathlib import Path
import pytest
import json
import shutil

GRAPHS_FOLDER = Path(__file__).parent / 'graphs'

def _clean_graphs(config):
    if not hasattr(config, "workerinput"):  # controller / non-xdist only
        shutil.rmtree(GRAPHS_FOLDER, ignore_errors=True)

def pytest_sessionstart(session):
    _clean_graphs(session.config)

def pytest_sessionfinish(session, exitstatus):
    _clean_graphs(session.config)

@pytest.fixture(scope="session")
def cleanUp():
    yield GRAPHS_FOLDER

@pytest.fixture
def case(request):
    test_file = Path(request.module.__file__)
    return get_data(test_file=test_file, scenario=request.node.name)

@pytest.fixture
def metadata(request):
    return {
        "scenario": request.node.name
    }

def get_data(test_file: Path, scenario: str):
    path = test_file.parent / "data" / test_file.name / scenario
    input_data = path / "input.json"
    output_data = path / "output.json"

    if not input_data.exists():
        input_data.parent.mkdir(parents=True, exist_ok=True)
        with open(input_data, "w") as file:
            json.dump({}, file)

    if not output_data.exists():
        output_data.parent.mkdir(parents=True, exist_ok=True)
        with open(output_data, "w") as file:
            json.dump({}, file)

    return (
        json.loads(input_data.read_text(encoding="utf-8")),
        json.loads(output_data.read_text(encoding="utf-8"))
    )