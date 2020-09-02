from lib.log import log
from lib.path_date import path_with_date
from sqlalchemy import and_, func
from model import session
from lib.photos import db_photos
from model.photo import Photo, PhotoStatus  # AaePair, Duplicate
from os import path


def set_pre_src():
    """set_correct_aae_jpg_reverse"""
    for p in db_photos(commit=True):
        _type, _suffix = p.exif_type, p.file_suffix
        l_type = _type.lower()
        l_suffix = _suffix.lower()

        if (l_type != l_suffix) and (l_type == 'aae' or l_suffix == 'aae'):
            if l_type == 'aae':
                pre_src = p.src[:-len(_suffix)] + _type
            else: # if l_suffix == 'aae':
                pre_src = p.src[:-3] + _type

            p.pre_src = pre_src
            log.info(f'set_pre_src correct {_type} {p.src} {p.pre_src}')
        else:
            p.pre_src = p.src
            log.info(f'set_pre_src direct {_type} {p.src} {p.pre_src}')


def set_photo_aae_pair():
    for p in db_photos(commit=True):
        if p.exif_type == 'AAE':
            continue
        aae_src = p.src[:p.src.rfind('.')] + '.AAE'
        if path.exists(aae_src):
            p.photo_aae_pair = aae_src
            log.info(f'set_photo_aae_pair {p.exif_type} {p.src} {aae_src}')


def parse_duplicate_photo_status():
    c = 0
    res = session.query(
        Photo.md5
    ).group_by(
        Photo.md5
    ).having(
        func.count(Photo.md5) > 1
    ).all()

    for d in res:
        c += 1
        ps = session.query(Photo).filter_by(md5=d[0]).all()
        target = ps[0]
        if target.exif_type != 'AAE':
            # 检测图片是否有 AAE 对,  如果有设置第一个检测到AAE的为正常, 其他为重复
            # 如果没有检测到 AAE 对, 设置第一个图片为正常, 其他为重复

            for p in ps:
                if p.photo_aae_pair:
                    target = p
                    break

            for p in ps:
                if p.id != target.id:
                    p.status = PhotoStatus.duplicate
                    p.photo_duplicate_with = target.src
                    log.info(f'duplicate {p.md5} {p.src}')
                else:
                    log.info(f'save_jump {p.md5} {p.src}')

            if c % 1000 == 0:
                session.commit()
        session.commit()


def __parse_pre_dst_status(p):
    # 非图片的单独放在 not_a_picture 文件夹
    if p.exif_type in ['gzip', 'json', 'lnk', 'txt', 'webp', '_none']:
        p.status = PhotoStatus.not_a_picture
        p.pre_dst = path.join(p.status, p.src.replace('/', '_'))

    # 上面只分析了重复的图片把重复的图片 放在 duplicate 文件夹
    elif p.status == PhotoStatus.duplicate:
        p.status = PhotoStatus.duplicate
        p.pre_dst = path.join(p.status, path_with_date(p))

    # 分析剩下的数据
    else:
        # 分析 AAE 图片
        if p.exif_type == 'AAE':
            photo_pair = p.aae_get_photo_pair()

            # zombie aae
            if not photo_pair:
                p.status = PhotoStatus.zombie_aae
                p.pre_dst = path.join(p.status, p.pre_src.lstrip('./'))

            else:
                # aae have pair can follow pair photo
                if photo_pair.status == PhotoStatus.duplicate:
                    p.status = PhotoStatus.duplicate
                else:
                    p.status = PhotoStatus.destination

                # d = p.pre_dst = path.join(p.status, path_with_date(photo_pair))
                # p.pre_dst = d[:d.rfind('.')] + '.AAE'

        # 分析剩下的图片
        else:
            p.status = PhotoStatus.destination
            p.pre_dst = path.join(p.status, path_with_date(p))

    log.info(f'pre_dst {p.status} {p.src} {p.pre_dst}')


def parse_pre_dst_status():
    for p in db_photos(commit=True):
        __parse_pre_dst_status(p)


def name_duplicate_push(name, num):
    if num == 0:
        return name
    i = name.rfind('.')
    return name[:i] + '_' + str(num) + name[i:]


def parse_dst():
    c = 0
    dups = session.query(
        Photo.pre_dst
    ).filter(
        Photo.exif_type != 'AAE'
    ).group_by(
        Photo.pre_dst
    ).having(
        func.count(Photo.pre_dst) > 1
    )

    for p in dups:
        rests = session.query(Photo).filter(Photo.pre_dst==p[0]).all()
        rests.sort(key=lambda x: x.src.replace('(', '_'))
        for d in rests:
            c += 1
            d.dst = name_duplicate_push(d.pre_dst, c)
            log.info(f'dup {c} set_dst {d.src} {d.dst}')

            if c % 1000 == 0:
                session.commit()

    ones = session.query(
        Photo.pre_dst
    ).filter(
        Photo.exif_type != 'AAE'
    ).group_by(
        Photo.pre_dst
    ).having(
        func.count(Photo.pre_dst) == 1
    )

    for p in session.query(Photo).filter(Photo.pre_dst.in_(ones)):
        c += 1
        p.dst = p.pre_dst
        log.info(f'one {c} set_dst {p.src} {p.pre_dst}')

        if c % 1000 == 0:
            session.commit()

    aaes = session.query(
        Photo
    ).filter(
        Photo.exif_type == 'AAE'
    )
    for p in aaes:
        c += 1
        pair = p.aae_get_photo_pair()
        if pair:
            # pair of aae not have pre_dst
            p.dst = pair.dst[:pair.dst.rfind('.')] + '.AAE'
            p.aae_final_follow = pair.src
        else:
            # zombie aae have pre_dst
            p.dst = p.pre_dst
        log.info(f'aae {c} set_dst {p.src} {p.dst}')
        if c % 1000 == 0:
            session.commit()
    session.commit()
    log.info(c)


if __name__ == '__main__':
    pass


