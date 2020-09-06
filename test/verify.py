import os
from sqlalchemy import and_
from config import PHOTO_PATH
from lib.photos import db_photos
from lib.log import log
from sqlalchemy import func
from model import session, Photo
from pprint import pprint


class PhotoStatus:
    not_a_picture = 'not_a_picture'
    zombie_aae = 'zombie_aae'
    duplicate = 'duplicate'
    destination = 'destination'


qf = session.query(Photo)


# verify zombie_aae number
def verify_zombie_aae_method():
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

    p1 = 0
    p2 = 0
    p3 = 0
    for p in db_photos(print_offset=True):
        p1 += parse_aae_pair1(p)
        p2 += parse_aae_pair2(p)
        p3 += parse_aae_pair3(p)

    print(p1, p2, p3)
    print('aae number ', (p1 == p2) == (p2 == p3))


def verify_number():
    al = qf.count()
    print(f'all number is {al}')
    not_a_picture = qf.filter_by(status='not_a_picture').count()
    print(f'not_a_picture {not_a_picture}')

    zombie_aae = qf.filter_by(status='zombie_aae').count()
    print(f'zombie_aae {zombie_aae}')

    duplicate = qf.filter_by(status='duplicate').count()
    print(f'duplicate {duplicate}')

    destination = qf.filter_by(status='destination').count()
    print(f'destination {destination}')
    print('verify: ', not_a_picture+zombie_aae+duplicate+destination == al)


def verify_not_a_picture():
    for p in qf.filter_by(status='not_a_picture'):
        print(p, p.dst)


def verify_duplicate():
    for p in qf.filter_by(status='duplicate'):
        for dup in qf.filter_by(md5=p.md5).all():
            if dup.status == 'destination':
                break
        else:
            print('error dups ', p.src, p.dst,  p.md5, p.status)



if __name__ == '__main__':
    os.chdir(PHOTO_PATH)
    # verify_zombie_aae_method()
    # verify_number()
    # verify_not_a_picture()
    verify_duplicate()

