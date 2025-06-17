import os
from aiohttp import web
import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Bot prêt : {bot.user}")

async def assign_role(discord_id):
    guild = bot.get_guild(int(os.getenv("GUILD_ID")))
    member = guild.get_member(int(discord_id))
    role = guild.get_role(int(os.getenv("ROLE_ID")))
    if member and role:
        await member.add_roles(role)
        await member.send("Tu as reçu le rôle utilisateur.")

# API pour recevoir l’appel depuis Flask
async def handle_assign(request):
    data = await request.json()
    discord_id = data.get("discord_id")
    asyncio.create_task(assign_role(discord_id))
    return web.Response(text="OK")

# Lancer serveur HTTP
async def start_web():
    app = web.Application()
    app.router.add_post("/assign", handle_assign)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

# Lancer discord bot + serveur web
async def main():
    await start_web()
    await bot.start(os.getenv("DISCORD_TOKEN"))

asyncio.run(main())
