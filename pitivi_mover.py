import argparse
import glob
import os
import shutil
import textwrap
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from xml.etree import ElementTree


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent(
        """\
        Tries to fix asset paths in Pitivi files after they have been moved.
        The provided `xges_path` path with be searched for all files ending
        with ".xges".  Then the asset paths within each xges file will be
        updated by changing `old_path` into `new_path`.  A backup copy of the
        original xges file is created if it does not already exist.  
        """
    ),
    epilog=textwrap.dedent(
        """\
        Note that only the portion of the paths that differ needs to be
        specified.  I.E. in the `old_path` and the `new_path` arguments,
        prefixes and suffixes in common can be omitted.

        Copyright 2022, John Cole <jhcole@purdue.edu>
        """
    ),
)

parser.add_argument(
    "xges_path", help="A directory path with xges files that need to be updated."
)
parser.add_argument("old_path", help="The path to the assets previous location.")
parser.add_argument("new_path", help="The path to the assets current location.")


def backup_file(orig_path):
    """Backup the original file by appending the suffix "original" if it
    doesn't already exist.  The original file is moved to the new location to
    preserve all metadata.  Then the file is copied from the new location back
    to the original location using copy2 to preserve as much metadata as
    possible.
    """
    backup_path = f"{orig_path}.original"
    if os.path.exists(backup_path):
        print(f"Skipping backup of {orig_path} because {backup_path} already exists.")
    else:
        print(f'Moving "{orig_path}"\n    to "{backup_path}"')
        shutil.move(orig_path, backup_path)  # Move to keep all metadata.
        shutil.copy2(backup_path, orig_path)  # Copy back to keep most metadata.


def update_paths(tree, old_path, new_path):
    """Update the paths in the `id` and `proxy-id` attributes of each asset,
    and in the `asset-id` attribute of each clip.
    """

    def update_uri(uri_str):
        """Replace old_path with new_path in a URI string if it represents a
        file path.
        """
        uri = urlsplit(uri_str)._asdict()
        if uri["scheme"] == "file":
            # Remove URL quoting (e.g. convert %20 into a spaces, etc.) before
            # path substitution.
            path = unquote(uri["path"]).replace(old_path, new_path, 1)

            # Check if the new path exists.
            if file_exists(path):
                # Reconstruct the uri and update the attribute.
                uri["path"] = quote(path)
            return urlunsplit(uri.values())
        return uri_str

    def file_exists(path):
        """Check if a file exists and report update skipping if not."""
        if os.path.exists(path):
            return True
        else:
            print(f"Warning: {path} does not exist; skipping.")

    # Update the paths in each asset.
    for asset in tree.findall(".//asset"):
        # Both original and proxy assets have an id attribute.
        asset.attrib["id"] = update_uri(asset.attrib["id"])

        # Original clips also have a proxy-id.
        if asset.get("proxy-id"):
            asset.attrib["proxy-id"] = update_uri(asset.attrib["proxy-id"])

    # Update the paths in each clip
    for clip in tree.findall(".//clip"):
        # Each clip has an asset-id.
        clip.attrib["asset-id"] = update_uri(clip.attrib["asset-id"])


def main():
    args = parser.parse_args()

    # Find the xges files.
    xges_files = glob.iglob("**/*.xges", root_dir=args.xges_path, recursive=True)

    for xges_file in xges_files:
        # Construct the full path of this xges file.
        xges_file_path = os.path.join(args.xges_path, xges_file)

        # Create a tree from the xml input file.
        tree = ElementTree.parse(xges_file_path)

        # Backup the original file.
        backup_file(xges_file_path)

        # Report what is being changed.
        print(
            f'Changing "{args.old_path}"\n'
            f'      to "{args.new_path}"\n'
            f'      in "{xges_file_path}"'
        )

        # Update each path.
        update_paths(tree, args.old_path, args.new_path)

        # Save the updated file.
        tree.write(xges_file_path)
        print("Done\n")


if __name__ == "__main__":
    main()
