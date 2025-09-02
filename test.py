import logging

import uvicorn

import config
import incelization
from task.steam.games import game

# Initialization
incelization.init()

app = config.APP

logging.basicConfig(level=logging.INFO)

game(1290160)
