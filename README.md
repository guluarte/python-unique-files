# Python Unique Files Finder

This project contains two Python scripts to find and manage duplicate files within a specified directory and its subdirectories.

## Scripts

1.  **`find_duplicates.py`**: Finds files that are exact duplicates by comparing their SHA256 checksums.
2.  **`find_potential_duplicates.py`**: Finds files that have the same name and similar file sizes, which are likely to be different versions of the same file.

Both scripts are designed to be run with `uv`, which automatically handles dependencies.

---
## `find_duplicates.py` - Find Exact Duplicates

This script identifies files with identical content by calculating and comparing their SHA256 checksums. It can replace duplicate files with symbolic links to save disk space.

### Usage

```bash
uv run find_duplicates.py [OPTIONS] DIRECTORY
```

### Options

-   `--dry-run`: Perform a dry run to see what changes would be made without modifying any files.
-   `--min-size BYTES`: The minimum file size in bytes to consider. Default is 1MB.

---
## `find_potential_duplicates.py` - Find Potential Duplicates by Name and Size

This script finds files that have the same name and a similar file size. This is useful for finding different versions of the same file.

### Usage

```bash
uv run find_potential_duplicates.py [OPTIONS] DIRECTORY
```

### Options

-   `--min-size INTEGER`: Minimum file size in bytes to consider. Defaults to 10MB.
-   `--auto`: Enable auto mode. Automatically links files if their size difference is less than 500KB.
-   `--original-dir PATH`: Specify a directory to be preferred for original files.
-   `--help`: Show the help message and exit.

### How the "Original" File is Determined (`find_potential_duplicates.py`)

The script uses the following logic to decide which file to keep as the original:

1.  **`--original-dir` specified**: If a file is found within this directory, it is chosen as the original. If multiple files are in that directory, the largest one is chosen.
2.  **No `--original-dir`**: The largest file among the set of duplicates is chosen as the original.

## Examples

### Find exact duplicates

```bash
# Do a dry run on a directory with large video files
uv run find_duplicates.py --dry-run --min-size 50000000 /path/to/videos

# Run for real on a directory of documents
uv run find_duplicates.py /path/to/documents
```

### Find potential duplicates by name and size

```bash
# Interactive mode on a directory
uv run find_potential_duplicates.py /home/user/documents

# Auto mode, linking files with < 500KB difference
uv run find_potential_duplicates.py --auto /home/user/downloads

# Prefer originals from a specific directory
uv run find_potential_duplicates.py --original-dir /home/user/all_photos/originals /home/user/all_photos
```