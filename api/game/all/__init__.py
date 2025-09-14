import hashlib
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, Query, Cookie
from pydantic import BaseModel
from sqlalchemy import *
from sqlalchemy.orm import Session as DbSession, load_only

import config
from db.likes_games import LikesGames
from db.steam.categories import Categories
from db.steam.developer import Developer
from db.steam.games import Games
from db.steam.games_to_categories import GamesToCategories
from db.steam.games_to_developer import GamesToDeveloper
from db.steam.games_to_genres import GamesToGenres
from db.steam.games_to_publisher import GamesToPublisher
from db.steam.genres import Genres
from db.steam.publisher import Publisher
from db.user import User
from db.session import Session
from typing import List, Optional, Dict, Any
from datetime import date
from pydantic import BaseModel
from dependency.user import get_user as dependency_get_user


class Game(BaseModel):
    id: int
    name: str
    header_image: Optional[str]

    platforms_windows: bool = False
    platforms_mac: bool = False
    platforms_linux: bool = False

    release_date: Optional[date]

    reviews_score: Optional[int]

    class Config:
        from_attributes = True


def all(
        is_liked: bool = Query(False),
        is_recommendations: bool = Query(False),

        genres: Optional[List[str]] = Query(None),
        categories: Optional[List[str]] = Query(None),
        developers: Optional[List[str]] = Query(None),
        publishers: Optional[List[str]] = Query(None),

        platforms: Optional[List[str]] = Query(None),

        min_year: Optional[int] = Query(None),
        max_year: Optional[int] = Query(None),

        min_rating: Optional[int] = Query(None),
        max_rating: Optional[int] = Query(None),

        page: int = Query(1, ge=1),
        limit: int = Query(100, ge=1, le=100),

        session_key: str | None = Cookie(default=None),

        db: DbSession = Depends(config.DB.get_db),
):
    query = db.query(Games).filter(Games.type == "game").options(
        load_only(
            Games.id,
            Games.name,
            Games.header_image,
            Games.platforms_windows,
            Games.platforms_mac,
            Games.platforms_linux,
            Games.release_date,
            Games.reviews_score
        )
    )

    if is_liked:
        user = dependency_get_user(session_key, db)
        query = query.join(LikesGames, (LikesGames.game_id == Games.id) & (LikesGames.user_id == user.id))
        query = query.filter(LikesGames.user_id == user.id)

    if genres:
        query = query.join(GamesToGenres, Games.id == GamesToGenres.id_games) \
            .join(Genres, GamesToGenres.id_genres == Genres.id) \
            .filter(Genres.name.in_(genres))

    if categories:
        query = query.join(GamesToCategories, Games.id == GamesToCategories.id_games) \
            .join(Categories, GamesToCategories.id_categories == Categories.id) \
            .filter(Categories.name.in_(categories))

    if developers:
        query = query.join(GamesToDeveloper, Games.id == GamesToDeveloper.id_games) \
            .join(Developer, GamesToDeveloper.id_developer == Developer.id) \
            .filter(Developer.name.in_(developers))

    if publishers:
        query = query.join(GamesToPublisher, Games.id == GamesToPublisher.id_games) \
            .join(Publisher, GamesToPublisher.id_publisher == Publisher.id) \
            .filter(Publisher.name.in_(publishers))

    if platforms:
        platforms = set(platforms)
        if "windows" in platforms:
            query = query.filter(Games.platforms_windows == True)
        if "linux" in platforms:
            query = query.filter(Games.platforms_linux == True)
        if "mac" in platforms:
            query = query.filter(Games.platforms_mac == True)

    if min_year:
        query = query.filter(Games.release_date >= date(min_year, 1, 1))

    if max_year:
        query = query.filter(Games.release_date <= date(max_year, 12, 31))

    if min_rating:
        query = query.filter(Games.reviews_score >= min_rating)

    if max_rating:
        query = query.filter(Games.reviews_score <= max_rating)

    if is_recommendations:
        pass

    return query.limit(limit).offset((page - 1) * limit).all()


def init():
    router = APIRouter(prefix="/all")
    router.get("", response_model=List[Game])(all)
    return router
