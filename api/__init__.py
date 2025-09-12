import config
from . import user, game


def init():
    app = config.APP

    app.include_router(user.init())

    app.include_router(game.init())
