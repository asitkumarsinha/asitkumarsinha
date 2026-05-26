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

## Read Excel Files

The package includes a helper that reads exactly four Excel workbooks from their active sheets:

```python
from hello_world.main import read_four_excel_files

rows_by_file = read_four_excel_files([
    "file_1.xlsx",
    "file_2.xlsx",
    "file_3.xlsx",
    "file_4.xlsx",
])
```

Each workbook is returned as a list of dictionaries. The first row is used as the header row.

## Test

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
