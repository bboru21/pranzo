# -*- coding: UTF-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from simple_settings import settings


Base = declarative_base()

class Vendor(Base):

    __tablename__ = 'vendor'
    id = Column(Integer, primary_key=True)
    site_permit = Column(String, unique=True)
    name = Column(String)
    alias = Column(String)

engine = create_engine(settings.DATABASES['ENGINE'], echo=False)
Base.metadata.create_all(engine)