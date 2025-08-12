# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
# ]
# ///

import click
import os
from collections import defaultdict


def find_duplicate_files(directory, min_size, auto=False, original_dir=None):
    """
    Finds files with the same name and similar file size in a directory.
    """
    files_by_name = defaultdict(list)
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                if os.path.islink(filepath):
                    continue
                filesize = os.path.getsize(filepath)
                if filesize >= min_size:
                    files_by_name[filename].append((filepath, filesize))
            except OSError:
                # Ignore files that can't be accessed
                pass

    for filename, files in files_by_name.items():
        if len(files) > 1:
            original_file_tuple = None

            if original_dir:
                files_in_original_dir = []
                for f in files:
                    if f[0].startswith(original_dir):
                        files_in_original_dir.append(f)

                if len(files_in_original_dir) > 0:
                    files_in_original_dir.sort(key=lambda x: x[1], reverse=True)
                    original_file_tuple = files_in_original_dir[0]

            if not original_file_tuple:
                files.sort(key=lambda x: x[1], reverse=True)
                original_file_tuple = files[0]

            original_filepath, original_size = original_file_tuple

            duplicates = [f for f in files if f[0] != original_filepath]

            for dup_filepath, dup_size in duplicates:
                if abs(original_size - dup_size) < 1024 * 1024:
                    size_diff_kb = abs(original_size - dup_size) / 1024
                    click.echo("Found potential duplicates:")
                    click.echo(
                        f"  - Original:  {original_filepath} ({original_size} bytes)"
                    )
                    click.echo(f"  - Duplicate: {dup_filepath} ({dup_size} bytes)")
                    click.echo(f"  - Size difference: {size_diff_kb:.2f} KB")

                    perform_link = False
                    if auto and size_diff_kb < 500:
                        perform_link = True
                        click.echo("Auto-linking files (size difference < 500KB).")
                    elif not auto:
                        if click.confirm(
                            f"Link '{os.path.basename(dup_filepath)}' to '{os.path.basename(original_filepath)}'? "
                            f"This will delete the duplicate file.",
                            default=False,
                        ):
                            perform_link = True

                    if perform_link:
                        try:
                            os.remove(dup_filepath)
                            os.symlink(original_filepath, dup_filepath)
                            click.echo(
                                f"Symbolic link created: {dup_filepath} -> {original_filepath}"
                            )
                        except OSError as e:
                            click.echo(f"Error creating symbolic link: {e}", err=True)


@click.command()
@click.argument(
    "directory", type=click.Path(exists=True, file_okay=False, resolve_path=True)
)
@click.option(
    "--min-size",
    default=10 * 1024 * 1024,
    help="Minimum file size in bytes to consider (default: 10MB)",
)
@click.option(
    "--auto",
    is_flag=True,
    default=False,
    help="Automatically link files with size difference < 500KB.",
)
@click.option(
    "--original-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="Directory to prefer as original.",
)
def main(directory, min_size, auto, original_dir):
    """
    Finds files with the same name and similar file size in a directory.
    """
    click.echo("Starting duplicate file finder with the following settings:")
    click.echo(f"  - Directory to scan: {directory}")
    click.echo(f"  - Minimum file size: {min_size} bytes")
    click.echo(f"  - Auto mode: {'Enabled' if auto else 'Disabled'}")
    if original_dir:
        click.echo(f"  - Original directory: {original_dir}")
    click.echo("-" * 20)

    find_duplicate_files(directory, min_size, auto, original_dir)


if __name__ == "__main__":
    main()
