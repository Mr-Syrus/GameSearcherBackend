from typing import List

from sqlalchemy import *
import config


class Games(config.DB.Model):
    __tablename__ = 'games'
    __table_args__ = {"schema": "steam"}

    id = Column(Integer, primary_key=True)

    # main
    type = Column(Text)
    name = Column(Text, nullable=False)
    required_age = Column(Integer, default=0)
    is_free = Column(Boolean, default=False)

    # descriptions
    detailed_description = Column(Text)
    about_the_game = Column(Text)
    short_description = Column(Text)

    # fullgame
    fullgame_appid = Column(Integer)
    fullgame_name = Column(Text)

    # languages
    supported_languages = Column(ARRAY(String(64)))

    # images
    header_image = Column(Text)
    capsule_image = Column(Text)
    capsule_imagev5 = Column(Text)

    bucket_header_image = Column(Text)
    bucket_capsule_image = Column(Text)
    bucket_capsule_imagev5 = Column(Text)

    # website
    website = Column(Text)

    # requirements
    pc_requirements = Column(JSON)
    mac_requirements = Column(JSON)
    linux_requirements = Column(JSON)

    # dev/pub
    developers = Column(ARRAY(String(64)))
    publishers = Column(ARRAY(String(64)))

    # platforms
    platforms_windows = Column(Boolean, default=False)
    platforms_mac = Column(Boolean, default=False)
    platforms_linux = Column(Boolean, default=False)

    # release
    release_date = Column(Date)
    coming_soon = Column(Boolean, default=False)


    # backgrounds
    background = Column(Text)
    background_raw = Column(Text)

    bucket_background = Column(Text)
    bucket_background_raw = Column(Text)

    # ratings
    ratings = Column(JSON)

    # reviews
    total_reviews = Column(Integer)
    total_reviews_positive = Column(Integer)
    total_reviews_negative = Column(Integer)
    reviews_score = Column(Integer)