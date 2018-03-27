#!/usr/bin/env python
# Copyright 2018 ARC Centre of Excellence for Climate Systems Science
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
from .model import *
from .query import find_or_create
import netCDF4
import six
import os
from stat import *

# FileNotFoundError not available in Python 2
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def read_general(basename, session, parent=None, collections=set()):
    """
    General purpose metadata reader
    """

    path = find_or_create(session, Path, basename=basename, parent=parent)
    path.collections.update(collections)
    session.add(path)
    session.commit()

    try:
        stat = os.stat(path.path)
        mtime = stat[ST_MTIME]
        size = stat[ST_SIZE]
    except (FileNotFoundError, OSError):
        # E.g. OpenDAP URL
        mtime = -1
        size = -1

    meta = path.meta
    if meta is not None:
        if meta.mtime < mtime:
            raise Exception(
                "File %s has been modified since last seen, "
                "updates are not supported")
        return
    else:
        meta = Metadata(mtime=mtime, size=size)
        path.meta = meta

    read_netcdf_metadata(path.path, path.meta, session)


def read_netcdf_attributes(source, session):
    """
    Read attributes from a NetCDF object
    """
    attrs = [find_or_create(session,
                            Attribute,
                            key=a,
                            value=str(source.getncattr(a)))
             for a in source.ncattrs()]

    session.add_all(attrs)
    return attrs


def read_netcdf_metadata(path, meta, session):
    """
    Import a netCDF file's metadata into the DB

    No-op if path is not a NetCDF file
    """
    print("Loading %s" % path)

    try:
        data = netCDF4.Dataset(path, mode='r')
    except (FileNotFoundError, OSError):
        # Not a Netcdf file, return
        return

    session.add(meta)

    dimensions = [
        find_or_create(session, Dimension, name=d.name, size=d.size, meta=meta)
        for d in six.itervalues(data.dimensions)]
    session.add_all(dimensions)

    variables = [
        Variable(name=v.name, type=str(v.dtype), meta=meta)
        for v in six.itervalues(data.variables)]
    session.add_all(variables)

    # Get the metadata for each variable
    for v in six.itervalues(data.variables):
        attrs = read_netcdf_attributes(v, session)

        meta.variables[v.name].attributes = {a.key: a for a in attrs}
        meta.variables[v.name].dimensions = [meta.dimensions[d]
                                             for d in v.dimensions]

    # Get the global metadata
    attrs = read_netcdf_attributes(data, session)
    meta.attributes = {a.key: a for a in attrs}
