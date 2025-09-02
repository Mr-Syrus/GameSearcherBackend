import logging
import os

from celery import Celery
from fastapi import FastAPI
from sqlalchemy import NullPool, QueuePool
import boto3
import redis
from celery import Celery
from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import MongoClient
from pymongo.synchronous.database import Database
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import fakeredis
import my_lib.db
import config
from minio import Minio

# FastApi
config.APP = FastAPI()

# SQLAlchemy
config.DB = my_lib.db.DB(
    config.DATABASE_URL,
    poolclass=NullPool,
)

# celery
config.CELERY_APP = Celery(
    "worker",
    broker=config.CELERY_BROKER_URL,
)
if config.REDIS_CACHE_URL:
    config.REDIS_LOCK = redis.from_url(config.REDIS_CACHE_URL)
else:
    config.REDIS_LOCK = fakeredis.FakeStrictRedis()

config.MINIO = Minio(
    "192.168.0.192",          # адрес MinIO
    access_key=config.ACCESS_KEY,   # логин
    secret_key=config.SECRET_KEY,   # пароль
    secure=True               # True если https
)
if not config.MINIO.bucket_exists(config.BUCKET_NAME):
    config.MINIO.make_bucket(config.BUCKET_NAME)

def init():

    import api
    api.init()

    import task
    task.init()

    import db
    db.init()
