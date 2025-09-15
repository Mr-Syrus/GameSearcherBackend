from fastapi import APIRouter

from . import all,filter,full_info


def init():
    router = APIRouter(prefix="/game")
    router.include_router(all.init())

    router.include_router(filter.init())
    router.include_router(full_info.init())

    return router
