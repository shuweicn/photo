from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, and_
from model import Base, session


class PhotoStatus:
    not_a_picture = 'not_a_picture'
    zombie_aae = 'zombie_aae'
    duplicate = 'duplicate'
    destination = 'destination'


class Photo(Base):
    __tablename__ = 'photo'

    id = Column(Integer, primary_key=True)

    src = Column(String(200), index=True)
    pre_src = Column(String(200), index=True)
    pre_dst = Column(String(200), index=True)
    dst = Column(String(200), index=True)

    photo_aae_pair = Column(String(200), index=True)  # Photo.src
    aae_final_follow = Column(String(200), index=True)
    photo_duplicate_with = Column(String(200), index=True)  # Photo.src

    mtime = Column(DateTime)
    ctime = Column(DateTime)
    md5 = Column(String(16), index=True)
    sha256 = Column(String(64))
    exif = Column(JSON)
    exif_status = Column(Boolean)
    exif_type = Column(String(10))
    file_suffix = Column(String(200))
    status = Column(String(20))
    is_moved = Column(Boolean)

    def aae_get_photo_pair(self):
        return session.query(Photo).filter_by(photo_aae_pair=self.src).first()


    def __repr__(self):
        return self.src



