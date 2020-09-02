import re
from datetime import datetime
from os import path
from model.photo import session, Photo


def model(p):
    model = p.exif.get('Model', 'Other')
    if '/Studio/meipai_' in p.src:
        return 'meipai'

    if '/video/meipai_' in p.src:
        return 'meipai'

    elif '/Camera/meipai_' in p.src:
        return 'meipai'

    elif '/.thumbnails/' in p.src or '/thumbnails/' in p.src:
        return 'thumbnails'

    elif '/miaopai/' in p.src:
        return 'miaopai'

    elif '/美图/' in p.src:
        return 'meitu'

    elif '/Screenshot_' in p.src:
        return 'Screenshots'

    elif '/YouCam Makeup/' in p.src:
        return 'YouCam_Makeup'

    elif '/2013-2015/Studio/' in p.src:
        return 'Studio'

    elif model == '':
        return 'None'

    elif model == 'Other':
        device = p.exif.get('DeviceManufacturer')
        if device:
            model = device

    return model


date1 = r'20[0-2][0-9]:[0-1][0-9]:[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'
date2 = r'20[0-2][0-9][0-1][0-9][0-3][0-9]_[0-2][0-9][0-5][0-9][0-5][0-9]'
date3 = r'20[0-2][0-9][0-1][0-9][0-3][0-9][0-2][0-9][0-5][0-9][0-5][0-9]'


def exif_create_date(p):
    # parse create date
    cd_str = p.exif.get('CreateDate')
    if cd_str and ('上午' in cd_str or '下午' in cd_str):
        cd_str = cd_str.replace('上午', 'AM').replace('下午', 'PM')

    if cd_str == None:
        return None

    if cd_str == '0000:00:00 00:00:00' or cd_str in ['1970:01:03 02:47:23']:
        return p.mtime

    if re.match('^'+date1+'$', cd_str):
        # 2019-10-21 14:11:47
        return datetime.strptime(cd_str, '%Y:%m:%d %H:%M:%S')

    if re.match('^'+date1+'\+\d{2}:\d{2}$', cd_str):
        # 2012:03:13 13:10:50+08:00
        return datetime.strptime(cd_str, '%Y:%m:%d %H:%M:%S%z')

    if re.match('^'+date1+'PM$|^'+date1+'AM$', cd_str):
        # 2017:06:27 14:00:52AM
        return datetime.strptime(cd_str, '%Y:%m:%d %H:%M:%S%p')

    if (len(cd_str) == 19 and cd_str.count(':') == 4 and cd_str[10] == ' ' and
        re.match('^20[0-2][0-9]:', cd_str)):
        # 2015: 8:26  6:43: 5
        return datetime.strptime(cd_str.replace(' ', '0'), '%Y:%m:%d0%H:%M:%S')

    print(p, f'"{cd_str}"', p.ctime, p.mtime)
    raise ValueError('break')


def _file_name_date(data_str):
    res = [
        # 2019-10-21 14:11:47
        (
            r'20[0-2][0-9]:[0-1][0-9]:[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]',
            '%Y:%m:%d %H:%M:%S',
        ),
        # 20191021_141147
        (
            r'20[0-2][0-9][0-1][0-9][0-3][0-9]_[0-2][0-9][0-5][0-9][0-5][0-9]',
            '%Y%m%d_%H%M%S',
        ),
        # 20160520102919
        (
            r'20[0-2][0-9][0-1][0-9][0-3][0-9][0-2][0-9][0-5][0-9][0-5][0-9]',
            '%Y%m%d%H%M%S',
        ),
        # 2015-07-25-18-29-20
        (
            r'20[0-2][0-9]-[0-1][0-9]-[0-3][0-9]-[0-2][0-9]-[0-5][0-9]-[0-5][0-9]',
            '%Y-%m-%d-%H-%M-%S',
        ),
        # 2014_01_02_17_14_47
        (
            r'20[0-2][0-9]_[0-1][0-9]_[0-3][0-9]_[0-2][0-9]_[0-5][0-9]_[0-5][0-9]',
            '%Y_%m_%d_%H_%M_%S',
        ),
        # 2014-07-15-152631
        (
            r'20[0-2][0-9]-[0-1][0-9]-[0-3][0-9]-[0-2][0-9][0-5][0-9][0-5][0-9]',
            '%Y-%m-%d-%H%M%S',
        ),
        # 2015-02-06 16.41.25
        (
            r'20[0-2][0-9]-[0-1][0-9]-[0-3][0-9] [0-2][0-9].[0-5][0-9].[0-5][0-9]',
            '%Y-%m-%d %H.%M.%S',
        ),
        # 2013-10-06_09-33-06
        (
            r'20[0-2][0-9]-[0-1][0-9]-[0-3][0-9]_[0-2][0-9]-[0-5][0-9]-[0-5][0-9]',
            '%Y-%m-%d_%H-%M-%S',
        ),

    ]
    for m, t in res:
        r = re.search(m, data_str)
        if r:
            return datetime.strptime(data_str[r.start():r.end()], t)


def file_name_date(p):
    # parse date from name
    base_name = path.basename(p.src)
    name_date = _file_name_date(base_name)
    if name_date:
        return name_date
    elif re.search('^1[2-6]\d{11}\D|\D(1[2-6]\d{11}\D)', base_name):
        r = re.search('1[2-6]\d{8}', base_name)
        stamp_time = datetime.fromtimestamp(int(base_name[r.start():r.end()]))
        return stamp_time


def path_with_date(p, exist=0):
    _model, exc_cd, fn_cd = model(p), exif_create_date(p), file_name_date(p)
    name = path.basename(p.src)
    suf = '.' + name.split('.')[-1]
    if exist > 0:
        if len(name.rsplit('.', 1)) == 1:
            _nam, _suf = name, name
        else:
            _nam, _suf = name.rsplit('.', 1)
        name = f'{_nam}_{exist}.{_suf}'
        suf = f'_{exist}.' + name.split('.')[-1]

    date = fn_cd or p.mtime or exc_cd
    _f = '%Y%m%d_%H%M%S'
    # parse watch use date
    if '/20160709/64G_RECOVER1/' in p.src or '/20160709/64G_RECOVER2/' in p.src:
        date = fn_cd or p.mtime
        final_name = date.strftime(_f) + suf

    elif 'iPhone' in _model or 'iPad' in _model:
        final_name = date.strftime(_f) + '_' + name

    elif len(name) < 20 and any(['\u4e00' <= x <= '\u9fff' for x in name]):
        final_name = date.strftime(_f) + '_' + name

    else:
        final_name = date.strftime(_f) + suf

    return path.join(date.strftime('%Y-%m'), _model, final_name)

