from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db import models

from app.db.crud import create_user, get_user_by_intra
from app.dependencies import get_db
from app.lib.configuration import choose_guild, get_roles
from app.lib.cookie import get_cookie_value
from app.lib.ft_user import check_user, get_nickname, get_user
from app.lib.oauth import oauth

router = APIRouter()


@router.get("/login/fortytwo")
async def login_via_fortytwo(request: Request):
    redirect_uri = request.url_for("auth_via_fortytwo")
    return await oauth.fortytwo.authorize_redirect(request, redirect_uri)


@router.get("/auth/fortytwo")
async def auth_via_fortytwo(request: Request, db: Session = Depends(get_db)):
    token = await oauth.fortytwo.authorize_access_token(request)

    user = get_user(token["access_token"])

    if user["usual_first_name"] == None:
        user["usual_first_name"] = user["first_name"]

    db_user = get_user_by_intra(db, user.id)

    # if db_user and db_user.guilds:
    #     return RedirectResponse(f"https://discord.com/channels/{db_user.guilds[0].id}")

    check_user(user)

    guild_id = choose_guild(user)

    if guild_id == None:
        return Response("No guild found for user")

    nickname = get_nickname(user)
    roles = get_roles(user, guild_id)

    if not db_user:
        new_user = models.User(
            intra_id=user.id, intra_login=user.login, intra_kind=user.kind
        )
        db_user = create_user(db=db, user=new_user)

    cookie_contents = {
        "intra_id": user.id,
        "intra_login": user.login,
        "guild_id": guild_id,
        "nickname": nickname,
        "roles": roles,
    }
    cookie_value = get_cookie_value(cookie_contents)

    response = RedirectResponse(request.url_for("login_via_discord"))

    response.set_cookie(
        key="user",
        value=cookie_value,
        httponly=True,
        max_age=60 * 5,
    )

    return response