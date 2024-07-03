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
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True
argsp = argsubparsers.add_parser("init", help="Initialize an empty git repository.")
argsp.add_argument(
    "path",
    metavar="directory",
    nargs="?",
    default=".",
    help="Where to create the repository.",
)


class Repository(object):
    """The repository class."""

    worktree = None
    git_directory = None
    conf = None

    def __init__(self, path, new_repo=False):
        self.worktree = path
        self.git_directory = os.path.join(path, ".git")


# Helper Functions


def default_config():
    parser = configparser.ConfigParser()
    parser.add_section("core")
    parser.set("core", "repositoryformatversion", "0")
    parser.set("core", "filemode", "true")
    parser.set("core", "bare", "false")
    return parser


def find_root(current_path="."):
    path = os.path.realpath(current_path)
    if path == "/":
        raise Exception("No Git repository exists")
    find_root(os.path.join(path, ".."))


def create_dir(repo: Repository, *path) -> str:
    """Create the directory at path relative to repository.git_directory"""
    os.makedirs(os.path.join(repo.git_directory, *path), exist_ok=True)


# Main Commands
def init(path="."):
    repo = Repository(os.path.abspath(path), True)
    if os.path.exists(repo.git_directory):
        raise Exception(f"Git directory already exists at {repo.git_directory}.")
    if os.path.exists(repo.worktree) and not os.path.isdir(repo.worktree):
        raise Exception(f"{repo.worktree} already exists but is not a directory.")
    os.makedirs(repo.worktree, exist_ok=True)
    create_dir(repo, "branches")
    create_dir(repo, "objects")
    create_dir(repo, "refs", "heads")
    create_dir(repo, "refs", "tags")
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
