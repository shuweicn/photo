import os
import sqlalchemy
import redis
import hashlib
from sqlalchemy import MetaData, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import path
from config import parse_path, DATABASE, REDIS
from datetime import datetime


os.chdir(parse_path)

r = redis.Redis(**REDIS)

Base = declarative_base()
metadata = MetaData()
engine = sqlalchemy.create_engine(DATABASE)
session = sessionmaker(bind=engine)()


class Photo(Base):
    __tablename__ = 'photo'

    id = Column(Integer, primary_key=True)
    path = Column(String(256), index=True)
    mtime = Column(DateTime)
    ctime = Column(DateTime)
    md5 = Column(String(64), index=True)
    sha256 = Column(String(256))

    def __repr__(self):
        return f'Photo {self.path}'


def hash_file(fp):
    hash_md5 = hashlib.md5()
    hash_sha256 = hashlib.sha256()
    with open(fp, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
            hash_sha256.update(chunk)
    return {
        'md5': hash_md5.hexdigest()[8:24],
        'sha256': hash_sha256.hexdigest()
    }


def files():
    for base, dirs, _files in os.walk(parse_path):
        for f in _files:
            file_path = path.join(base, f)
            main_dir = file_path[len(parse_path):]
            yield main_dir.lstrip('/')


def infos():
    for f in files():
        yield dict(
            path=f,
            mtime=datetime.fromtimestamp(os.path.getmtime(f)),
            ctime=datetime.fromtimestamp(os.path.getctime(f)),
            **hash_file(f)
        )


if __name__ == '__main__':
    Base.metadata.create_all(engine)

    for i in infos():
        now = str(datetime.now())[0:19]

        p = i['path']
        try:
            if r.get(p) is None:
                session.add(Photo(**i))
                session.commit()
                r.set(p, 1)
                print(f'[{now}] register {p}', flush=True)
            else:
                print(f'[{now}] continue {p}', flush=True)
        except Exception as e:
            print(f'[{now} error {p} {e}]')