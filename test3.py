import logging
from urllib.parse import urlparse

import uvicorn
from minio import S3Error

import config
import incelization
from db.session import Session
from db.steam.games import Games
from db.steam.screenshots import Screenshots
from db.steam.user_games import UserGames
from task.steam import img
from task.steam.games import games, scheduler_games
from task.steam.user import user
from task.steam_virtual_user.user_games import scheduler_user_games
from tqdm import tqdm

# Initialization
incelization.init()

app = config.APP

logging.basicConfig(level=logging.INFO)

def file_exists(key):
    try:
        config.MINIO.stat_object(config.MINIO_BUCKET_NAME, key)
        return True
    except S3Error as e:
        if e.code == "NoSuchKey":
            return False
        raise  # другая ошибка

with config.DB.get_db_session() as db:
    db: Session

    sc = db.session.query(Screenshots).all()
    for s in tqdm(sc, desc="Screenshots"):
        s.bucket_path_thumbnail = urlparse(s.path_thumbnail).path
        if not file_exists(s.bucket_path_thumbnail):
            img.img.apply_async((s.path_thumbnail,))

        s.bucket_path_full = urlparse(s.path_full).path
        if not file_exists(s.bucket_path_full):
            img.img.apply_async((s.path_full,))


    gs = db.session.query(Games).all()
    for g in tqdm(gs, desc="Games"):
        g.bucket_header_image = urlparse(g.header_image).path
        if not file_exists(g.bucket_header_image):
            img.img.apply_async((g.header_image,))

        g.bucket_capsule_image = urlparse(g.capsule_image).path
        if not file_exists(g.bucket_capsule_image):
            img.img.apply_async((g.capsule_image,))

        g.bucket_capsule_imagev5 = urlparse(g.capsule_imagev5).path
        if not file_exists(g.bucket_capsule_imagev5):
            img.img.apply_async((g.capsule_imagev5,))

        g.bucket_background = urlparse(g.background).path
        if not file_exists(g.bucket_background):
            img.img.apply_async((g.background,))

        g.bucket_background_raw = urlparse(g.background_raw).path
        if not file_exists(g.bucket_background_raw):
            img.img.apply_async((g.background_raw,))
