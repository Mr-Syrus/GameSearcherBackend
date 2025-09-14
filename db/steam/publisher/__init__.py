from sqlalchemy import *
import config


class Publisher(config.DB.Model):
    __tablename__ = 'publisher'
    __table_args__ = {"schema": "steam"}

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)

