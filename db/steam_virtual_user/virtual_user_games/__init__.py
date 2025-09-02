from sqlalchemy import *
import config


class VirtualUserGames(config.DB.Model):
    __tablename__ = 'virtual_user_games'

    id_games = Column(Integer, primary_key=True)
    id_games_likes = Column(Integer, primary_key=True)

    points = Column(Float(), nullable=False)
