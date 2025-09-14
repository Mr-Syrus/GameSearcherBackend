from fastapi import APIRouter, Depends

from db.user import User
from dependency.user import get_user as dependency_get_user

from . import login, register, likes


def get_user(
        user: User = Depends(dependency_get_user)
):
    return user.get_model()


def init():
    router = APIRouter(prefix="/user")
    router.get("")(get_user)

    router.include_router(login.init())
    router.include_router(register.init())
    router.include_router(likes.init())

    return router
