from sqlalchemy import *
import config


class Genres(config.DB.Model):
    __tablename__ = 'genres'
    __table_args__ = {"schema": "steam"}

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)

