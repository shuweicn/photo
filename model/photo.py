import sqlalchemy
from sqlalchemy import MetaData, Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from config import DB_URI

Base = declarative_base()
metadata = MetaData()

engine = sqlalchemy.create_engine(DB_URI, poolclass=NullPool)
session = sessionmaker(bind=engine)()


class Photo(Base):
    __tablename__ = 'photo'

    id = Column(Integer, primary_key=True)
    path = Column(String(256), index=True)
    mtime = Column(DateTime)
    ctime = Column(DateTime)
    md5 = Column(String(64), index=True)
    sha256 = Column(String(256))
    exif = Column(JSON)
    exif_status = Column(Boolean)

    def __repr__(self):
        return f'Photo {self.path}'


class PhotoMulti(Base):
    __tablename__ = 'photo_multi'
    id = Column(Integer, primary_key=True)
    path = Column(String(256))
    md5 = Column(String(64))
    sha256 = Column(String(256))

    def __repr__(self):
        return f'Photo {self.path}'