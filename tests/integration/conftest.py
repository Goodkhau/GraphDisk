import pytest
import json
from pathlib import Path

class ConfigClass:
    def update(self, path: Path, config: dict[str, str | int]):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        with open(path, "w") as file:
            json.dump(config, file)

    def read(self, path: Path):
        try:
            with open(path, 'r', encoding="utf-8") as file:
                return json.load(file)
        except:
            return None

@pytest.fixture
def Config():
    return ConfigClass()