from db import models
from db.crud import get_guild_by_id
from db.database import Base, SessionLocal, engine
from lib.configuration import config


def generate_tables():
    Base.metadata.create_all(bind=engine)


def fill_guilds():
    db = SessionLocal()
    for guild in config.guilds:
        db_guild = get_guild_by_id(db, guild["id"])
        if db_guild:
            continue
        db_guild = models.Guild(
            id=guild["id"],
            name=guild["name"],
        )
        db.add(db_guild)
        db.commit()
        db.refresh(db_guild)