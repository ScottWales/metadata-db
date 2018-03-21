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
"""
Database queries
"""
from __future__ import print_function

from .model import *

from sqlalchemy.orm import aliased
from sqlalchemy import and_
import six


def search_metadata(session,
                    variables=[],
                    file_attributes=[],
                    variable_attributes=[]):
    global_attrs = aliased(Attribute)
    variable_attrs = aliased(Attribute)

    q = (session
         .query(Metadata)
         .join(Metadata.variables)
         .join(global_attrs, Metadata.attributes, isouter=True)
         .join(variable_attrs, Variable.attributes, isouter=True)
         .distinct()
         )

    if variables:
        q = q.filter(Variable.name.in_(variables))

    if file_attributes:
        for k, v in file_attributes:
            q = q.filter(and_(global_attrs.key == k, global_attrs.value == v))

    if variable_attributes:
        for k, v in variable_attributes:
            q = q.filter(and_(variable_attrs.key == k,
                              variable_attrs.value == v))

    return q


def find_or_create(session, klass, **kwargs):
    """
    Return either an existing klass object that matches kwargs, or create a new
    one
    """
    r = session.query(klass).filter_by(**kwargs).one_or_none()

    if r is None:
        r = klass(**kwargs)
        session.add(r)

    return r
