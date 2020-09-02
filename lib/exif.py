import os
import redis
import hashlib
import json

from os import path
from config import PHOTO_PATH, REDIS, EXIFTOOLS
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
from traceback import format_exc
from multiprocessing import Pool
from lib.log import logging

from model.photo import Photo, session


os.chdir(PHOTO_PATH)

rds = redis.Redis(**REDIS)


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
                    'exif': exif[0],
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


def process_a_photo(fp):
    try:
        if rds.hget(fp, 'src') is None:
            mtime = os.path.getmtime(fp)
            ctime = os.path.getctime(fp)

            db_arg = dict(path=fp, **file_hash(fp), **file_exif(fp))

            session.add(
                Photo(
                    mtime=datetime.fromtimestamp(mtime),
                    ctime=datetime.fromtimestamp(ctime)
                      **db_arg
                )
            )
            session.commit()

            exif_status = bool(db_arg['exif_status'])
            rds.hmset(fp, dict(mtime=mtime, ctime=ctime, **db_arg))

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
    process_all_photo()

