import hashlib
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, Query, Cookie
from pydantic import BaseModel
from sqlalchemy import *
from sqlalchemy.orm import Session as DbSession

import config
from db.likes_games import LikesGames
from db.steam.developer import Developer
from db.steam.games import Games
from db.steam.genres import Genres
from db.user import User
from db.session import Session
from typing import List, Optional, Dict, Any
from datetime import date
from pydantic import BaseModel
from dependency.user import get_user as dependency_get_user
from sqlalchemy import select, func
from sqlalchemy import select, func
def filter(
        db: DbSession = Depends(config.DB.get_db),
):
    stmt = db.query(
        func.min(Games.release_date),
        func.max(Games.release_date)
    ).one()

    min_date, max_date = stmt

    return {
        "genres": [i[0] for i in db.query(Genres.name).all()],
        "release_date": {
            "min": min_date.year,
            "max": max_date.year,
        },
        "developers": [i[0] for i in db.query(Developer.name).all()]
    }


def init():
    router = APIRouter(prefix="/filter")
    router.get("")(filter)
    return router
