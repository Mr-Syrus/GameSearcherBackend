from sqlalchemy import *
import config


class UserGames(config.DB.Model):
    __tablename__ = 'user_games'

    id_games = Column(Integer, primary_key=True)
    id_games_likes = Column(Integer, primary_key=True)

    points = Column(Integer, nullable=False)
