from sqlalchemy import *
import config


class Categories(config.DB.Model):
    __tablename__ = 'categories'
    __table_args__ = {"schema": "steam"}

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)

