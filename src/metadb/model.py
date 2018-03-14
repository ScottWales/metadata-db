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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.orderinglist import OrderingList

Base = declarative_base()

# Many to many links
var_to_attr = Table('var_to_attr', Base.metadata,
        Column('var_id', Integer, ForeignKey('variable.id')),
        Column('attr_id', Integer, ForeignKey('attribute.id')),
        )
meta_to_attr = Table('meta_to_attr', Base.metadata,
        Column('meta_id', Integer, ForeignKey('metadata.id')),
        Column('attr_id', Integer, ForeignKey('attribute.id')),
        )
var_to_dim = Table('var_to_dim', Base.metadata,
        Column('var_id', Integer, ForeignKey('variable.id')),
        Column('dim_id', Integer, ForeignKey('dimension.id')),
        Column('ndim', Integer),
        )

class Path(Base):
    """
    File path
    """
    __tablename__ = 'path'

    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer, ForeignKey('metadata.id'))
    path = Column(Text)

    meta = relationship('Metadata', back_populates='paths')


class Metadata(Base):
    """
    Metadata sourced from a file
    """
    __tablename__ = 'metadata'

    id = Column(Integer, primary_key=True)
    sha256 = Column(String, unique=True)

    dimensions = relationship('Dimension',
            back_populates='meta',
            collection_class=attribute_mapped_collection('name'),
            )
    variables = relationship('Variable',
            back_populates='meta',
            collection_class=attribute_mapped_collection('name'),
            )
    attributes = relationship('Attribute',
            secondary=meta_to_attr,
            collection_class=attribute_mapped_collection('key'),
            )
    paths = relationship('Path', back_populates='meta')

class Attribute(Base):
    __tablename__ = 'attribute'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(Text)


class Dimension(Base):
    __tablename__ = 'dimension'

    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer, ForeignKey('metadata.id'))
    name = Column(String)
    size = Column(String)

    meta = relationship('Metadata', back_populates='dimensions')


class Variable(Base):
    __tablename__ = 'variable'

    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer, ForeignKey('metadata.id'))
    name = Column(String)
    type = Column(String)

    meta = relationship('Metadata', back_populates='variables')
    attributes = relationship('Attribute',
            secondary=var_to_attr,
            collection_class=attribute_mapped_collection('key'),
            )
    dimensions = relationship('Dimension',
            secondary=var_to_dim,
            order_by='var_to_dim.c.ndim',
            collection_class=OrderingList('var_to_dim.c.ndim'),
            )

