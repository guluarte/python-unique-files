# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
# ]
# ///

import click
import hashlib
import json
from pathlib import Path
import os

CHECKSUM_FILE = ".checksums.json"


def calculate_checksum(file_path):
    """Calculates the SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def load_checksums(directory):
    """Loads the checksums from the checksum file."""
    checksum_path = Path(directory) / CHECKSUM_FILE
    if checksum_path.exists():
        with open(checksum_path, "r") as f:
            return json.load(f)
    return {}


def save_checksums(directory, checksums):
    """Saves the checksums to the checksum file."""
    checksum_path = Path(directory) / CHECKSUM_FILE
    with open(checksum_path, "w") as f:
        json.dump(checksums, f, indent=4)


@click.command()
@click.argument(
    "directory", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option("--dry-run", is_flag=True, help="Don't actually do anything.")
@click.option(
    "--min-size", default=1024 * 1024, help="Minimum file size in bytes to consider."
)
def find_duplicates(directory, dry_run, min_size):
    """
    Finds duplicate files in a directory and its subdirectories,
    creates symbolic links for them, and saves checksums to avoid re-calculating them.
    A checksum file is created in each subdirectory.
    """
    files_by_checksum = {}

    for root, _, files in os.walk(directory):
        checksums = load_checksums(root)

        for filename in files:
            file_path = Path(root) / filename
            if file_path.is_symlink() or filename == CHECKSUM_FILE:
                continue

            if os.path.getsize(file_path) < min_size:
                continue

            file_path_str = str(file_path)
            if file_path_str not in checksums:
                checksums[file_path_str] = calculate_checksum(file_path)
                click.echo(f"Checksummed: {file_path}")

            checksum = checksums[file_path_str]
            if checksum not in files_by_checksum:
                files_by_checksum[checksum] = []
            files_by_checksum[checksum].append(file_path_str)

        save_checksums(root, checksums)

    for checksum, files in files_by_checksum.items():
        if len(files) > 1:
            original = files[0]
            click.echo(f"\nDuplicates found for checksum: {checksum}")
            click.echo(f"  Original: {original}")
            for duplicate in files[1:]:
                click.echo(f"  Duplicate: {duplicate}")
                if dry_run:
                    click.echo(f"    (Dry run) Would remove and link to {original}")
                else:
                    os.remove(duplicate)
                    os.symlink(original, duplicate)
                    click.echo(f"    -> Linked to {original}")


if __name__ == "__main__":
    find_duplicates()
