# uv Dependency Management Workflow

This document describes how to manage Python dependencies in this project using [`uv`](https://github.com/astral-sh/uv).

## Initialization

To set up `uv` for dependency management, run:

```sh
uv init
```

This creates a `pyproject.toml` and a `uv.lock` file for your project.

## Adding Dependencies

To add a new package:

```sh
uv pip install <package>
```
or
```sh
uv add <package>
```

This updates both `pyproject.toml` and `uv.lock`.

## Updating Dependencies

To update a specific package:

```sh
uv pip install --upgrade <package>
```
or
```sh
uv update <package>
```

To update all dependencies:

```sh
uv update
```

## Removing Dependencies

To remove a package:

```sh
uv remove <package>
```

This will update your project files accordingly.

## Installing from Lock File

To install all dependencies exactly as specified in `uv.lock`:

```sh
uv pip install --sync
```
or
```sh
uv install
```

## Migration Notes

No migration steps are needed since there are no legacy dependency files.

## Advanced Usage

For advanced features (such as constraints, extras, or environment management), refer to the official [`uv documentation`](https://docs.astral.sh/uv/).