import config
from . import steam, user

def init():
    # config.DB.drop_all()
    config.DB.create_all()
