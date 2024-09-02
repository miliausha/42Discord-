from pydantic import BaseModel
from typing import List, Optional


class UserBase(BaseModel):
    intra_id: int
    intra_login: str
    intra_kind: str
    discord_id: Optional[int]
    discord_username: Optional[str]

    class Config:
        from_attributes = True


class GuildBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class User(UserBase):
    guilds: List[GuildBase]


class Guild(GuildBase):
    members: List[UserBase]