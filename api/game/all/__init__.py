import hashlib
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import *
from sqlalchemy.orm import Session as DbSession

import config
from db.steam.games import Games
from db.user import User
from db.session import Session
from typing import List, Optional, Dict, Any
from datetime import date
from pydantic import BaseModel


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

    ratings: Optional[Dict[str, Any]]

    class Config:
        orm_mode = True


def all(
        db: DbSession = Depends(config.DB.get_db),
):
    return db.query(Games).limit(1000).all()


def init():
    router = APIRouter(prefix="/all")
    router.get("", response_model=List[Game])(all)
    return router
