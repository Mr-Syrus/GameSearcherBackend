from sqlalchemy import *
from sqlalchemy.orm import relationship, Session as sqlalchemySession

import config
from db.user import User


class Session(config.DB.Model):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    key = Column(String(64), unique=True, nullable=False)

    user = relationship("User", backref="sessions")

    @staticmethod
    def get_user(db: sqlalchemySession, key) -> User | None:
        s = db.query(Session).filter(Session.key==key).first()
        if s is None:
            return None
        return s.user
