# Python Unique Files Finder

A Python script to find duplicate files within a specified directory and its subdirectories. It replaces duplicate files with symbolic links to the original file, thus saving disk space.

## Features

-   Finds duplicate files based on their SHA256 checksum.
-   Replaces duplicates with symbolic links.
-   Caches checksums in `.sha256` files to avoid re-calculation on subsequent runs.
-   Option to perform a dry run to see what changes would be made without actually modifying any files.
-   Option to set a minimum file size to consider, to avoid processing many small files.

## Requirements

-   Python 3.12+
-   `uv`

The script is designed to be run as a single file using `uv`. `uv` will read the script dependencies from the script's header and create a virtual environment automatically.

You can install `uv` by following the official instructions: https://github.com/astral-sh/uv

## Usage

```bash
uv run find_duplicates.py [OPTIONS] DIRECTORY
```

### Arguments

-   `DIRECTORY`: The directory to scan for duplicate files.

### Options

-   `--dry-run`: If set, the script will only print the actions it would take without actually deleting files or creating symbolic links.
-   `--min-size BYTES`: The minimum file size in bytes to consider for checksumming and duplicate finding. The default is 1048576 bytes (1 MiB).

## How it works

The script traverses the given directory. For each file, it calculates a SHA256 checksum. To speed up subsequent runs, the checksum is stored in a separate file with a `.sha256` extension (e.g., `my_file.txt.sha256`).

If files have the same checksum, they are considered duplicates. The script keeps the first file it encounters as the "original" and replaces all other duplicate files with a symbolic link pointing to the original.

## Example

```bash
# Do a dry run on a directory with large video files
uv run find_duplicates.py --dry-run --min-size 50000000 /path/to/videos

# Run for real on a directory of documents
uv run find_duplicates.py /path/to/documents
```