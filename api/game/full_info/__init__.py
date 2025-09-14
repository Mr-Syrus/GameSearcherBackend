import hashlib
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, Query, Cookie
from pydantic import BaseModel
from sqlalchemy import *
from sqlalchemy.orm import Session as DbSession

import config
from db.likes_games import LikesGames
from db.steam.games import Games
from db.steam.games_to_genres import GamesToGenres
from db.steam.genres import Genres
from db.user import User
from db.session import Session
from typing import List, Optional, Dict, Any
from datetime import date
from pydantic import BaseModel
from dependency.user import get_user as dependency_get_user


class Game(BaseModel):
    id: int
    type: Optional[str]
    name: str
    required_age: int = 0
    is_free: bool = False

    detailed_description: Optional[str]
    about_the_game: Optional[str]
    short_description: Optional[str]

    fullgame_appid: Optional[int]
    fullgame_name: Optional[str]

    supported_languages: Optional[List[str]]

    header_image: Optional[str]
    capsule_image: Optional[str]
    capsule_imagev5: Optional[str]

    bucket_header_image: Optional[str]
    bucket_capsule_image: Optional[str]
    bucket_capsule_imagev5: Optional[str]

    website: Optional[str]

    pc_requirements: Optional[Any]
    mac_requirements: Optional[Any]
    linux_requirements: Optional[Any]

    developers: Optional[List[str]]
    publishers: Optional[List[str]]

    platforms_windows: bool = False
    platforms_mac: bool = False
    platforms_linux: bool = False

    release_date: Optional[date]
    coming_soon: bool = False

    background: Optional[str]
    background_raw: Optional[str]

    bucket_background: Optional[str]
    bucket_background_raw: Optional[str]

    ratings: Optional[Dict[str, Any]]

    total_reviews: Optional[int]
    total_reviews_positive: Optional[int]
    total_reviews_negative: Optional[int]
    reviews_score: Optional[int]

    class Config:
        orm_mode = True


def all(
        is_liked: bool = Query(False),

        genres: Optional[List[str]] = Query(None),

        platforms: Optional[List[str]] = Query(None),
        developers: Optional[List[str]] = Query(None),

        min_year: Optional[List[str]] = Query(None),
        max_year: Optional[List[str]] = Query(None),

        min_rating: Optional[List[str]] = Query(None),
        max_rating: Optional[List[str]] = Query(None),

        page: int = Query(1, ge=1),
        limit: int = Query(100, ge=1, le=100),

        session_key: str | None = Cookie(default=None),

        db: DbSession = Depends(config.DB.get_db),
):
    query = db.query(Games).filter(Games.type == "game")

    if is_liked:
        user = dependency_get_user(session_key, db)
        query = query.join(LikesGames, (LikesGames.game_id == Games.id) & (LikesGames.user_id == user.id))
        query = query.filter(LikesGames.user_id == user.id)

    if genres:
        query = query.join(GamesToGenres, Games.id == GamesToGenres.id_games) \
            .join(Genres, GamesToGenres.id_genres == Genres.id) \
            .filter(Genres.name.in_(genres))

    if platforms:
        platforms = set(platforms)
        if "windows" in platforms:
            query = query.filter(Games.platforms_windows == True)
        if "linux" in platforms:
            query = query.filter(Games.platforms_linux == True)
        if "mac" in platforms:
            query = query.filter(Games.platforms_mac == True)

    if developers:
        query = query.filter(Games.developers.overlap(developers))

    return query.limit(limit).offset((page - 1) * limit).all()


def init():
    router = APIRouter(prefix="/all")
    router.get("", response_model=List[Game])(all)
    return router
