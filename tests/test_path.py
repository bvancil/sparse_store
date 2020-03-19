import pathlib

import pytest

from sparse_store import storage_path


def test_storage_path():
    assert storage_path(
        pathlib.Path("B:/backup"), pathlib.Path("C:/Users/bozo/.ssh")
    ) == pathlib.Path("B:/backup/C_drive/Users/bozo/.ssh")
