#!/usr/bin/env python
"""
Copyright 2018 Scott Wales

author: Scott Wales <scottwales@outlook.com.au>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import print_function
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()

def connect(url, debug=False, init=False):
    """
    Returns a sqlalchemy.Connection
    """
    engine = create_engine(url, echo=debug)

    if init:
        from archive.model import Base
        Base.metadata.create_all(engine)

    Session.configure(bind=engine)

    return engine.connect()
