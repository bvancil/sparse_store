import pathlib

from cleo import Command

from .store import Store


class RestoreCommand(Command):
    """
    Restores from a sparse_store

    restore
        {path : path to create for sparse_store and configuration}
        {--dry-run : If set, just show what would have been done}
    """

    def handle(self):
        path = pathlib.Path(self.argument("path"))
        dry_run = self.option("dry-run")
        perform = not dry_run

        self.line(f"")
        if dry_run:
            self.line("<info>This is a dry run of init.</info>")

        store = Store(path)

        self.write(f'Config file: "{store.config_file()}"')
