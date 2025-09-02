from sqlalchemy import *
import config


class GamesToCategories(config.DB.Model):
    __tablename__ = 'games_to_categories'
    __table_args__ = {"schema": "steam"}

    id_games = Column(Integer, primary_key=True)
    id_categories = Column(Integer, primary_key=True)

