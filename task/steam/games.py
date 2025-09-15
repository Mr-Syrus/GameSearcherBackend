from datetime import datetime
from typing import List
from urllib.parse import urlparse

import requests
from celery import Task
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
import json
import config
import my_requests
from db.steam.categories import Categories
from db.steam.developer import Developer
from db.steam.games import Games
from db.steam.games_to_categories import GamesToCategories
from db.steam.games_to_developer import GamesToDeveloper
from db.steam.games_to_genres import GamesToGenres
from db.steam.games_to_package import GamesToPackage
from db.steam.games_to_publisher import GamesToPublisher
from db.steam.genres import Genres
from db.steam.package import Package
from db.steam.publisher import Publisher
from db.steam.screenshots import Screenshots
from my_lib.queue import QueueEnum
from my_lib.split_list import split_list
from . import img


@config.CELERY_APP.task(bind=True, queue=QueueEnum.STEAM.value)
def scheduler_games(self: Task):
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = my_requests.get(url)
    data_list = response.json()
    for app in data_list["applist"]["apps"]:
        if "dlc" in app["name"].lower():
            print("scip:", app["appid"], app["name"])
            continue
        print(app["appid"], app["name"])
        games.apply_async((app["appid"],))


@config.CELERY_APP.task(bind=True, queue=QueueEnum.STEAM.value)
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

            for developer_name in app_data.get("developers", []):
                developer = db.query(Developer).filter(Developer.name == developer_name).first()

                if not developer:
                    developer = Developer(name=developer_name)
                    db.add(developer)
                    db.flush()

                db.merge(GamesToDeveloper(
                    id_games=id,
                    id_developer=developer.id
                ))

            for publisher_name in app_data.get("publishers", []):
                publisher = db.query(Publisher).filter(Publisher.name == publisher_name).first()

                if not publisher:
                    publisher = Publisher(name=publisher_name)
                    db.add(publisher)
                    db.flush()

                db.merge(GamesToPublisher(
                    id_games=id,
                    id_publisher=publisher.id
                ))

            for screenshot in app_data.get("screenshots", []):
                if screenshot.get("path_full") is None:
                    continue
                db.merge(Screenshots(
                    id_games=id,
                    id=screenshot["id"],

                    path_thumbnail=screenshot.get("path_thumbnail"),
                    path_full=screenshot.get("path_full"),

                    bucket_path_thumbnail=urlparse(screenshot.get("path_thumbnail")).path + ".webp" if app_data.get("path_thumbnail") else None,
                    bucket_path_full=urlparse(screenshot.get("path_full")).path + ".webp",
                ))

                img.img.apply_async((screenshot["path_thumbnail"],))
                img.img.apply_async((screenshot["path_full"],))
            try:
                release_date = datetime.strptime(app_data["release_date"]["date"], "%d %b, %Y").date(),
            except:
                release_date = None
            data = Games(
                id=id,

                type=app_data.get("type"),
                name=app_data["name"],
                required_age=app_data["required_age"],
                is_free=app_data["is_free"],

                detailed_description=app_data["detailed_description"],
                about_the_game=app_data["about_the_game"],
                short_description=app_data["short_description"],

                supported_languages=app_data.get("supported_languages", "").split(", "),

                header_image=app_data.get("header_image"),
                capsule_image=app_data.get("capsule_image"),
                capsule_imagev5=app_data.get("capsule_imagev5"),

                bucket_header_image=urlparse(app_data.get("header_image")).path + ".webp",
                bucket_capsule_image=urlparse(app_data.get("capsule_image")).path + ".webp",
                bucket_capsule_imagev5=urlparse(app_data.get("capsule_imagev5")).path + ".webp",

                website=app_data["website"],

                pc_requirements=app_data["pc_requirements"],
                mac_requirements=app_data["mac_requirements"],
                linux_requirements=app_data["linux_requirements"],

                developers=app_data.get("developers"),
                publishers=app_data.get("publishers"),

                platforms_windows=app_data["platforms"]["windows"],
                platforms_mac=app_data["platforms"]["mac"],
                platforms_linux=app_data["platforms"]["linux"],

                release_date=release_date,
                coming_soon=bool(app_data["release_date"]["coming_soon"]),

                background=app_data.get("background"),
                background_raw=app_data.get("background_raw"),

                bucket_background=urlparse(app_data.get("background")).path + ".webp",
                bucket_background_raw=urlparse(app_data.get("background_raw")).path + ".webp",

                ratings=app_data["ratings"]
            )
            db.merge(data)
        db.commit()
    get_reviews(id)

@config.CELERY_APP.task(bind=True, queue=QueueEnum.STEAM.value)
def get_reviews(self: Task, id: int):
    r = requests.get(
        f"https://store.steampowered.com/appreviews/{id}",
        params={
            "json": 1,
            "filter": "all",
            "language": "all",
            "day_range": 9223372036854775807,  # все отзывы
            "review_type": "all",
            "purchase_type": "all",
            "num_per_page": 0,  # без загрузки отзывов, только статистика
        },
        headers={"User-Agent": "Mozilla/5.0"}
    )

    data = r.json()
    summary = data["query_summary"]

    total = summary["total_reviews"]
    positive = summary["total_positive"]
    negative = summary["total_negative"]
    score = (positive / total * 100) if total else 0

    with config.DB.get_db_session() as db:
        db: Session
        data = db.query(Games).filter(Games.id==id).first()
        data.total_reviews = total
        data.total_reviews_positive = positive
        data.total_reviews_negative = negative
        data.reviews_score = score
        db.commit()


def init(): pass
