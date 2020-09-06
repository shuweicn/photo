import os
import shutil
from os import path
from lib.log import log
from config import MOVED_DIR
from lib.photos import db_photos


def moves():
    for p in db_photos(commit=True):
        dst = path.join(MOVED_DIR, p.dst)
        base = path.dirname(dst)
        if not os.path.exists(base):
            os.makedirs(base)

        try:
            if os.path.exists(p.src) and not os.path.exists(dst):
                shutil.move(p.src, dst)
                p.is_moved = True
                log.info(f'moved success {p.src} {dst}')
            else:
                log.info(f'moved failed {p.src} {dst}')
        except FileNotFoundError:
            log.info(f'moved jump {p.src} {dst}')