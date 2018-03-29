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

from metadb.io import *
from metadb.model import *


def test_read_general(session):
    read_general(basename='foo', parent=None, session=session)
    p1 = session.query(Path).one()
    m = session.query(Metadata).one()
    assert p1.path == 'foo'
    assert p1.meta == m

    # Identical paths should not create a new object
    read_general(basename='foo', parent=None, session=session)
    p2 = session.query(Path).one()
    assert p1 == p2


test_data = ('http://dapds00.nci.org.au/thredds/dodsC/rr3/CMIP5/output1/'
             'CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/latest/'
             'tas/tas_Amon_ACCESS1-0_historical_r1i1p1_185001-200512.nc')


def test_read_netcdf_metadata(session):
    meta = Metadata()
    read_netcdf_metadata(test_data, meta, session=session)

    m = session.query(Metadata).one()

    assert m.attributes['institute_id'].value == 'CSIRO-BOM'

    assert m.variables['tas'].name == 'tas'
    assert m.variables['tas'].dimensions[0].name == 'time'
    assert m.variables['tas'].dimensions[1].name == 'lat'
    assert m.variables['tas'].dimensions[2].name == 'lon'
    assert m.variables['tas'].attributes['units'].value == 'K'


def test_read_general_netcdf(session):
    read_general(test_data, parent=None, session=session)

    p = session.query(Path).one()
    assert p.path == test_data

    m = session.query(Metadata).one()

    assert m.attributes['institute_id'].value == 'CSIRO-BOM'

    assert m.variables['tas'].name == 'tas'
    assert m.variables['tas'].dimensions[0].name == 'time'
    assert m.variables['tas'].dimensions[1].name == 'lat'
    assert m.variables['tas'].dimensions[2].name == 'lon'
    assert m.variables['tas'].attributes['units'].value == 'K'
