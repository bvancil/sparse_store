# sparse_store
Backup sparse collections of configuration files scattered across a system using a command-line utility

At present, only minimal backup capability is provided with no restore option.

## Installation

Using poetry:

```{bash}
poetry build
```

Then, in the environment in which you mean to install `sparse_store`:

```{bash}
python -m pip install /path/to/sparse_store/dist/sparse_store-X.X.X-py3-none-any.whl
```

## Running

For help, type:

```{bash}
sparse_store
```

### Initialize a sparse store:

```{bash}
sparse_store init /path/to/backup
```

Edit the `sparse_store.yml` example file in `/path/to/backup` to get started.

### Backup the files and directories you specified:

```{bash}
sparse_store backup -vv /path/to/backup
```

### Further suggestions

If you have mainly text files, you might consider putting `/path/to/backup` under version control.

