import pathlib
import re
import shutil
from typing import Iterable

from clikit.api.io import IO

from .verbosity import Verbosity


def encode_path(path: pathlib.Path) -> str:
    _, *rest = path.parts
    drive = path.drive
    new_drive = re.sub(r"^([A-Za-z]):$", r"\1_drive", drive, count=1)
    new_subpath = pathlib.Path(new_drive, *rest)
    return str(new_subpath)


def storage_path(base: pathlib.Path, path: pathlib.Path) -> pathlib.Path:
    return base / encode_path(path)


def compare_files(original_file: pathlib.Path, backup_file: pathlib.Path) -> int:
    """Returns an element of {-1, 0, 1} to indicate which has been updated latest
    
    * -1 = backup_file has been modified more recently
    *  0 = the timestamps match
    *  1 = original_file has been modified more recently 
    """

    def cmp(a, b):
        return (a > b) - (b > a)

    return cmp(original_file.stat().st_mtime, backup_file.stat().st_mtime)


def ignore_up_to_date(store_backup_path: pathlib.Path) -> Iterable[pathlib.Path]:
    """Higher-level function to return a callable for shutil.copytree
    to pass to the ignore parameter"""

    def _ignore_up_to_date(current_directory, directory_contents):
        current_directory = pathlib.Path(current_directory)
        directory_contents = (current_directory / child for child in directory_contents)
        stored_directory_contents = (
            storage_path(store_backup_path, child) for child in directory_contents
        )
        already_up_to_date_contents = (
            path
            for path, stored_path in zip(directory_contents, stored_directory_contents)
            if not path.is_dir()
            and stored_path.exists()
            and compare_files(path, stored_path) < 1
        )
        relative_paths_to_ignore = (
            path.relative_to(current_directory) for path in already_up_to_date_contents
        )
        return relative_paths_to_ignore

    return _ignore_up_to_date


class BackupPath:
    "Wrapper of pathlib.Path to enable backup/restore functionality"

    def __init__(self, path: pathlib.Path, config, io: IO, perform: bool = True):
        self.path = path
        self.config = config
        self.io = io
        self.perform = perform

    def __str__(self):
        return f"{self.__class__.__name__}({self.path!r}, ...)"

    def _add_class_name(self, x: str, separator=": ") -> str:
        "Prepend `obj`'s class name in return string"
        return f"{self.__class__.__name__}{separator}{x}"

    def storage_path(self):
        return storage_path(self.config.backup_path(), self.path)

    def remove_stored(self):
        storage_path = self.storage_path()
        if not storage_path.exists():
            self.io.write_line(
                self._add_class_name(f"Path {storage_path!r} not found; not deleting"),
                flags=Verbosity.VERBOSE,
            )
        elif storage_path.is_dir():
            self.io.write_line(
                self._add_class_name(f"Removing directory {storage_path!r}"),
                flags=Verbosity.VERBOSE,
            )
            if self.perform:
                shutil.rmtree(storage_path)
        elif storage_path.is_file():
            self.io.write_line(
                self._add_class_name(f"Removing file {storage_path!r}"),
                flags=Verbosity.VERBOSE,
            )
            if self.perform:
                storage_path.unlink()

    def backup(self):
        storage_path = self.storage_path()
        # try:
        #     self.remove_stored()
        # except PermissionError:
        #     return ("Permission error on removing stored", (storage_path, ))
        if not self.path.exists():
            self.io.write_line(
                self._add_class_name(
                    f"Warning! Path {self.path!r} not found. Cannot backup."
                ),
                flags=Verbosity.NORMAL,
            )
            return ("Path not found", (self.path,))
        elif self.path.is_dir():
            self.io.write_line(
                self._add_class_name(
                    f"Copying directory {self.path!r} to {storage_path!r}"
                ),
                flags=Verbosity.VERBOSE,
            )
            if self.perform:
                try:
                    storage_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(
                        self.path,
                        storage_path,
                        ignore=ignore_up_to_date(self.config.backup_path()),
                        dirs_exist_ok=True,
                    )
                    return None
                except PermissionError:
                    return ("Error on copy directory", (self.path, storage_path))
        elif self.path.is_file():
            if storage_path.exists():
                comparison = compare_files(self.path, storage_path)
            else:
                comparison = 1  # Needs update
            if comparison == 1:
                self.io.write_line(
                    self._add_class_name(
                        f"Copying file {self.path!r} to {storage_path!r}"
                    ),
                    flags=Verbosity.VERBOSE,
                )
                if self.perform:
                    try:
                        storage_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(self.path, storage_path)
                    except:
                        return ("Error on copy file", (self.path, storage_path))
            elif comparison == 0:
                self.io.write_line(
                    self._add_class_name(
                        f"Already up to date. Not copying file {self.path!r} to {storage_path!r}"
                    ),
                    flags=Verbosity.VERBOSE,
                )
            elif comparison == -1:
                self.io.write_line(
                    self._add_class_name(
                        f"Stored copy of {self.path!r} in {storage_path!r} is newer than original. Not copying file."
                    ),
                    flags=Verbosity.VERBOSE,
                )
            else:
                # We should never get here.
                self.io.write_line(
                    self._add_class_name(
                        f"Bad comparision between file {self.path!r} and stored file {storage_path!r}. Not copying file."
                    ),
                    flags=Verbosity.VERBOSE,
                )
        else:
            self.io.write_line(
                self._add_class_name(f"Error! Unrecognized path {self.path!r}"),
                flags=Verbosity.NORMAL,
            )
            return ("Unrecognized path", (self.path,))
        return None

    def restore(self):
        self.io.write_line(
            self._add_class_name(f"Method restore() is not yet implemented"),
            flags=Verbosity.NORMAL,
        )
