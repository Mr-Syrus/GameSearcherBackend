import logging

import uvicorn

import config
import incelization
from task.steam.games import game, games

# Initialization
incelization.init()

app = config.APP

logging.basicConfig(level=logging.INFO)

games.apply_async()
