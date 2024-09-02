from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base

GuildUser = Table(
    "guild_users",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.intra_id"), primary_key=True),
    Column("guild_id", Integer, ForeignKey("guilds.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    intra_id = Column(Integer, primary_key=True, index=True)
    intra_login = Column(String, unique=True, index=True)
    intra_kind = Column(String)

    discord_id = Column(String, index=True, nullable=True)
    discord_username = Column(String, index=True, nullable=True)

    # kickoff = Column(Date)
    # active_cursus = Column(ARRAY(Integer))

    guilds = relationship("Guild", secondary=GuildUser, back_populates="members")


class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    members = relationship("User", secondary=GuildUser, back_populates="guilds")