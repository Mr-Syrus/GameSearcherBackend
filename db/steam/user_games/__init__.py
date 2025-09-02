from sqlalchemy import *
import config


class UserGames(config.DB.Model):
    __tablename__ = 'user_games'
    __table_args__ = {"schema": "steam"}

    id = Column(BigInteger, primary_key=True)
    id_games = Column(Integer, primary_key=True)

    playtime_hours = Column(BigInteger, nullable=False)
    rtime_last_played = Column(BigInteger, nullable=False)

