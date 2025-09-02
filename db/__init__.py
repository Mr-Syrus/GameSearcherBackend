import config
from . import steam, account

def init():
    # config.DB.drop_all()
    config.DB.create_all()
