# Hello World Python

A minimal Python project that prints `Hello, world!`.

## Requirements

- Python 3.9 or newer

## Run

Run directly from the repository:

```bash
PYTHONPATH=src python3 -m hello_world.main
```

Or install the package in editable mode and use the console script:

```bash
python3 -m pip install -e .
hello-world
```

## Test

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
