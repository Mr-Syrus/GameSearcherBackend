from celery import Task
from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

import config
from db.steam.user_games import UserGames
from db.steam_virtual_user.virtual_user_games import VirtualUserGames


@config.CELERY_APP.task(bind=True)
def scheduler_user_games(self: Task):
    with config.DB.get_db_session() as db:
        db: Session
        unique_ids = db.query(UserGames.id_games).filter(
                UserGames.playtime_hours > 0
        ).distinct().all()
        unique_ids = [id_[0] for id_ in unique_ids]

    for i in unique_ids:
        # user_games(i)
        user_games.apply_async((i,))


@config.CELERY_APP.task(bind=True)
def user_games(self: Task, id_games: int):
    with (config.DB.get_db_session() as db):
        db: Session

        # avg_playtime = db.query(func.avg(UserGames.playtime_hours)) \
        #     .filter(UserGames.id_games == id_games) \
        #     .scalar()
        median_playtime = db.query(func.percentile_cont(0.5).within_group(UserGames.playtime_hours)) \
            .filter(
            UserGames.id_games == id_games,
                UserGames.playtime_hours > 0
        ).scalar()
        # mode_playtime = db.query(func.mode().within_group(UserGames.playtime_hours)) \
        #     .filter(UserGames.id_games == id_games) \
        #     .scalar()
        # mode_hours = db.query(
        #     func.mode().within_group((UserGames.playtime_hours / 60.0).label('hours'))
        # ).filter(UserGames.id_games == id_games).scalar()
        if median_playtime is None:
            return
        ids_users = select(UserGames.id).where(
            UserGames.id_games == id_games,
            UserGames.playtime_hours >= median_playtime
        )

        datas = db.query(UserGames).filter(
            UserGames.id.in_(ids_users),
            UserGames.id_games != id_games,
            UserGames.playtime_hours > 0
        ).all()

        median_playtimes = db.query(
            UserGames.id_games,
            func.percentile_cont(0.5).within_group(UserGames.playtime_hours).label("median_playtime")
        ).filter(
            UserGames.id_games.in_([i.id_games for i in datas]),
            UserGames.playtime_hours > 0
        ).group_by(UserGames.id_games).all()

        # Создадим словарь для быстрого доступа
        median_dict = {g: m for g, m in median_playtimes}

        for data in datas:
            median_playtime_data = median_dict.get(data.id_games)
            points = data.playtime_hours / median_playtime_data
            stmt = insert(VirtualUserGames).values({
                "id_games": id_games,
                "id_games_likes": data.id_games,
                "points": points
            }).on_conflict_do_update(
                index_elements=["id_games", "id_games_likes"],
                set_={
                    "points": points
                }
            )
            db.execute(stmt)
        db.commit()


def init():
    pass
