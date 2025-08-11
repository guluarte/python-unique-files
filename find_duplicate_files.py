# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
# ]
# ///

import click
import os
from collections import defaultdict

def find_duplicate_files(directory, min_size):
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
            files.sort(key=lambda x: x[1], reverse=True)
            original_filepath, original_size = files[0]

            for i in range(1, len(files)):
                dup_filepath, dup_size = files[i]

                if abs(original_size - dup_size) < 1024 * 1024:
                    size_diff_kb = abs(original_size - dup_size) / 1024
                    click.echo("Found potential duplicates:")
                    click.echo(f"  - Original:  {original_filepath} ({original_size} bytes)")
                    click.echo(f"  - Duplicate: {dup_filepath} ({dup_size} bytes)")
                    click.echo(f"  - Size difference: {size_diff_kb:.2f} KB")

                    if click.confirm(
                        f"Link '{os.path.basename(dup_filepath)}' to '{os.path.basename(original_filepath)}'? "
                        f"This will delete the duplicate file.",
                        default=False,
                    ):
                        try:
                            os.remove(dup_filepath)
                            os.symlink(original_filepath, dup_filepath)
                            click.echo(
                                f"Symbolic link created: {dup_filepath} -> {original_filepath}"
                            )
                        except OSError as e:
                            click.echo(f"Error creating symbolic link: {e}", err=True)


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option('--min-size', default=10 * 1024 * 1024, help='Minimum file size in bytes to consider (default: 10MB)')
def main(directory, min_size):
    """
    Finds files with the same name and similar file size in a directory.
    """
    find_duplicate_files(directory, min_size)

if __name__ == "__main__":
    main()
