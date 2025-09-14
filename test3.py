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
from task.steam.games import games, scheduler_games, get_reviews
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
    gs = db.query(Games).all()
    for g in tqdm(gs, desc="Games"):
        get_reviews.apply_async((g.id,))

    last_100 = (
        db.query(UserGames)
        .order_by(UserGames.id.desc())
        .limit(100)
        .all()
    )
    for i in tqdm(last_100, desc="pars"):
        user.apply_async((i.id,))

    img_count = 0
    with tqdm(gs, desc="Games") as pbar:
        for g in pbar:
            g.bucket_header_image = urlparse(g.header_image).path
            if not file_exists(g.bucket_header_image):
                img.img.apply_async((g.header_image,))
                img_count += 1

            g.bucket_capsule_image = urlparse(g.capsule_image).path
            if not file_exists(g.bucket_capsule_image):
                img.img.apply_async((g.capsule_image,))
                img_count += 1

            g.bucket_capsule_imagev5 = urlparse(g.capsule_imagev5).path
            if not file_exists(g.bucket_capsule_imagev5):
                img.img.apply_async((g.capsule_imagev5,))
                img_count += 1

            g.bucket_background = urlparse(g.background).path
            if not file_exists(g.bucket_background):
                img.img.apply_async((g.background,))
                img_count += 1

            g.bucket_background_raw = urlparse(g.background_raw).path
            if not file_exists(g.bucket_background_raw):
                img.img.apply_async((g.background_raw,))
                img_count += 1

            pbar.set_postfix({"scheduled_images": img_count/5})

    db.commit()

    img_conut = 0
    sc = db.query(Screenshots).all()
    with tqdm(sc, desc="Screenshots") as pbar:
        for s in pbar:
            s.bucket_path_thumbnail = urlparse(s.path_thumbnail).path
            if not file_exists(s.bucket_path_thumbnail):
                img.img.apply_async((s.path_thumbnail,))
                img_count += 1

            s.bucket_path_full = urlparse(s.path_full).path
            if not file_exists(s.bucket_path_full):
                img.img.apply_async((s.path_full,))
                img_count += 1

            pbar.set_postfix({"scheduled_images": img_count/2})

    db.commit()