import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from config import DB_URI

Base = declarative_base()
metadata = MetaData()

engine = sqlalchemy.create_engine(DB_URI, poolclass=NullPool)
session = sessionmaker(bind=engine)()


Base = declarative_base()
metadata = MetaData()

engine = sqlalchemy.create_engine(DB_URI, poolclass=NullPool)
session = sessionmaker(bind=engine)()

from model.photo import Photo