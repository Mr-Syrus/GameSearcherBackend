# import
import os

import redis
from celery import Celery
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from minio import Minio
import my_lib.db

load_dotenv()

# FastApi
APP: FastAPI

# DB
DB: my_lib.db.DB
DATABASE_URL: str = os.getenv('DATABASE_URL')

# celery
CELERY_APP: Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', "redis://192.168.0.192:6379/1")

# redis_cache
REDIS_LOCK: redis.Redis
REDIS_CACHE_URL = os.getenv('REDIS_CACHE_URL', "redis://192.168.0.192:6379/2")

MINIO:Minio
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
BUCKET_NAME = "game_searcher"

STEAM_API = os.getenv('STEAM_API')
