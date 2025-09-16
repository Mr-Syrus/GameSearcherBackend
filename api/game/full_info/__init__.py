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
from db.steam.screenshots import Screenshots
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
        from_attributes  = True


class GameFull(Game):
    screenshots: List[str]
    genres: List[str]


def full_info(
        id: int = Query(...),
        db: DbSession = Depends(config.DB.get_db),
):
    game_obj = db.query(Games).get(id)
    game:Game = Game.model_validate(game_obj)

    return GameFull(
        screenshots=[i[0] for i in db.query(Screenshots.path_full).filter(Screenshots.id_games==id).all()],
        genres=[i[0] for i in db.query(Genres.name).all()],
        **game.model_dump()
    )


def init():
    router = APIRouter(prefix="/full_info")
    router.get("")(full_info)
    return router
