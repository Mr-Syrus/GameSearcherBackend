from sqlalchemy import *
import config


class Screenshots(config.DB.Model):
    __tablename__ = 'screenshots'
    __table_args__ = {"schema": "steam"}

    id_games = Column(Integer, primary_key=True)
    id = Column(Integer, primary_key=True)
    path_thumbnail = Column(Text, nullable=False)
    path_full = Column(Text, nullable=False)

