from sqlalchemy import *
import config


class User(config.DB.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    avatar = Column(Text)
    login = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)

    def get_model(self):
        return {
            "id": self.id,
            "name": self.name,
            "avatar": "/bucket/" + self.avatar if self.avatar else None,
        }
