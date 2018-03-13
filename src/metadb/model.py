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

from sqlalchemy.orm import declarative_base

Base = declarative_base()

def Metadata(Base):
    __tablename__ = 'metadata'

    id = Column(Integer, primary_key=True)

def Attribute(Base):
    __tablename__ = 'attribute'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(Text)

def Dimension(Base):
    __tablename__ = 'dimension'

    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer)
    name = Column(String)
    size = Column(String)

def Variable(Base):
    __tablename__ = 'variable'

    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer)
    name = Column(String)
    type = Column(String)
