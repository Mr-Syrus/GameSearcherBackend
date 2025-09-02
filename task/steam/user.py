import requests
from celery import Task
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

import config
import my_requests
from db.steam.games import Games
from db.steam.user_games import UserGames
from my_lib.split_list import split_list


@config.CELERY_APP.task(bind=True)
def user(self: Task, steam_id: int):
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    r = my_requests.get(url, params={
        "key": config.STEAM_API,
        "steamid": steam_id,
        "include_played_free_games": 1
    })
    data = r.json()

    games = data.get("response", {}).get("games", [])

    with config.DB.get_db_session() as db:
        db: Session
        for g in games:
            appid = g.get("appid")
            playtime_hours = g.get("playtime_forever", 0)
            rtime_last_played = g.get("rtime_last_played", 0)

            db.merge(UserGames(
                id=steam_id,
                id_games=appid,
                playtime_hours=playtime_hours,
                rtime_last_played=rtime_last_played,
            ))
        db.commit()
        url = f"https://api.steampowered.com/ISteamUser/GetFriendList/v1/"
        r = my_requests.get(url, params={
            "key": config.STEAM_API,
            "steamid": steam_id
        })
        data = r.json()

        friends = data.get("friendslist", {}).get("friends", [])
        for f in friends:
            if not db.query(UserGames.id).filter_by(id=f["steamid"]).first():
                user.apply_async((f["steamid"],))


def init(): pass
