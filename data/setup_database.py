# -*- coding: UTF-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Vendors(Base):

    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    site_permit = Column(String, unique=True)
    name = Column(String)
    alias = Column(String)

engine = create_engine('sqlite:///data/db/pranzodb.db', echo=True)
Base.metadata.create_all(engine)