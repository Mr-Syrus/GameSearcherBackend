import hashlib
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import *
from sqlalchemy.orm import Session as DbSession

import config
from db.user import User
from db.session import Session


class LoginRequest(BaseModel):
    username: str
    login: str
    password: str


def register(
        data: LoginRequest,
        response: Response,
        db: DbSession = Depends(config.DB.get_db),
):
    account: User = db.query(User).filter(
        or_(
            User.name == data.username,
            User.login == data.login
        )
    ).first()
    if account is not None:
        raise HTTPException(status_code=400, detail="Аккаунт с таким именем или логином уже существует")

    account: User = User(
        name=data.username,
        login=data.login,
        password=hashlib.sha256(data.password.encode("utf-8")).hexdigest(),
    )
    db.add(account)
    db.flush()

    s = Session(
        user_id=account.id,
        key=hashlib.sha256(str(datetime.now()).encode("utf-8")).hexdigest(),
    )
    db.add(s)
    db.commit()
    response.set_cookie(key="session_key", value=s.key, httponly=False)
    return {"detail": "ok"}


def init():
    router = APIRouter(prefix="/register")
    router.post("")(register)
    return router
