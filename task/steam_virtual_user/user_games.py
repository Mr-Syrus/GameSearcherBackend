from celery import Task
from sqlalchemy import *
from sqlalchemy.orm import Session

import config
from db.steam.user_games import UserGames


@config.CELERY_APP.task(bind=True)
def user_games(self: Task, id_games: int):
    with config.DB.get_db_session() as db:
        db: Session

        avg_playtime = db.query(func.avg(UserGames.playtime_hours)) \
            .filter(UserGames.games_id == id_games) \
            .scalar()
        median_playtime = db.query(func.percentile_cont(0.5).within_group(UserGames.playtime_hours)) \
            .filter(UserGames.games_id == id_games) \
            .scalar()
        mode_playtime = db.query(func.mode().within_group(UserGames.playtime_hours)) \
            .filter(UserGames.games_id == id_games) \
            .scalar()
        mode_hours = db.query(
            func.mode().within_group((UserGames.playtime_hours / 60.0).label('hours'))
        ).filter(UserGames.games_id == id_games).scalar()


        ids_users = db.query(UserGames.id).filter(
            UserGames.games_id == id_games,
            UserGames.playtime_hours>=median_playtime
        ).scalar()

        datas = db.query(UserGames).filter(
            UserGames.id._in(ids_users),
            UserGames.games_id != id_games
        ).scalar()

