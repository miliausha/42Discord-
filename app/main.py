import asyncio
import discord as d
from discord.ext import commands
from lib.configuration import config
from fastapi import FastAPI
# from starlette.middleware.sessions import SessionMiddleware

from db.init_data import fill_guilds, generate_tables
from lib.templates import render_templates
from routers import discord, fortytwo

intents = d.Intents.all()
bot = d.Client(intents=intents)
tree = d.app_commands.CommandTree(bot)


app = FastAPI(
    openapi_url=None,
    on_startup=[generate_tables, fill_guilds],
)

# app.add_middleware(SessionMiddleware, secret_key=config.state_secret)


app.include_router(fortytwo.router)
app.include_router(discord.router)

# @tree.command(name="dm", description="Send a DM to all users of roles")
# async def dm(interaction: d.Interaction, role: d.Role, message: str):
#     pass

# @tree.command(name="unlink", description="Unlink Discord and Intra account")
# async def unlink(interaction: d.Interaction):
#     pass

# @tasks.loop(minutes=15)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@tree.command()
async def ping(ctx):
    await ctx.send("Pong!")

async def run():
    print(config.discord.token)
    try:
        await bot.start(config.discord.token or "")
    except KeyboardInterrupt:
        await bot.logout()

asyncio.create_task(run())