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
    if not game_obj:
        raise HTTPException(status_code=404, detail="Game not found")

    game = Game(
        id=game_obj.id,
        type=game_obj.type,
        name=game_obj.name,
        required_age=game_obj.required_age,
        is_free=game_obj.is_free,
        detailed_description=game_obj.detailed_description,
        about_the_game=game_obj.about_the_game,
        short_description=game_obj.short_description,
        fullgame_appid=game_obj.fullgame_appid,
        fullgame_name=game_obj.fullgame_name,
        supported_languages=game_obj.supported_languages,
        header_image=game_obj.header_image,
        capsule_image=game_obj.capsule_image,
        capsule_imagev5=game_obj.capsule_imagev5,
        bucket_header_image=game_obj.bucket_header_image,
        bucket_capsule_image=game_obj.bucket_capsule_image,
        bucket_capsule_imagev5=game_obj.bucket_capsule_imagev5,
        website=game_obj.website,
        pc_requirements=game_obj.pc_requirements,
        mac_requirements=game_obj.mac_requirements,
        linux_requirements=game_obj.linux_requirements,
        developers=game_obj.developers,
        publishers=game_obj.publishers,
        platforms_windows=game_obj.platforms_windows,
        platforms_mac=game_obj.platforms_mac,
        platforms_linux=game_obj.platforms_linux,
        release_date=game_obj.release_date,
        coming_soon=game_obj.coming_soon,
        background=game_obj.background,
        background_raw=game_obj.background_raw,
        bucket_background=game_obj.bucket_background,
        bucket_background_raw=game_obj.bucket_background_raw,
        ratings=game_obj.ratings,
        total_reviews=game_obj.total_reviews,
        total_reviews_positive=game_obj.total_reviews_positive,
        total_reviews_negative=game_obj.total_reviews_negative,
        reviews_score=game_obj.reviews_score,
    )

    return GameFull(
        screenshots=[i[0] for i in db.query(Screenshots.path_full).filter(Screenshots.id_games==id).all()],
        genres=[i[0] for i in db.query(Genres.name).all()],
        **game.model_dump()
    )


def init():
    router = APIRouter(prefix="/full_info")
    router.get("")(full_info)
    return router
