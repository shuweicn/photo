import os
import hashlib
import json

from os import path
from config import EXIFTOOLS
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
from multiprocessing import Pool
from lib.log import log

from model.photo import Photo, session


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
    log.info(f'exif {exif_status} {fp}')


def write_all_photo_to_db():
    for fp in files():
        if session.query(Photo).filter_by(src=fp).first():
            log.info(f'write_all_photo_to_db continue {fp}')
        else:
            exif = file_exif(fp)

            if '.' not in path.basename(fp) or (
                    fp.count('.') == 1 and fp.startswith('.')):
                file_suffix = '_none'
            else:
                file_suffix = fp.split('.')[-1].strip(),

            data = dict(
                src=fp,
                mtime=datetime.fromtimestamp(os.path.getmtime(fp)),
                ctime=datetime.fromtimestamp(os.path.getctime(fp)),
                exif_type=exif['exif'].get('FileType', '_none').strip(),
                file_suffix=file_suffix,
                **file_hash(fp),
                **file_exif(fp),
            )
            exif_status = bool(data['exif_status'])
            session.add(Photo(**data))
            session.commit()
            log.info(f'write_all_photo_to_db {exif_status} {fp}')

