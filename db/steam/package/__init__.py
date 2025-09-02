from sqlalchemy import *
import config


class Package(config.DB.Model):
    __tablename__ = 'package'
    __table_args__ = {"schema": "steam"}

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    title = Column(Text)
    description = Column(Text)
    selection_text = Column(Text)
    save_text = Column(Text)
    display_type = Column(Integer)
    is_recurring_subscription = Column(Boolean)

