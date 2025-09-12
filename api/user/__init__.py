from fastapi import Cookie

from fastapi import APIRouter, Depends, HTTPException

import config
from . import login, register
from db.session import Session


def get_user(
        session_key: str | None = Cookie(default=None),
        db=Depends(config.DB.get_db),
):
    if session_key is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    u = Session.get_user(db, session_key)
    if u is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return u.get_model()


def init():
    router = APIRouter(prefix="/user")
    router.get("")(get_user)

    router.include_router(login.init())
    router.include_router(register.init())

    return router
