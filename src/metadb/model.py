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
from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy import ForeignKey, Table, UniqueConstraint, text
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.orderinglist import OrderingList
import os
import time

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
path_to_collection = Table('path_to_collection', Base.metadata,
                           Column('path_id', Integer, ForeignKey('path.id')),
                           Column('coll_id', Integer,
                                  ForeignKey('collection.id')),
                           )


class Collection(Base):
    """
    A collection of files

    A single file can be part of multiple collections

    """
    __tablename__ = 'collection'

    id = Column(Integer, primary_key=True)

    #: Collection name
    name = Column(String, unique=True)

    #: :py:class:`Path` s in this collection
    paths = relationship('Path', secondary=path_to_collection,
                         back_populates='collections')


class Path(Base):
    """
    Filesystem path

    The same path can point to the same file contents (e.g. from symlinks)
    """
    __tablename__ = 'path'

    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer, ForeignKey('metadata.id'))

    #: str Filesystem path
    path = Column(Text, unique=True)

    #: int os.stat() mtime
    mtime = Column(Integer)
    #: int os.stat() uid
    uid = Column(Integer)
    #: int os.stat() gid
    gid = Column(Integer)
    #: int os.stat() size
    size = Column(Integer)
    #: Unix time when the path was last seen
    last_seen = Column(Float)

    #: :py:class:`Metadata` of the path's content
    meta = relationship('Metadata', back_populates='paths')
    #: :py:class:`Collection` s that the path is part of
    collections = relationship('Collection', secondary=path_to_collection,
                               collection_class=set,
                               back_populates='paths')

    @property
    def basename(self):
        """
        The basename of the path
        """
        return os.path.basename(self.path)

    def update_stat(self, stat):
        """
        Update the path's stat data

        :param stat: Stat values to use in the update
        """
        import stat as st

        if self.meta is not None and self.mtime < stat[st.ST_MTIME]:
            # Metadata might have changed
            self.meta = None

        self.mtime = stat[st.ST_MTIME]
        self.uid = stat[st.ST_UID]
        self.gid = stat[st.ST_GID]
        self.size = stat[st.ST_SIZE]
        self.last_seen = time.time()


class Metadata(Base):
    """
    Metadata sourced from a file
    """
    __tablename__ = 'metadata'

    id = Column(Integer, primary_key=True)
    #: sha256 checksum
    sha256 = Column(String, unique=True)
    mtime = Column(Integer)
    size = Column(Integer)

    #: :py:class:`Dimension` s in the file (dict)
    dimensions = relationship('Dimension',
                              back_populates='meta',
                              collection_class=attribute_mapped_collection(
                                  'name'),
                              )
    #: :py:class:`Variable` s in the file (dict)
    variables = relationship('Variable',
                             back_populates='meta',
                             collection_class=attribute_mapped_collection(
                                 'name'),
                             )
    #: :py:class:`Attribute` s of the file (dict)
    attributes = relationship('Attribute',
                              secondary=meta_to_attr,
                              collection_class=attribute_mapped_collection(
                                  'key'),
                              )
    #: :py:class:`Path` s to the file
    paths = relationship('Path', back_populates='meta')

    @property
    def size_str(self):
        from math import log, floor
        r = int(floor(log(self.size, 1000)))
        prefix = ['', 'k', 'm', 'G', 'T']
        return "%.1f %sb" % (self.size / 1000**r, prefix[r])


class Attribute(Base):
    """
    A generic attribute

    Can be attached to either :py:class:`Metadata` or :py:class:`Variable`

    Read-only (attributes in the database are de-duplicated)
    """
    __tablename__ = 'attribute'

    id = Column(Integer, primary_key=True)
    #: Attribute name
    key = Column(String)
    #: Attribute value
    value = Column(Text)

    __table_args__ = (
        UniqueConstraint('key', 'value'),
    )


class Dimension(Base):
    """
    A dimension in a file (c.f. netCDF)
    """
    __tablename__ = 'dimension'

    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer, ForeignKey('metadata.id'))

    #: Dimension name
    name = Column(String)
    #: Dimension size
    size = Column(Integer)

    #: :py:class:`Metadata` this is part of
    meta = relationship('Metadata', back_populates='dimensions')


class Variable(Base):
    """
    A variable in a file (c.f. netCDF)
    """
    __tablename__ = 'variable'

    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer, ForeignKey('metadata.id'))

    #: Variable name
    name = Column(String)
    #: Variable type
    type = Column(String)

    #: :py:class:`Metadata` this is part of
    meta = relationship('Metadata', back_populates='variables')
    #: :py:class:`Attribute` s of this variable (dict)
    attributes = relationship('Attribute',
                              secondary=var_to_attr,
                              collection_class=attribute_mapped_collection(
                                  'key'),
                              )
    #: :py:class:`Dimension` s of this variable
    dimensions = relationship('Dimension',
                              secondary=var_to_dim,
                              order_by='var_to_dim.c.ndim',
                              collection_class=OrderingList(
                                  'var_to_dim.c.ndim'),
                              )
