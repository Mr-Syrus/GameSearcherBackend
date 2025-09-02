import io
import os
from urllib.parse import urlparse

import requests
from celery import Task
from minio import S3Error
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

import config
import my_requests
from db.steam.games import Games
from my_lib.split_list import split_list


@config.CELERY_APP.task(bind=True)
def img(self: Task, url:str):
    try:
        # 1. скачать файл в память
        r = my_requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        data = io.BytesIO(r.content)

        # 2. имя объекта (берем из url)
        object_name = urlparse(url).path

        # 3. загрузить в MinIO
        config.MINIO.put_object(
            config.BUCKET_NAME,
            object_name,
            data,
            length=len(r.content),
            content_type=r.headers.get("Content-Type", "application/octet-stream"),
        )

    except (S3Error, requests.RequestException) as e:
        self.retry(exc=e, countdown=10, max_retries=3)


def init(): pass
