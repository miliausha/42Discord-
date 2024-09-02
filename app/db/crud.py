from sqlalchemy.orm import Session, joinedload
from typing import Optional

from . import models, schemas


def get_user_by_intra(db: Session, intra_id: int) -> Optional[models.User]:
    return (
        db.query(models.User)
        .options(joinedload(models.User.guilds))
        .where(models.User.intra_id == intra_id)
        .first()
    )


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: models.User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: models.User):
    db.merge(user)
    db.commit()
    db.refresh(user)
    return user


def get_guild_by_id(db: Session, guild_id: int):
    return db.query(models.Guild).where(models.Guild.id == guild_id).first()


def get_guilds(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Guild).offset(skip).limit(limit).all()


def create_guild_user(db: Session, guild: models.Guild, user: models.User):
    guild.members.append(user)
    db.merge(guild)
    db.commit()