"""Upload the contents of your Downloads folder to Dropbox.

This is an example app for API v2.
"""

import argparse
import contextlib
import datetime
import os
import sys
import time
import unicodedata

import dropbox


def main():
    """Main program.

    Parse command line, then iterate over files and directories under
    rootdir and upload all files.  Skips some temporary files and
    directories, and avoids duplicate uploads by comparing size and
    mtime with the server.
    """
    parser = argparse.ArgumentParser(description="Sync ~/Downloads to Dropbox")
    parser.add_argument(
        "folder", nargs="?", default="Downloads", help="Folder name in your Dropbox"
    )
    parser.add_argument(
        "rootdir", nargs="?", default="~/Downloads", help="Local directory to upload"
    )
    parser.add_argument(
        "--token",
        default="",
        help="Access token (see https://www.dropbox.com/developers/apps)",
    )
    parser.add_argument(
        "--yes", "-y", action="store_true", help="Answer yes to all questions"
    )
    parser.add_argument(
        "--no", "-n", action="store_true", help="Answer no to all questions"
    )
    parser.add_argument(
        "--default", "-d", action="store_true", help="Take default answer on all questions"
    )
    args = parser.parse_args()
    if sum(bool(b) for b in (args.yes, args.no, args.default)) > 1:
        print("At most one of --yes, --no, --default is allowed")
        sys.exit(2)
    if not args.token:
        print("--token is mandatory")
        sys.exit(2)

    folder = args.folder
    rootdir = os.path.expanduser(args.rootdir)
    print("Dropbox folder name:", folder)
    print("Local directory:", rootdir)
    if not os.path.exists(rootdir):
        print(rootdir, "does not exist on your filesystem")
        sys.exit(1)
    elif not os.path.isdir(rootdir):
        print(rootdir, "is not a folder on your filesystem")
        sys.exit(1)

    dbx = dropbox.Dropbox(args.token)

    for dn, dirs, files in os.walk(rootdir):
        subfolder = dn[len(rootdir) :].strip(os.path.sep)
        listing = list_folder(dbx, folder, subfolder)
        print("Descending into", subfolder, "...")

        # First do all the files.
        for name in files:
            fullname = os.path.join(dn, name)
            nname = unicodedata.normalize("NFC", name)
            if name.startswith("."):
                print("Skipping dot file:", name)
            elif name.startswith("@") or name.endswith("~"):
                print("Skipping temporary file:", name)
            elif name.endswith(".pyc") or name.endswith(".pyo"):
                print("Skipping generated file:", name)
            elif nname in listing:
                md = listing[nname]
                mtime = os.path.getmtime(fullname)
                mtime_dt = datetime.datetime.utcfromtimestamp(mtime)
                size = os.path.getsize(fullname)
                if (
                    isinstance(md, dropbox.files.FileMetadata)
                    and mtime_dt == md.client_modified
                    and size == md.size
                ):
                    print(name, "is already synced [stats match]")
                else:
                    print(name, "exists with different stats, downloading")
                    res = download(dbx, folder, subfolder, name)
                    with open(fullname, "rb") as f:
                        data = f.read()
                    if res == data:
                        print(name, "is already synced [content match]")
                    else:
                        print(name, "has changed since last sync")
                        if yesno(f"Refresh {name}", False, args):
                            upload(
                                dbx, fullname, folder, subfolder, name, overwrite=True
                            )
            elif yesno(f"Upload {name}", True, args):
                upload(dbx, fullname, folder, subfolder, name)

        # Then choose which subdirectories to traverse.
        keep = []
        for name in dirs:
            if name.startswith("."):
                print("Skipping dot directory:", name)
            elif name.startswith("@") or name.endswith("~"):
                print("Skipping temporary directory:", name)
            elif name == "__pycache__":
                print("Skipping generated directory:", name)
            elif yesno(f"Descend into {name}", True, args):
                print("Keeping directory:", name)
                keep.append(name)
            else:
                print("OK, skipping directory:", name)
        dirs[:] = keep


def dropbox_path(*parts):
    """Build a Dropbox path from parts, normalizing separators."""
    return "/" + "/".join(p.replace(os.path.sep, "/") for p in parts if p)


def list_folder(dbx, folder, subfolder):
    """List a folder.

    Return a dict mapping unicode filenames to
    FileMetadata|FolderMetadata entries.
    """
    path = dropbox_path(folder, subfolder)
    try:
        with stopwatch("list_folder"):
            res = dbx.files_list_folder(path)
    except dropbox.exceptions.ApiError as err:
        print("Folder listing failed for", path, "-- assumed empty:", err)
        return {}
    return {entry.name: entry for entry in res.entries}


def download(dbx, folder, subfolder, name):
    """Download a file.

    Return the bytes of the file, or None if it doesn't exist.
    """
    path = dropbox_path(folder, subfolder, name)
    with stopwatch("download"):
        try:
            md, res = dbx.files_download(path)
        except dropbox.exceptions.HttpError as err:
            print("*** HTTP error", err)
            return None
    data = res.content
    print(len(data), "bytes; md:", md)
    return data


def upload(dbx, fullname, folder, subfolder, name, overwrite=False):
    """Upload a file.

    Return the request response, or None in case of error.
    """
    path = dropbox_path(folder, subfolder, name)
    mode = (
        dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add
    )
    mtime = os.path.getmtime(fullname)
    with open(fullname, "rb") as f:
        data = f.read()
    with stopwatch(f"upload {len(data)} bytes"):
        try:
            res = dbx.files_upload(
                data,
                path,
                mode,
                client_modified=datetime.datetime.utcfromtimestamp(mtime),
                mute=True,
            )
        except dropbox.exceptions.ApiError as err:
            print("*** API error", err)
            return None
    print("uploaded as", res.name)
    return res


def yesno(message, default, args):
    """Handy helper function to ask a yes/no question.

    Command line arguments --yes or --no force the answer;
    --default to force the default answer.

    Otherwise a blank line returns the default, and answering
    y/yes or n/no returns True or False.

    Retry on unrecognized answer.

    Special answers:
    - q or quit exits the program
    - p or pdb invokes the debugger
    """
    if args.default:
        print(f"{message}? [auto] {'Y' if default else 'N'}")
        return default
    if args.yes:
        print(message + "? [auto] YES")
        return True
    if args.no:
        print(message + "? [auto] NO")
        return False
    if default:
        message += "? [Y/n] "
    else:
        message += "? [N/y] "
    while True:
        answer = input(message).strip().lower()
        if not answer:
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        if answer in ("q", "quit"):
            print("Exit")
            raise SystemExit(0)
        if answer in ("p", "pdb"):
            breakpoint()
        print("Please answer YES or NO.")


@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print(f"Total elapsed time for {message}: {t1 - t0:.3f}")


if __name__ == "__main__":
    main()
