import hashlib
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from pydantic import BaseModel
from sqlalchemy import *
from sqlalchemy.orm import Session as DbSession

import config
from db.user import User
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
    return u