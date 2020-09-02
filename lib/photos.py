from model import session, Photo
from lib.log import log
from sqlalchemy import and_
import time


def db_photos(commit=False, print_offset=False):
    start = time.time()
    size = 1000
    last_count = size
    offset = 0

    if print_offset:
        log.info(f'process {offset}')

    while last_count == size:
        q = and_(Photo.id > offset, Photo.id <= offset + size)
        query = session.query(Photo).filter(q)

        photos = query.all()

        for p in photos:
            yield p

        last_count = len(photos)
        offset += size
        if commit:
            session.commit()

        if print_offset:
            lt = time.time() - start
            log.info(f'process {offset} {lt}')
            start = time.time()


if __name__ == '__main__':
    c = 0
    ids = 0
    for p in db_photos(print_offset=True):
        c += 1
        ids += p.id
    print(c, ids)