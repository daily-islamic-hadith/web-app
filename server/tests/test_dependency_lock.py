import re
from importlib.metadata import version
from pathlib import Path


def test_runtime_versions_match_production_lock():
    lock = Path(__file__).resolve().parents[1] / 'requirements.lock'
    pins = re.findall(r'^([\w.-]+)==([^\s\\]+)', lock.read_text(), re.MULTILINE)
    assert pins
    for name, expected in pins:
        assert version(name) == expected, f'{name} must match the production lock'
