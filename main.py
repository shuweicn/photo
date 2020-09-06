import os
from config import PHOTO_PATH
from lib.correct import (
    set_pre_src, set_photo_aae_pair, parse_duplicate_photo_status,
    parse_pre_dst_status, parse_dst
)
from lib.move import moves


if __name__ == '__main__':
    # update photo set pre_src = null, pre_dst = null, photo_aae_pair=null, photo_duplicate_with = null, status=null;
    os.chdir(PHOTO_PATH)
    ## write_all_photo_to_db()
    # set_pre_src()
    # set_photo_aae_pair()
    # parse_duplicate_photo_status()
    # parse_pre_dst_status()
    # parse_dst()
    moves()












