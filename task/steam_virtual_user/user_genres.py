from celery import Task
from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

import config
from db.steam.games_to_genres import GamesToGenres
from db.steam.genres import Genres
from db.steam.user_games import UserGames
from db.steam_virtual_user.virtual_user_games import VirtualUserGames


@config.CELERY_APP.task(bind=True)
def scheduler_user_genres(self: Task):
    with config.DB.get_db_session() as db:
        db: Session
        unique_ids = db.query(Genres.id).distinct().all()
        unique_ids = [id_[0] for id_ in unique_ids]
    for i in unique_ids:
        user_genres(i)
        # user_genres.apply_async((i,))


@config.CELERY_APP.task(bind=True)
def user_genres(self: Task, id_genres: int):
    with (config.DB.get_db_session() as db):
        db: Session

        ids_games = select(GamesToGenres.id_games).where(
            GamesToGenres.id_genres == id_genres,
        )

        datas = db.query(UserGames).filter(
            UserGames.id_games.in_(ids_games),
            UserGames.playtime_hours > 0
        ).all()

        for data in datas:
            points=points
            stmt = insert(VirtualUserGames).values({
                "id_genres": id_genres,
                "id_games": data.id_games,
                "points": points
            }).on_conflict_do_update(
                index_elements=["id_games", "id_genres"],
                set_={
                    "points": points
                }
            )
            db.execute(stmt)
        db.commit()


def init():
    pass
