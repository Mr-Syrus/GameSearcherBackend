import logging

import uvicorn

import config
import incelization
from task.steam.games import games, scheduler_games
from task.steam.user import user
from task.steam_virtual_user.user_games import scheduler_user_games

# Initialization
incelization.init()

app = config.APP

logging.basicConfig(level=logging.INFO)
scheduler_user_games()
# user("76561199001568702")
# scheduler_games()
# scheduler_games.apply_async()
# games(508620)
