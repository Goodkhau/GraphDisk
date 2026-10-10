from pathlib import Path
import pytest
import json

DATA_DIR = Path(__file__).parent / "data"

@pytest.fixture
def case(request):
    filename = Path(request.module.__file__).name
    return get_data(filename, request.node.name)

def get_data(test_name, scenario):
    path = DATA_DIR / test_name / scenario
    input_data = path / f"input.json"
    output_data = path / f"output.json"

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