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
    with config.DB.get_db_session() as db:
        db: Session

        # 1. Медиана для выбранной игры
        median_playtime = db.query(
            func.percentile_cont(0.5).within_group(UserGames.playtime_hours)
        ).filter(
            UserGames.id_games == id_games,
            UserGames.playtime_hours > 0
        ).scalar()

        if median_playtime is None:
            return

        # 2. Подзапрос пользователей, у которых >= медианы
        ids_users_subq = select(UserGames.id).where(
            UserGames.id_games == id_games,
            UserGames.playtime_hours >= median_playtime
        ).subquery()

        # 3. Подзапрос всех других игр этих пользователей + их playtime
        datas_subq = select(
            UserGames.id_games.label("id_games_likes"),
            UserGames.id,
            UserGames.playtime_hours
        ).where(
            UserGames.id.in_(ids_users_subq),
            UserGames.id_games != id_games,
            UserGames.playtime_hours > 0
        ).subquery()

        # 4. Медианы сразу для всех id_games_likes одним запросом
        median_playtimes = db.query(
            datas_subq.c.id_games_likes,
            func.percentile_cont(0.5).within_group(datas_subq.c.playtime_hours).label("median_playtime")
        ).group_by(datas_subq.c.id_games_likes).subquery()

        # 5. Соединяем и считаем points на уровне SQL
        joined = select(
            datas_subq.c.id_games_likes,
            (datas_subq.c.playtime_hours / median_playtimes.c.median_playtime).label("points")
        ).join(
            median_playtimes,
            median_playtimes.c.id_games_likes == datas_subq.c.id_games_likes
        )

        results = db.execute(joined).all()

        if not results:
            return

        # 6. Bulk insert/update
        stmt = insert(VirtualUserGames).values([
            {"id_games": id_games, "id_games_likes": g, "points": p}
            for g, p in results
        ]).on_conflict_do_update(
            index_elements=["id_games", "id_games_likes"],
            set_={"points": func.excluded.points}
        )

        db.execute(stmt)
        db.commit()


def init():
    pass
