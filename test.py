import logging

import uvicorn

import config
import incelization
from task.steam.games import games, scheduler_games

# Initialization
incelization.init()

app = config.APP

logging.basicConfig(level=logging.INFO)
# scheduler_games.apply_async()
games([1086160])
