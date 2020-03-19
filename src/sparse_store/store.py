import pathlib

# from typing import

from clikit.api.io import IO

from .config import Config
from .config import convert_backup_section_to_commands
from .config import convert_commands_to_paths
from .path import BackupPath


class Store:
    """Configuration and sparse file store

    """

    def __init__(self, path: pathlib.Path, io: IO, perform: bool = False):
        self.project_path = path
        self.config = Config(self.project_path)
        self.perform = perform
        self.io = io

    def config_file(self):
        return self.config.config_file()

    def backup_paths(self):
        """BackupPath objects for all configured backup paths
        
        
        Dispatches to Config to get list of files to backup
        """
        # Note: These are all generator expressions, so if you need
        #       to reuse them, wrap them with a `list()` function.

        backup_section = self.config.backup()
        commands = convert_backup_section_to_commands(backup_section)
        paths = convert_commands_to_paths(commands)
        backup_paths = (
            BackupPath(path, self.config, perform=self.perform, io=self.io)
            for path in paths
        )
        return backup_paths

    def backup(self):
        """Backup all files we find"""
        all_calls = (backup_path.backup() for backup_path in self.backup_paths())
        failures = filter(None, all_calls)
        return list(failures)

    def remove_stored(self):
        """Remove stored copies of all files we find"""
        for backup_path in self.backup_paths():
            backup_path.remove_stored()
