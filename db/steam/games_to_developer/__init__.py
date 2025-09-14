from sqlalchemy import *
import config


class GamesToDeveloper(config.DB.Model):
    __tablename__ = 'games_to_developer'
    __table_args__ = {"schema": "steam"}

    id_games = Column(Integer, primary_key=True)
    id_developer = Column(Integer, primary_key=True)

