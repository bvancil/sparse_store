import pytest

from cleo import Application
from cleo import CommandTester

from sparse_store import Store
from sparse_store import InitCommand

# cleo-related

@pytest.fixture(scope="session")
def init_command():
    "init command"
    application = Application()
    application.add(InitCommand())
    command = application.find("init")
    return command


@pytest.fixture(scope="session")
def init_tester(init_command):
    "tester fir init subcommand"
    return CommandTester(init_command)

# depending on command

@pytest.fixture(scope="function")
def project_path(tmp_path):
    "project path for sparse_store"
    return tmp_path / "sparse_store"


# FIXME: Passing init_command to store is a hack that needs to be fixed.

@pytest.fixture(scope="function")
def store(project_path, init_command):
    "sparse_store in temporary directory"
    return Store(project_path, init_command.io)

