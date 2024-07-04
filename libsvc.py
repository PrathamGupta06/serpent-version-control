import argparse
import collections
import configparser
from datetime import datetime
import grp, pwd
from fnmatch import fnmatch
import hashlib
from math import ceil
import os
import re
import sys
import zlib

argparser = argparse.ArgumentParser(
    description="Serpent Version Control System (SVC): A friendly and helpful serpent."
)
subparser = argparser.add_subparsers(title="Commands", dest="command")
subparser.required = True
# Subparsers
# Init
added_parser = subparser.add_parser("init", help="Create an empty Git repository.")
added_parser.add_argument(
    "directory",
    metavar="directory",
    nargs="?",
    default=".",
    help="Initializes the git repository in this directory. Creates the directory if it does not exist.",
)


class Repository:
    """The repository class."""

    worktree = None
    git_directory = None
    conf = None

    def __init__(self, path: str, new_repo: bool = False):
        self.worktree = os.path.abspath(path)
        self.git_directory = os.path.join(self.worktree, ".git")


class GitObject:
    def __init__(self, data=None):
        if data != None:
            self.deserialize(data)

    def deserialize(self, repo):
        # Not Implemented
        pass

    def serialize(self, repo):
        # Not Implemented
        pass


# Helper Functions


def default_config() -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    parser.add_section("core")
    parser.set("core", "repositoryformatversion", "0")
    parser.set("core", "filemode", "true")
    parser.set("core", "bare", "false")
    return parser


def find_root(current_path: str = ".") -> Repository:
    """Searches for root directory in current and parent directory and returns the path of the root."""
    path = os.path.realpath(current_path)
    if os.path.isdir(os.path.join(path, ".git")):
        return Repository(path)
    if path == "/":
        raise Exception("No Git repository exists")
    find_root(os.path.join(path, ".."))


def create_dir(repo: Repository, path: str) -> str:
    """Create the directory at path relative to repository.git_directory"""
    os.makedirs(os.path.join(repo.git_directory, path), exist_ok=True)


def read_object(repo: Repository, sha: str) -> object:
    path = f"{repo.git_directory}/objects/{sha[:2]}/{sha[2:]}"
    if not os.path.isfile(path):
        return None

    with open(path, "rb") as f:
        raw_file = zlib.decompress(f.read())

        # Read the object type (i.e. commit, tree, log, blob)
        header_separator = raw_file.find(b" ")
        object_type = raw_file[:header_separator].decode("ascii")

        # Read the object size
        header_ending = raw_file.find(b"\x00", header_separator)
        size = int(raw_file[header_separator:header_ending].decode("ascii"))

        if size != len(raw_file) - header_ending - 1:
            raise Exception(f"File at {path} has mismatched object size.")

        match object_type:
            case "commit":
                cmd = GitCommit
            case "tree":
                cmd = GitTree
            case "tag":
                cmd = GitTag
            case "blob":
                cmd = GitBlob
            case _:
                raise Exception(f"Invalid Object Type f{object_type}")
    return cmd(raw_file[header_ending + 1 :])


def get_sha(obj: object) -> str:
    # The object should have its own serialization function
    data = obj.serialize()
    # Add header
    data = obj.type + b" " + str(len(data)).encode() + b"\x00" + data
    sha1 = hashlib.sha1(data).hexdigest()
    return sha1


def write_object(repo: Repository, obj: object) -> None:
    sha = get_sha(obj)
    dir_path = f"{repo.git_directory}/objects/{sha[0:2]}"
    create_dir(dir_path)
    obj_path = f"{dir_path}/{sha[2:]}"
    with open(obj_path, "wb") as f:
        # Write the zlib compressed sha
        f.write(zlib.compress(sha))


# Main Commands
def init(path="."):
    # Create repo object
    repo = Repository(os.path.abspath(path), True)
    # Check if git is not already initialized and that the work path is a directory
    if os.path.exists(repo.git_directory):
        raise Exception(f"Git directory already exists at {repo.git_directory}.")
    if os.path.exists(repo.worktree) and not os.path.isdir(repo.worktree):
        raise Exception(f"{repo.worktree} already exists but is not a directory.")
    # Create Required Directories
    os.makedirs(repo.worktree, exist_ok=True)
    create_dir(repo, "branches")
    create_dir(repo, "objects")
    create_dir(repo, "refs/heads")
    create_dir(repo, "refs/tags")
    # .git/description
    with open(os.path.join(repo.git_directory, "description"), "w") as desc_file:
        desc_file.write(
            "Unnamed repository; edit this file 'description' to name the repository.\n"
        )

    # .git/HEAD
    with open(os.path.join(repo.git_directory, "HEAD"), "w") as head_file:
        head_file.write("ref: refs/heads/main\n")

    # config
    with open(os.path.join(repo.git_directory, "config"), "w") as config_file:
        config = default_config()
        config.write(config_file)
    return repo


def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        case "init":
            init(args.path)
        case _:
            print("Invalid Command")
