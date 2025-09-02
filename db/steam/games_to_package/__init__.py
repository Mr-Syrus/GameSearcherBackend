from sqlalchemy import *
import config


class GamesToPackage(config.DB.Model):
    __tablename__ = 'games_to_package'
    __table_args__ = {"schema": "steam"}

    id_games = Column(Integer, primary_key=True)
    id_package = Column(Integer, primary_key=True)

