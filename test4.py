import logging
from urllib.parse import urlparse

import uvicorn
from minio import S3Error

import config
import incelization
from db.session import Session
from db.steam.developer import Developer
from db.steam.games import Games
from db.steam.games_to_developer import GamesToDeveloper
from db.steam.games_to_publisher import GamesToPublisher
from db.steam.publisher import Publisher
from db.steam.screenshots import Screenshots
from db.steam.user_games import UserGames
from task.steam import img
from task.steam.games import games, scheduler_games, get_reviews
from task.steam.user import user
from task.steam_virtual_user.user_games import scheduler_user_games
from tqdm import tqdm

# Initialization
incelization.init()

app = config.APP

logging.basicConfig(level=logging.INFO)


def file_exists(key):
    try:
        config.MINIO.stat_object(config.MINIO_BUCKET_NAME, key)
        return True
    except S3Error as e:
        if e.code == "NoSuchKey":
            return False
        raise  # другая ошибка


with config.DB.get_db_session() as db:
    db: Session
    c = 0

    developersinss = {i.name: i for i in db.query(Developer).all()}
    publishersss = {i.name: i for i in db.query(Publisher).all()}

    gs = db.query(Games.id, Games.developers, Games.publishers).all()
    for id, developersin, publishers in tqdm(gs):

        if developersin:
            for developer_name in set(developersin):
                if developersinss.get(developer_name) is None:
                    developer = db.query(Developer).filter(Developer.name == developer_name).first()

                    if not developer:
                        developer = Developer(name=developer_name)
                        db.add(developer)
                        db.flush()
                    developersinss[developer_name] = developer
                else:
                    developer = developersinss.get(developer_name)

                db.merge(GamesToDeveloper(
                    id_games=id,
                    id_developer=developer.id
                ))

        if publishers:
            for publisher_neme in set(publishers):
                if publishersss.get(publisher_neme) is None:
                    publisher = db.query(Publisher).filter(Publisher.name == publisher_neme).first()

                    if not publisher:
                        publisher = Publisher(name=publisher_neme)
                        db.add(publisher)
                        db.flush()
                    publishersss[publisher_neme] = publisher
                else:
                    publisher = publishersss.get(publisher_neme)

                db.merge(GamesToPublisher(
                    id_games=id,
                    id_publisher=publisher.id
                ))

    db.commit()
