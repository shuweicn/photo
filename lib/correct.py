from lib.log import log
def unify(k):
    if k == 'jpeg':
        return 'jpg'
    return k


def exif_type(p):
    return unify(p.exif.get('FileType', '_none').strip())


def file_suffix(p):
    return unify(p.src.split('.')[-1].strip())


def correct_aae_jpg(p):
    _type, _suffix = exif_type(p), file_suffix(p)
    l_type = _type.lower()
    l_suffix = _suffix.lower()

    if (l_type != l_suffix) and (l_type == 'aae' or l_suffix == 'aae'):
        if l_type == 'aae':
            p.correct = p.src[:-len(_suffix)] + _type
        else: # if l_suffix == 'aae':
            p.correct = p.src[:-3] + _type

        log.info(f'correct {_type} {p.src} {p.correct}')
    else:
        p.correct = p.src

    return p.correct





