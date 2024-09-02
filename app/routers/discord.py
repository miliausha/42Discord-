from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.crud import (
    create_guild_user,
    get_guild_by_id,
    get_user_by_intra,
    update_user,
)
from app.dependencies import get_db
from app.lib.cookie import get_cookie_values
from app.lib.discord import get_guild_member, get_user, join_guild, update_guild_user
from app.lib.oauth import oauth
from app.lib.webhook import webhook_user
from app.lib.logs import logger

router = APIRouter()


@router.get("/login/discord")
async def login_via_discord(request: Request):
    redirect_uri = request.url_for("auth_via_discord")
    return await oauth.discord.authorize_redirect(request, redirect_uri)


@router.get("/auth/discord")
async def auth_via_discord(request: Request, db: Session = Depends(get_db)):
    token = await oauth.discord.authorize_access_token(request)

    cookie = get_cookie_values(request)
    db_user = get_user_by_intra(db, cookie.intra_id)
    discord_user = get_user(token["access_token"])

    if not db_user:
        return Response("No entry found for this Intra user")

    if db_user.discord_id and db_user.discord_id != discord_user.id:
        return Response("Different Discord user already linked to this Intra user")

    db_user.discord_id = discord_user.id
    db_user.discord_username = discord_user.username
    db_user = update_user(db, db_user)

    guild_member = get_guild_member(guild_id=cookie.guild_id, user_id=discord_user.id)

    logger.info(
        "GuildMember, status_code=%s, text=%s",
        guild_member.status_code,
        guild_member.text,
    )

    if guild_member.status_code == 404:
        status_code = join_guild(
            token["access_token"],
            cookie.guild_id,
            discord_user.id,
            cookie.nickname,
            cookie.roles,
        )

        # user has been added to the guild
        if status_code == 201:
            webhook_user(cookie, discord_user, "just joined", 16759896)

            db_guild = get_guild_by_id(db, cookie.guild_id)
            create_guild_user(db=db, guild=db_guild, user=db_user)
        # user was already in the guild
        elif status_code == 204:
            webhook_user(cookie, discord_user, "tried joining again", 5819135)
        # user was not added to the guild
        else:
            return Response("User could not be added to the guild")

    else:
        status_code = update_guild_user(
            cookie.guild_id,
            discord_user.id,
            cookie.nickname,
            cookie.roles,
        )

        if status_code == 204:
            webhook_user(
                cookie, discord_user, "joined again and refreshed info", 5819135
            )

    return RedirectResponse(f"https://discord.com/channels/{cookie.guild_id}")