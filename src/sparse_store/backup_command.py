import pathlib

from cleo import Command

from .store import Store
from .verbosity import Verbosity


class BackupCommand(Command):
    """
    Backs up to a sparse_store

    backup
        {path : path to create for sparse_store and configuration}
        {--dry-run : If set, just show what would have been done}
    """

    def handle(self):
        path = pathlib.Path(self.argument("path"))
        dry_run = self.option("dry-run")
        perform = not dry_run

        store = Store(path, io=self.io, perform=perform)
        self.line("", style="", verbosity=Verbosity.VERBOSE)
        self.line(f'Store: "{store.project_path}"', verbosity=Verbosity.NORMAL)
        if dry_run:
            self.line(
                "This is a dry run of backup.", style="info", verbosity=Verbosity.NORMAL
            )
        self.line(f"Commencing backup...")
        if perform:
            failures = store.backup()
            if failures:
                self.line(
                    "These are the failures:", style="error", verbosity=Verbosity.NORMAL
                )
                self.line(
                    "\n".join(str(f) for f in failures),
                    style="error",
                    verbosity=Verbosity.NORMAL,
                )


if __name__ == "__main__":
    from cleo import Application
    from cleo import CommandTester

    application = Application()
    application.add(BackupCommand())
    command = application.find("backup -vv C:/sparse_store")
