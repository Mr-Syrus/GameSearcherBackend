import io
import os
from urllib.parse import urlparse

import requests
from PIL import Image
from celery import Task
from minio import S3Error
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

import config
import my_requests
from db.steam.games import Games
from my_lib.queue import QueueEnum
from my_lib.split_list import split_list

def file_exists(key):
    try:
        config.MINIO.stat_object(config.MINIO_BUCKET_NAME, key)
        return True
    except S3Error as e:
        if e.code == "NoSuchKey":
            return False
        raise  # другая ошибка

def convert(object_name, object_name_webp):
    # скачать из MinIO
    response = config.MINIO.get_object(config.MINIO_BUCKET_NAME, object_name)
    data = io.BytesIO(response.read())
    data.seek(0)

    # конвертировать в webp
    img = Image.open(data).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=80, method=6)
    buf.seek(0)

    # загрузить обратно в MinIO
    config.MINIO.put_object(
        config.MINIO_BUCKET_NAME,
        object_name_webp,
        buf,
        length=buf.getbuffer().nbytes,
        content_type="image/webp",
    )

    # удалить оригинал
    config.MINIO.remove_object(
        config.MINIO_BUCKET_NAME,
        object_name,
    )


@config.CELERY_APP.task(bind=True, queue=QueueEnum.STEAM_IMG.value)
def img(self: Task, url:str):
    try:
        # 1. имя объекта (берем из url)
        object_name = urlparse(url).path + ".webp"
        object_name_webp = urlparse(url).path + ".webp"
        if file_exists(object_name):
            return
        if file_exists(object_name_webp):
            convert(object_name, object_name_webp)
            return

        # 2. скачать файл в память
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()

        # 3. конвертировать в webp
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=80, method=6)
        buf.seek(0)


        # 4. загрузить в MinIO
        config.MINIO.put_object(
            config.MINIO_BUCKET_NAME,
            object_name_webp,
            buf,
            length=buf.getbuffer().nbytes,
            content_type="image/webp",
        )
    except (S3Error, requests.RequestException) as e:
        self.retry(exc=e, countdown=10, max_retries=3)


def init(): pass
