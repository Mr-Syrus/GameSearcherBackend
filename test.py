import logging

import uvicorn

import config
import incelization
from task.steam.games import games, scheduler_games
from task.steam.user import user

# Initialization
incelization.init()

app = config.APP

logging.basicConfig(level=logging.INFO)
# user("76561199001568702")
scheduler_games()
# scheduler_games.apply_async()
# games(1086160)
