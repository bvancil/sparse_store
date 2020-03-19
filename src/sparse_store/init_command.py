import pathlib

from cleo import Command

from .config import Config
from .store import Store


class InitCommand(Command):
    """
    Initializes a sparse_store

    init
        {path : path to create for sparse_store and configuration}
        {--dry-run : If set, just show what would have been done}
        {--force-dir : If set, ignore the fact that the directory exists.}
        {--force-config : If set, ignore the fact that the config file sparse_store.yaml exists in the directory.}
    """

    def handle(self):
        path = pathlib.Path(self.argument("path"))
        dry_run = self.option("dry-run")
        perform = not dry_run
        force_dir = self.option("force-dir")
        force_config = self.option("force-config")

        self.line(f"Store: {path}")
        if dry_run:
            self.line("This is a dry run of init.", style="info")

        # Handle directory creation
        if path.exists() and not force_dir:
            self.line(
                "The store already exists. Please use a path that you want to create or use --force-dir, as in:",
                style="error",
            )
            self.line(
                f'sparse_store init{" --dry-run" if dry_run else ""} --force-dir{" --force-config" if force_config else ""} "{path}"'
            )
            exit(1)
        if path.exists():
            self.line(f'Using "{path}" as store.')
        else:
            self.line(f'Creating "{path}" as store.')
            if perform:
                path.mkdir(parents=True)
        if perform:
            (path / "backup").mkdir(exist_ok=True)
            (path / "backup" / ".gitkeep").touch(exist_ok=True)

        # Create Store object
        store = Store(path, io=self.io, perform=perform)

        # Handle config creation
        config_file = store.config_file()
        if config_file.exists() and not force_config:
            self.line(
                "The store sparse_store.yaml file already exists. Please use a path that you want to create or use --force-config to wipe it, as in:",
                style="error",
            )
            self.line(
                f'sparse_store init{" --dry-run" if dry_run else ""}{" --force-dir" if force_dir else ""} --force-config "{path}"'
            )
            exit(1)
        if config_file.exists():
            gerund = "Overwriting"
        else:
            gerund = "Writing"
        self.line(f'{gerund} config file: "{config_file}"')
        if perform:
            store.config_file().write_text(
                """# This is a sample sparse_store.yaml file. Replace it with your important paths.
backup:
- path_1 # Include all contents of this directory
- path_2: # Include select contents of this directory:
  - relative_dir_path2.1: # Full path is "{path_2}/{relative_dir_path2.1}"
  - relative_file_path_2.1.1 # Full path is "{path_2}/{relative_dir_path2.1}/{relative_file_path_2.1.1}"
    - relative_file_path_2.2 # Full path is "{path_2}/{relative_file_path_2.2}"
"""
            )
