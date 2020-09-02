import os
from model.photo import PhotoStatus
from sqlalchemy import and_
from config import PHOTO_PATH
from lib.photos import db_photos
from lib.log import log
from lib.correct import (
    set_pre_src, set_photo_aae_pair, parse_duplicate_photo_status,
    parse_pre_dst_status, parse_dst
)
from lib.exif import write_all_photo_to_db
from sqlalchemy import func
from model import session, Photo
from pprint import pprint


def parse_aae_pair1(p):
    if p.exif_type == 'AAE':
        like = p.src[:-4] + '.%'
        q = and_(Photo.src.like(like), Photo.id != p.id)

        res = session.query(Photo).filter(q).all()
        if len(res) == 0:
            log.info('parse_aae_pair1 ' + p.src)
            return 1
    return 0


def parse_aae_pair2(p):
    if p.exif_type == 'AAE':
        like = p.pre_src[:-4] + '.%'
        q = and_(Photo.pre_src.like(like), Photo.id != p.id)

        res = session.query(Photo).filter(q).all()
        if len(res) == 0:
            log.info('parse_aae_pair2 ' + p.src)
            return 1
    return 0


def parse_aae_pair3(p):
    if p.exif_type == 'AAE':
        if not session.query(Photo).filter_by(photo_aae_pair=p.src).first():
            log.info('parse_aae_pair3 ' + p.src)
            return 1
    return 0


if __name__ == '__main__':
    os.chdir(PHOTO_PATH)
    p1 = 0
    p2 = 0
    p3 = 0
    for p in db_photos():
        p1 += parse_aae_pair1(p)
        p2 += parse_aae_pair2(p)
        p3 += parse_aae_pair3(p)

    print(p1, p2, p3)
