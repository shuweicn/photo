from logging import getLogger, StreamHandler, Formatter, DEBUG, FileHandler
from config import LOG_FILE

log = getLogger('photo')
log.setLevel(level=DEBUG)

log_format = Formatter('[%(asctime)s] %(message)s')

stream = StreamHandler()
stream.setFormatter(log_format)
log.addHandler(stream)

file = FileHandler(filename=LOG_FILE)
file.setFormatter(log_format)
log.addHandler(file)



if __name__ == '__main__':
    log.info('test')