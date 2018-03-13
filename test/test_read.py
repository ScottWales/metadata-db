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

from metadb.io import read_netcdf
from metadb.model import *

test_data = ('http://dapds00.nci.org.au/thredds/dodsC/rr3/CMIP5/output1/'
            'CSIRO-BOM/ACCESS1-0/historical/mon/atmos/Amon/r1i1p1/latest/'
            'tas/tas_Amon_ACCESS1-0_historical_r1i1p1_185001-200512.nc')

def test_read(session):
    read_netcdf(test_data, session=session) 

    m = session.query(Metadata).one()
