from config import DELETE_EXE
from lib.photos import db_photos
from model.photo import PhotoStatus

exists_data = {}
c = 1
for p in db_photos(print_offset=True):
    c += 1
    exists_data[p.md5] = p.sha256

print(f'dst {c}')


script = """
import os
import hashlib
import argparse
from os import path
from logging import getLogger, StreamHandler, Formatter, DEBUG, FileHandler


parser = argparse.ArgumentParser(description='delete duplicates photo')
parser.add_argument('--delete', default=False, action='store_true')
parser.add_argument('--dir', dest='delete_dir', type=str)
args = parser.parse_args()


log = getLogger('delete')
log.setLevel(level=DEBUG)
log_format = Formatter('[%(asctime)s] %(message)s')

a = args.delete_dir
filename = './delete_' + a.lstrip('./').strip('/').replace('/', '_') + '.log'

file = FileHandler(filename=filename)
file.setFormatter(log_format)
log.addHandler(file)

stream = StreamHandler()
stream.setFormatter(log_format)
log.addHandler(stream)


def files(delete_dir):
    for base, dirs, _files in os.walk(delete_dir):
        for f in _files:
            yield path.join(base, f)


def file_hash(fp):
    hash_md5 = hashlib.md5()
    hash_sha256 = hashlib.sha256()
    with open(fp, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
            hash_sha256.update(chunk)

    return hash_md5.hexdigest()[8:24], hash_sha256.hexdigest()


def process_delete(delete, delete_dir):
    for fp in files(delete_dir):
        md5, sha256 = file_hash(fp)
        if exists_data.get(md5) == sha256:
            
            if delete:
                log.info('match complete delete {0} {1}'.format(md5, fp))
                os.remove(fp)
            else:
                log.info('match complete test {0} {1}'.format(md5, fp))
        else:
            log.error('match failed jump {0} {1}'.format(md5,fp))


if __name__ == '__main__':
    process_delete(delete=args.delete, delete_dir=args.delete_dir)
    
"""

if __name__ == '__main__':
    with open(DELETE_EXE, 'w') as f:
        f.write(f'exists_data = {exists_data}')
        f.write(script)

    print(f'python3 {DELETE_EXE} -h')









