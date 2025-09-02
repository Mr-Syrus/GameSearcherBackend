from sqlalchemy import *
import config


class LikesGames(config.DB.Model):
    __tablename__ = 'likes_games'

    user_id = Column(Integer, primary_key=True)
    game_id = Column(Integer, primary_key=True)
