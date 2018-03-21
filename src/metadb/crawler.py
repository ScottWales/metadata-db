#!/usr/bin/env python
# Copyright 2018 Scott Wales
# author: Scott Wales <scott.wales@unimelb.edu.au>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import print_function
from .model import Path
from .query import find_or_create
import os

try:
    from os import scandir
except ImportError:
    from scandir import scandir

# FileNotFoundError not available in Python 2
try:
    FileNotFoundError
except NameError:
    PermissionError = IOError
    FileNotFoundError = IOError

def crawl_recursive(session, basedir, collection=None):
    basedir = os.path.abspath(basedir)

    for entry in scandir(basedir):
        print(entry.path, type(entry.path))
        p = find_or_create(session, Path, path=entry.path)
        p.collections.add(collection)

        try:
            p.update_stat(entry.stat())
            if entry.is_dir() and not entry.is_symlink():
                crawl_recursive(session, entry, collection)
        except PermissionError:
            # Not readable
            pass
        except FileNotFoundError:
            # Broken symlink
            pass
