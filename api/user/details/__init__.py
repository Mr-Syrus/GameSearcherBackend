from fastapi import APIRouter, Depends

import config
from db.likes_games import LikesGames
from db.steam.games import Games
from db.steam.games_to_genres import GamesToGenres
from db.steam.genres import Genres
from db.user import User
from dependency.user import get_user as dependency_get_user
from sqlalchemy.orm import Session as DbSession, load_only


def get_user_details(
        user: User = Depends(dependency_get_user),
        db: DbSession = Depends(config.DB.get_db),

):
    res = user.get_model()

    games = (
        db
        .query(Games).options(
            load_only(
                Games.id,
            )
        )
        .join(LikesGames, LikesGames.game_id == Games.id)
        .filter(
            LikesGames.user_id == user.id
        ).order_by(Games.release_date).all()
    )
    if games is None:
        res["likes"] = 0
        res["genres"] = []

        res["date"] = {}
        return res

    genres = (
        db
        .query(Genres.name)
        .join(GamesToGenres, GamesToGenres.id_genres == Genres.id)
        .join(Games, Games.id == GamesToGenres.id_games)
        .filter(
            Games.id.in_([i.id for i in games])
        ).all()
    )
    res["likes"] = len(games)
    res["genres"] = [i[0] for i in genres]

    date = {}
    min_year = 3000
    max_year = 0

    developers = set()
    for game in games:
        game: Games
        date[game.release_date.year] = game.name
        min_year = min(min_year, game.release_date.year)
        max_year = max(max_year, game.release_date.year)
        developers.update(game.developers)

    res["date"] = {}
    res["date"]["min_year"] = min_year
    res["date"]["max_year"] = max_year
    res["date"]["date"] = date

    res["developers"] = list(developers)

    return res


def init():
    router = APIRouter(prefix="/details")
    router.get("")(get_user_details)
    return router
