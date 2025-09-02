from sqlalchemy import *
import config


class Session(config.DB.Model):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    key = Column(String(64), unique=True, nullable=False)

