import pytest

from sparse_store import dump_yaml
from sparse_store import load_yaml

yaml_equivalencies = {
    "test1": (
        {
            "backup": [
                {"FAKEDIR1": [{"FAKEDIR2": ["FILE2a", "FILE2b"]}, "FILE1a", "FILE1b"]},
                {"FAKEDIR2": ["FILE2a", "FILE2b", "FILE3b"]},
                "FAKEDIR3",
            ]
        },
        """backup:
- FAKEDIR1:
  - FAKEDIR2:
    - FILE2a
    - FILE2b
  - FILE1a
  - FILE1b
- FAKEDIR2:
  - FILE2a
  - FILE2b
  - FILE3b
- FAKEDIR3
""",
    )
}


@pytest.mark.parametrize("test", yaml_equivalencies.keys())
def test_load_yaml(test):
    obj, yaml = yaml_equivalencies[test]
    assert load_yaml(yaml) == obj


@pytest.mark.parametrize("test", yaml_equivalencies.keys())
def test_dump_yaml(test):
    obj, yaml = yaml_equivalencies[test]
    assert dump_yaml(obj) == yaml
