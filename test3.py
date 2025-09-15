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
    c=0
    gs = db.query(Games).all()
    # for g in tqdm(gs, desc="Games"):
    #     get_reviews.apply_async((g.id,))

    # last_100 = (
    #     db.query(UserGames)
    #     .order_by(UserGames.id.desc())
    #     .limit(100)
    #     .all()
    # )
    # for i in tqdm(last_100, desc="pars"):
    #     user.apply_async((i.id,))

    img_count = 0

    def process_image(url, bucket_attr):
        global img_count
        img.img.apply_async((url,))
        return
        object_name = urlparse(url).path
        webp_name = object_name + ".webp"
        setattr(bucket_attr[0], bucket_attr[1], webp_name)

        if file_exists(object_name):
            try:
                img.convert(object_name, webp_name)
            except Exception as e:
                print(e)
                config.MINIO.remove_object(
                    config.MINIO_BUCKET_NAME,
                    webp_name,
                )
            return
        if not file_exists(webp_name):
            img.img.apply_async((url,))
            img_count += 1

    with tqdm(gs, desc="Games") as pbar:
        for g in pbar:
            c+=1
            process_image(g.header_image, (g, "bucket_header_image"))
            process_image(g.capsule_image, (g, "bucket_capsule_image"))
            process_image(g.capsule_imagev5, (g, "bucket_capsule_imagev5"))
            process_image(g.background, (g, "bucket_background"))
            process_image(g.background_raw, (g, "bucket_background_raw"))

            pbar.set_postfix({"scheduled_images": img_count})
            if c%1000==0:
                db.commit()
    db.commit()

    img_conut = 0
    sc = db.query(Screenshots).all()
    with tqdm(sc, desc="Screenshots") as pbar:
        for s in pbar:
            process_image(s.path_thumbnail, (s, "bucket_path_thumbnail"))
            process_image(s.path_full, (s, "bucket_path_full"))

            pbar.set_postfix({"scheduled_images": img_count})
            if c%1000==0:
                db.commit()
    db.commit()