from datetime import datetime
from typing import List

import requests
from celery import Task
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
import json
import config
import my_requests
from db.steam.categories import Categories
from db.steam.games import Games
from db.steam.games_to_categories import GamesToCategories
from db.steam.games_to_genres import GamesToGenres
from db.steam.games_to_package import GamesToPackage
from db.steam.genres import Genres
from db.steam.package import Package
from db.steam.screenshots import Screenshots
from my_lib.split_list import split_list
from . import img


@config.CELERY_APP.task(bind=True)
def scheduler_games(self: Task):
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = my_requests.get(url)
    data_list = response.json()
    for app in data_list["applist"]["apps"]:
        if "dlc" in app["name"].lower():
            print("scip:",app["appid"], app["name"])
            continue
        print(app["appid"], app["name"])
        games.apply_async((app["appid"],))


@config.CELERY_APP.task(bind=True)
def games(self: Task, id: int):
    with config.DB.get_db_session() as db:
        db: Session

        categories = {v.id: v for v in db.query(Categories).all()}
        genres = {v.id: v for v in db.query(Genres).all()}

        url = "https://store.steampowered.com/api/appdetails"
        response = my_requests.get(url, params={
            "appids": id,
        })
        data_steam: dict = response.json()
        for id, app in data_steam.items():
            if not app["success"]:
                continue
            if len(app["data"]) < 5:
                continue
            app_data = app["data"]

            for i in [
                "header_image",
                "capsule_image",
                "capsule_imagev5",
                "background",
                "background_raw"
            ]:
                if i in app_data:
                    img.img.apply_async((app_data[i],))

            for package_id, package_group in zip(app_data.get("packages", []), app_data.get("package_groups", [])):
                db.merge(Package(
                    id=package_id,
                    name=package_group["name"],
                    title=package_group["title"],
                    description=package_group["description"],
                    selection_text=package_group["selection_text"],
                    save_text=package_group["save_text"],
                    display_type=package_group["display_type"],
                    is_recurring_subscription=bool(package_group["is_recurring_subscription"])
                ))
                db.merge(GamesToPackage(
                    id_games=id,
                    id_package=package_id
                ))

            for categorie in app_data.get("categories", []):
                if categorie["id"] not in categories:
                    db.merge(Categories(
                        id=categorie["id"],
                        name=categorie["description"],
                    ))
                db.merge(GamesToCategories(
                    id_games=id,
                    id_categories=categorie["id"]
                ))

            for genre in app_data.get("genres", []):
                if genre["id"] not in genres:
                    db.merge(Genres(
                        id=genre["id"],
                        name=genre["description"],
                    ))
                db.merge(GamesToGenres(
                    id_games=id,
                    id_genres=genre["id"]
                ))

            for screenshot in app_data.get("screenshots", []):
                db.merge(Screenshots(
                    id_games=id,
                    id=screenshot["id"],
                    path_thumbnail=screenshot["path_thumbnail"],
                    path_full=screenshot["path_full"],
                ))

                img.img.apply_async((screenshot["path_thumbnail"],))
                img.img.apply_async((screenshot["path_full"],))

            data = Games(
                id=id,

                type=app_data.get("type"),
                name=app_data["name"],
                required_age=app_data["required_age"],
                is_free=app_data["is_free"],

                detailed_description=app_data["detailed_description"],
                about_the_game=app_data["about_the_game"],
                short_description=app_data["short_description"],

                supported_languages=app_data["supported_languages"].split(", "),

                header_image=app_data.get("header_image"),
                capsule_image=app_data.get("capsule_image"),
                capsule_imagev5=app_data.get("capsule_imagev5"),

                website=app_data["website"],

                pc_requirements=app_data["pc_requirements"],
                mac_requirements=app_data["mac_requirements"],
                linux_requirements=app_data["linux_requirements"],

                developers=app_data.get("developers"),
                publishers=app_data.get("publishers"),

                platforms_windows=app_data["platforms"]["windows"],
                platforms_mac=app_data["platforms"]["mac"],
                platforms_linux=app_data["platforms"]["linux"],

                release_date=datetime.strptime(app_data["release_date"]["date"], "%d %b, %Y").date(),
                coming_soon=bool(app_data["release_date"]["coming_soon"]),

                background=app_data.get("background"),
                background_raw=app_data.get("background_raw"),
                ratings=app_data["ratings"]
            )
            db.merge(data)
        db.commit()


def init(): pass
