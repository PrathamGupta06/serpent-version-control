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

argparser = argparse.ArgumentParser(description='Serpent Version Control System (SVC): A friendly and helpful serpent.')
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

class Repository(object):
    """The repository class."""
    worktree = None
    git_directory = None
    conf = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.git_directory = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.git_directory)):
            raise Exception(f"Not a git repository {path}" )

        
def main(argv = sys.argv[1:]):
    args = argparser.parse_args(argv)