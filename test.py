import logging

import uvicorn
from tqdm import tqdm

import config
import incelization
from db.session import Session
from db.steam.games import Games
from db.steam.user_games import UserGames
from task.steam.games import games, scheduler_games
from task.steam.user import user
from task.steam_virtual_user.user_games import scheduler_user_games, user_games

# Initialization
incelization.init()

app = config.APP

logging.basicConfig(level=logging.INFO)
# scheduler_user_games()
# user_games(292030)

# user("76561199851203448")
# scheduler_games()
# scheduler_games.apply_async()
# games(3180070)

# with config.DB.get_db_session() as db:
#     db: Session
#
#     last_100 = (
#         db.query(UserGames)
#         .order_by(UserGames.id.desc())
#         .limit(100)
#         .all()
#     )
#     for i in last_100:
#         user(i.id)

# with config.DB.get_db_session() as db:
#     db: Session
#
#     missing_ids = db.query(UserGames.id_games) \
#         .filter(~UserGames.id_games.in_(db.query(Games.id))) \
#         .distinct() \
#         .all()
#
#     missing_ids = [x[0] for x in missing_ids]
#     for i in tqdm(missing_ids):
#         games.apply_async(args=(i,))

