from sqlalchemy import *
import config


class Developer(config.DB.Model):
    __tablename__ = 'developer'
    __table_args__ = {"schema": "steam"}

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)

