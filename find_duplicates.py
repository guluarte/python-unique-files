# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
# ]
# ///

import click
import hashlib
from pathlib import Path
import os


def calculate_checksum(file_path):
    """Calculates the SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def get_checksum_file_path(file_path):
    """Returns the path to the checksum file for a given file."""
    return Path(str(file_path) + ".sha256")


def read_checksum(checksum_file_path):
    """Reads the checksum from a checksum file if it exists."""
    if checksum_file_path.exists():
        with open(checksum_file_path, "r") as f:
            return f.read().strip()
    return None


def write_checksum(checksum_file_path, checksum):
    """Saves the checksum to a file."""
    with open(checksum_file_path, "w") as f:
        f.write(checksum)


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
    creates symbolic links for them, and saves a checksum file for each file to avoid re-calculating them.
    """
    files_by_checksum = {}

    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = Path(root) / filename

            # Check if the file is a symlink or a checksum file
            if file_path.is_symlink() or str(file_path).endswith(".sha256"):
                continue

            if os.path.getsize(file_path) < min_size:
                continue

            click.echo(f"Processing: {file_path}")

            checksum_file = get_checksum_file_path(file_path)
            checksum = read_checksum(checksum_file)

            if not checksum:
                checksum = calculate_checksum(file_path)
                write_checksum(checksum_file, checksum)
                click.echo(f"Checksummed: {file_path}")

            if checksum not in files_by_checksum:
                files_by_checksum[checksum] = []
            files_by_checksum[checksum].append(str(file_path))

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
