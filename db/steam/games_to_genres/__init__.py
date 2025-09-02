from sqlalchemy import *
import config


class GamesToGenres(config.DB.Model):
    __tablename__ = 'games_to_genres'
    __table_args__ = {"schema": "steam"}

    id_games = Column(Integer, primary_key=True)
    id_genres = Column(Integer, primary_key=True)

