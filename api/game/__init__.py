from fastapi import APIRouter

from . import all


def init():
    router = APIRouter(prefix="/game")
    router.include_router(all.init())

    return router
