import itertools
import pathlib
from typing import Any, Iterable, List, Optional
import yaml

# Exceptions


class FormatException(Exception):
    "Base class for all sparse_store.yaml data formatting exceptions"
    pass


class NotJustASingleKeyInDictionaryFormatException(FormatException):
    "sparse_store's YAML-based format should have only dictionaries of length 1."
    pass


class DictionaryValueNotAList(FormatException):
    "sparse_store's YAML-based format should have every key introducing a list."
    pass


class UnexpectedTypeFormatException(FormatException):
    "Unexpected type in parsed YAML"
    pass


# Functions


def get_backup_section(obj):
    "Return pure config part of sparse_store.yaml file"
    return obj["backup"]


def dump_yaml(object):
    "Turn object into YAML"
    return yaml.dump(object, default_flow_style=False)


def load_yaml(stream):
    "Turn YAML into object"
    return yaml.safe_load(stream)


def path(prefix: Optional[pathlib.Path], value: str) -> pathlib.Path:
    if prefix is None:
        return pathlib.Path(value)
    return prefix / value


## Commands


class Command:
    "Base class"
    pass


class DirectoryWithSparseContents(Command):
    "Sparse (read: specified) contents of a given directory"

    def __init__(self, directory: str, contents: List[Any]):
        self.directory = directory
        self.contents = [command for command in contents]

    def __repr__(self):
        return f'{self.__class__.__name__}(directory="{self.directory}", list={self.contents})'

    def with_context(self, context: pathlib.Path) -> Iterable[pathlib.Path]:
        new_context = context / self.directory
        return itertools.chain.from_iterable(
            command.with_context(new_context) for command in self.contents
        )


class PathComponent(Command):
    "File; or Directory and full contents"

    def __init__(self, component: str):
        self.component = component

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.component}")'

    def with_context(self, context: pathlib.Path) -> Iterable[pathlib.Path]:
        return [context / self.component]


class UnknownCommand(Exception):
    "Invalid backup command provided"
    pass


def convert_backup_section_to_commands(backup: List[Any]) -> Iterable[Command]:
    """Turn parsed YAML into rules

    * backup: Something like, for instance,
        [{'FAKEDIR1': [{'FAKEDIR2': ['FILE2a', 'FILE2b']}, 'FILE1a', 'FILE1b']}, {'FAKEDIR2': ['FILE2a', 'FILE2b', 'FILE3b']}, 'FAKEDIR3']
    * length 1 Dict[str, List[Any]] ==> Turn into a command DirectoryWithSparseContents(prefix / ., .)
    * List[Any] ==> Process each subelement into a command
    * str ==>
      * dir?  ==> DirectoryWithAllContents(prefix / .)
      * file? ==> File(.)
    
    TODO: Come up with a better type than List[Any]

    """
    if isinstance(backup, list):
        return [convert_backup_section_to_commands(element) for element in backup]
    elif isinstance(backup, dict):
        # Length 1
        if len(backup) != 1:
            raise NotJustASingleKeyInDictionaryFormatException
        # Extract single key and value
        parent = list(backup.keys())[0]
        child = backup[parent]
        # List-valued
        if not isinstance(child, list):
            raise DictionaryValueNotAList
        return DirectoryWithSparseContents(
            directory=parent, contents=convert_backup_section_to_commands(child)
        )
    elif isinstance(backup, str):
        return PathComponent(component=backup)
    else:
        raise UnexpectedTypeFormatException


def convert_commands_to_paths(
    command_set: Iterable[Command], context: Optional[pathlib.Path] = None
) -> Iterable[pathlib.Path]:
    if isinstance(command_set, list):
        return itertools.chain.from_iterable(
            convert_commands_to_paths(command, context=context)
            for command in command_set
        )
    elif isinstance(command_set, PathComponent):
        return (path(context, command_set.component) for _ in range(1))
    elif isinstance(command_set, DirectoryWithSparseContents):
        new_context = path(context, command_set.directory)
        return itertools.chain.from_iterable(
            convert_commands_to_paths(command, context=new_context)
            for command in command_set.contents
        )
    else:
        raise UnknownCommand


# Config


class Config:
    "Utility class to read config file sparse_store.yaml from project_path"

    def __init__(self, project_path: pathlib.Path):
        self.project_path = project_path

    def config_file(self):
        return self.project_path / "sparse_store.yaml"

    def backup_path(self):
        return self.project_path / "backup"

    def dump(self):
        "Write config"
        self.config_file().write_text(dump_yaml(self.parsed_yaml), encoding="UTF-8")

    def load(self):
        "Read config"
        with self.config_file().open(mode="rt", encoding="UTF-8") as stream:
            self.parsed_yaml = load_yaml(stream)

    def is_loaded(self):
        try:
            self.parsed_yaml
            return True
        except AttributeError:
            return False

    def ensure_loaded(self):
        if not self.is_loaded():
            self.load()

    def backup(self):
        self.ensure_loaded()
        return get_backup_section(self.parsed_yaml)


if __name__ == "__main__":
    config = Config(pathlib.Path("C:") / "sparse_store")
    print(config)
    print(config.project_path)
    print(config.config_file())
    backup = config.backup()
    print(backup)
    commands = convert_backup_section_to_commands(backup)
    print(commands)
    paths = list(convert_commands_to_paths(commands))
    print(paths)
