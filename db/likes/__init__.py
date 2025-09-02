from sqlalchemy import *
import config


class Likes(config.DB.Model):
    __tablename__ = 'likes'

    user_id = Column(Integer, primary_key=True)
    game_id = Column(Integer, primary_key=True)