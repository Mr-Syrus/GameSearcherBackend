import hashlib
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, Query
from pydantic import BaseModel
from sqlalchemy import *
from sqlalchemy.orm import Session as DbSession

from db.likes_games import LikesGames
from dependency.user import get_user

import config
from db.user import User
from db.session import Session


def likes_get(
        user: User = Depends(get_user),
        db: DbSession = Depends(config.DB.get_db),
):
    games_id = db.query(LikesGames.game_id).filter(
        LikesGames.user_id == user.id
    ).all()
    return [i[0] for i in games_id]


def likes_post(
        game_id=Query(),
        user: User = Depends(get_user),
        db: DbSession = Depends(config.DB.get_db),
):
    lg = db.query(LikesGames).filter(
        LikesGames.user_id == user.id,
        LikesGames.game_id == game_id
    ).first()
    if lg:
        db.delete(lg)
    else:
        db.add(LikesGames(
            user_id=user.id,
            game_id=game_id
        ))
    db.commit()
    return likes_get(user, db)


def init():
    router = APIRouter(prefix="/likes")
    router.get("")(likes_get)
    router.post("")(likes_post)
    return router
