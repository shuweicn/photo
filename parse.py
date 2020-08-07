import os
import sqlalchemy
import redis
import hashlib
import json
import logging
from sqlalchemy import MetaData, Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import path
from config import PHOTO_PATH, DATABASE, REDIS, EXIFTOOLS, LOG
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
from traceback import format_exc
from multiprocessing import Pool, RLock

logging.basicConfig(
    filename=LOG,
    level=logging.DEBUG,
    format='[%(asctime)s] %(message)s'

)
os.chdir(PHOTO_PATH)

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


def files():
    for base, dirs, _files in os.walk('./'):
        for f in _files:
            yield path.join(base, f)


def file_hash(fp):
    hash_md5 = hashlib.md5()
    hash_sha256 = hashlib.sha256()
    with open(fp, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
            hash_sha256.update(chunk)

    return {
        'md5': hash_md5.hexdigest()[8:24],
        'sha256': hash_sha256.hexdigest(),
    }


def file_exif(fp):
    cmd = f'{EXIFTOOLS} -json "{fp}"'

    with Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True) as c:
        out, err = c.communicate()
        try:

            exif = json.loads(out)
            if isinstance(exif, list) and len(exif) == 1:
                return {
                    'exif': exif,
                    'exif_status': True
                }
            else:
                return {
                    'exif': exif,
                    'exif_status': False
                }

        except json.decoder.JSONDecodeError:

            if out and not err:
                msg = out.decode().strip()
            elif not out and err:
                msg = err.decode().strip()
            elif out and err:
                msg = out.decode().strip() + '|' + err.decode().strip()
            else:
                msg = ''
            return {
                'exif': {'Error': msg},
                'exif_status': False
            }


def parse_multi(path, md5, sha256, *args, **kwargs):
    num = r.get(md5)
    if not num:
        r.set(md5, 1)
    else:
        r.incr(md5, 1)
        session.add(PhotoMulti(path=path, md5=md5, sha256=sha256))
        session.commit()


def process_a_photo(fp):
    try:
        if r.get(fp) is None:
            db_arg = dict(
                path=fp,
                mtime=datetime.fromtimestamp(os.path.getmtime(fp)),
                ctime=datetime.fromtimestamp(os.path.getctime(fp)),
                **file_hash(fp),
                **file_exif(fp),
            )

            session.add(Photo(**db_arg))
            session.commit()

            parse_multi(**db_arg)

            exif_status = bool(db_arg['exif_status'])
            r.set(fp, 1)
            logging.info(f'register {exif_status} {fp}')
        else:
            logging.info(f'continue None {fp}')
    except Exception as e:
        logging.error(f'error {fp} {e} \n {format_exc()}')


def process_all_photo():
    import time
    s = time.time()
    pool = Pool(5)
    pool.map(process_a_photo, files())
    print(time.time() - s)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    process_all_photo()

