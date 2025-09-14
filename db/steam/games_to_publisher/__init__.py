from sqlalchemy import *
import config


class GamesToPublisher(config.DB.Model):
    __tablename__ = 'games_to_publisher'
    __table_args__ = {"schema": "steam"}

    id_games = Column(Integer, primary_key=True)
    id_publisher = Column(Integer, primary_key=True)

