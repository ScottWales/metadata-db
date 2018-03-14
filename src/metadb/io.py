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
import netCDF4
import six

def read_netcdf(path, session):
    """
    Import a netCDF file's metadata into the DB
    """
    print("Loading %s"%path)

    data = netCDF4.Dataset(path, mode='r')

    meta = Metadata()
    path = Path(path=path, meta = meta)

    dimensions = [
        Dimension(name=d.name, size=d.size, meta=meta)
        for d in six.itervalues(data.dimensions)]
    session.add_all(dimensions)

    variables = [
        Variable(name=v.name, type=str(v.dtype), meta=meta)
        for v in six.itervalues(data.variables)]
    session.add_all(variables)

    # Get the metadata for each variable
    for v in six.itervalues(data.variables):
        attrs = [Attribute(key=a, value=str(v.getncattr(a)))
                for a in v.ncattrs()]
        session.add_all(attrs)

        meta.variables[v.name].attributes = {a.key: a for a in attrs}
        meta.variables[v.name].dimensions = [meta.dimensions[d] for d in v.dimensions]

    # Get the global metadata
    attrs = [Attribute(key=a, value=str(data.getncattr(a)))
            for a in data.ncattrs()]
    session.add_all(attrs)
    meta.attributes = {a.key: a for a in attrs}

    session.add(meta)

    return meta
