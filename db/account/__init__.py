from sqlalchemy import *
import config


class Account(config.DB.Model):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True)
    login = Column(Text, nullable=False, unique=True)
    pasword = Column(Text, nullable=False)
