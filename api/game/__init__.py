from fastapi import APIRouter

from . import all,filter


def init():
    router = APIRouter(prefix="/game")
    router.include_router(all.init())

    router.include_router(filter.init())

    return router
