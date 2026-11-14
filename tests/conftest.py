from pathlib import Path
import pytest
import json
import shutil

@pytest.fixture(scope="session")
def cleanUp():
    graphs_folder = Path(__file__).parent / 'graphs'

    yield graphs_folder

    shutil.rmtree(graphs_folder)
    graphs_folder.mkdir(parents=True, exist_ok=True)

@pytest.fixture
def case(request):
    test_file = Path(request.module.__file__)
    return get_data(test_file=test_file, scenario=request.node.name)

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