import io
from datetime import datetime

from PIL import Image
from fastapi import FastAPI, Request, Depends, UploadFile, File, APIRouter

import config
from db.likes_games import LikesGames
from db.steam.games import Games
from db.steam.games_to_genres import GamesToGenres
from db.steam.genres import Genres
from db.user import User
from dependency.user import get_user as dependency_get_user
from sqlalchemy.orm import Session as DbSession, load_only


def switch_avatar(
    avatar: UploadFile = File(...),
    user: User = Depends(dependency_get_user),
    db: DbSession = Depends(config.DB.get_db),
):
    # читаем байты файла
    avatar_bytes = avatar.file.read()

    # открываем картинку
    img = Image.open(io.BytesIO(avatar_bytes)).convert("RGB")

    img.thumbnail((512, 512), Image.Resampling.LANCZOS)

    # конвертируем в webp
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=80, method=2)
    buf.seek(0)

    # заливаем в MinIO
    object_name_webp = f"user/icon/{user.id}_{int(datetime.now().timestamp())}.webp"
    config.MINIO.put_object(
        config.MINIO_BUCKET_NAME,
        object_name_webp,
        buf,
        length=buf.getbuffer().nbytes,
        content_type="image/webp",
    )

    # обновляем ссылку в БД
    user.avatar = object_name_webp
    db.add(user)
    db.commit()

    return {"status": "ok"}


def init():
    router = APIRouter(prefix="/switch_avatar")
    router.post("")(switch_avatar)
    return router
