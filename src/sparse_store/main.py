#!/usr/bin/env python

from . import __version__
from .init_command import InitCommand
from .backup_command import BackupCommand
from .restore_command import RestoreCommand
from cleo import Application as BaseApplication


class Application(BaseApplication):
    """Backup files sparsely

    {--p|path= : path to use for sparse_store backup/restore operations; directories are configured in sparse_store.yaml}

    sparse_store.yaml format:
    backup:
    - path_1 # Include all contents of this directory
    - path_2: # Include select contents of this directory:
      - relative_dir_path2.1: # Full path is "{path2}/{relative_dir_path2.1}"
        - relative_file_path_2.1.1 # Full path is "{path2}/{relative_dir_path2.1}/{relative_file_path_2.1.1}"
      - relative_file_path_2.2 # Full path is "{path2}/{relative_file_path_2.2}"
    """

    # TODO: The above attempt at a global flag doesn't work. Fix it.
    def __init__(self):
        super(Application, self).__init__(name="sparse_store", version=__version__)
        for command in self.get_commands():
            self.add(command)

    def get_commands(self):
        "List of commands"
        commands = [InitCommand(), BackupCommand(), RestoreCommand()]
        return commands


def main():
    application = Application()
    application.run()


if __name__ == "__main__":
    main()
