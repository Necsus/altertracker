from datetime import datetime
import os
from aiohttp import web
import discord
from discord.ext import commands
import asyncio

from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Bot prêt : {bot.user}", flush=True)

async def assign_role(discord_id):
    guild = bot.get_guild(int(os.getenv("GUILD_ID")))
    member = guild.get_member(int(discord_id))
    role = guild.get_role(int(os.getenv("ROLE_ID")))
    if member and role:
        await member.add_roles(role)
        await member.send("Tu as reçu le rôle utilisateur.")

async def handle_test_message(request):
    data = await request.json()
    discord_id = data.get("discord_id")
    guild = bot.get_guild(int(os.getenv("GUILD_ID")))

    if not guild:
        print("[ERROR] Guild non trouvée", flush=True)
        return web.Response(status=500, text="Guild non trouvée")

    try:
        member = await guild.fetch_member(int(discord_id))  # ⬅️ force un appel API
        print(f"[INFO] Membre {member.display_name} récupéré", flush=True)
        embed_color = discord.Color.default()
        embed = discord.Embed(
            title="Ceci est un message de test",
            description="Si tu vois ce message, c'est que le bot fonctionne correctement.",
            color=embed_color,
        )
    
        embed.set_author(name=f"AlterTracker", icon_url="https://altertracker.com/favicon.ico")  # si tu as un logo en url
        embed.set_footer(text="Merci pour votre confiance • AlterTracker © 2025")
        embed.timestamp = discord.utils.utcnow()

        if member:
            await member.send(embed=embed)
        return web.Response(text="Alert sent")
    except discord.NotFound:
        return web.Response(status=404, text="Membre introuvable")
    except Exception as e:
        print(f"[ERROR] Erreur fetch_member : {e}", flush=True)
        return web.Response(status=500, text="Erreur lors de la récupération du membre")

async def handle_send_alert(request):
    data = await request.json()
    discord_id = data.get("discord_id")
    message = data.get("embed_message")
    guild = bot.get_guild(int(os.getenv("GUILD_ID")))

    if not guild:
        print("[ERROR] Guild non trouvée", flush=True)
        return web.Response(status=500, text="Guild non trouvée")

    try:
        member = await guild.fetch_member(int(discord_id))  # ⬅️ force un appel API
        print(f"[INFO] Membre {member.display_name} récupéré", flush=True)
        
        if message['changement_type'] == "added":
            embed_color = discord.Color.green()
        elif message['changement_type'] == "edited":
            embed_color = discord.Color.blue()
        elif message['changement_type'] == "expired":  # "expired" ou autre
            embed_color = discord.Color.red()
        else:
            embed_color = discord.Color.default()
    
        embed = discord.Embed(
            title="🔔 Un changement de prix a été appliqué à votre favoris",
            color=embed_color,
            timestamp=datetime.strptime(message['date_effective'], "%Y-%m-%d %H:%M:%S")  # adapte le format de date si besoin
        )
    
        embed.set_author(name=f"AlterTracker", icon_url="https://altertracker.com/favicon.ico")  # si tu as un logo en url
    
        # Description de bienvenue personnalisée
        embed.description = f"\nBonjour **{message['username']}**, \n\n" \
                            "Un changement de prix a été détecté sur une de vos cartes favorites associée à votre compte **AlterTracker**."
    
        # Champs détaillés
        embed.add_field(name="Nom", value=message['name_card'], inline=True)
        embed.add_field(name="Référence", value=message['reference'], inline=True)
        embed.add_field(name="Changement", value=message['changement_type'], inline=True)
        embed.add_field(name="Prix", value=message['price'], inline=True)
        embed.add_field(name="Date de détection", value=message['date_effective'], inline=True)
    
        # Image de la carte
        embed.set_image(url=message['url_image_card'])
    
        # Footer et timestamp
        embed.set_footer(text="Merci pour votre confiance • AlterTracker © 2025")
        embed.timestamp = discord.utils.utcnow()
    
        if member:
            await member.send(embed=embed)
            await member.send(f"👉 [Cliquez ici pour voir la carte]({message['lien_vers_alerts']})")
        return web.Response(text="Alert sent")
    except discord.NotFound:
        return web.Response(status=404, text="Membre introuvable")
    except Exception as e:
        print(f"[ERROR] Erreur fetch_member : {e}", flush=True)
        return web.Response(status=500, text="Erreur lors de la récupération du membre")
    
async def handle_send_alert_new_card(request):
    data = await request.json()
    discord_id = data.get("discord_id")
    message = data.get("embed_message")
    guild = bot.get_guild(int(os.getenv("GUILD_ID")))

    if not guild:
        print("[ERROR] Guild non trouvée", flush=True)
        return web.Response(status=500, text="Guild non trouvée")

    try:
        member = await guild.fetch_member(int(discord_id))  # ⬅️ force un appel API
        print(f"[INFO] Membre {member.display_name} récupéré", flush=True)
        
        embed_color = discord.Color.green()
    
        embed = discord.Embed(
            title="🔔 Une nouvelle carte est apparue dans une de vos recherche",
            color=embed_color,
            timestamp=datetime.strptime(message['date_effective'], "%Y-%m-%d %H:%M:%S")  # adapte le format de date si besoin
        )
    
        embed.set_author(name=f"AlterTracker", icon_url="https://altertracker.com/favicon.ico")  # si tu as un logo en url
    
        # Description de bienvenue personnalisée
        embed.description = f"\nBonjour **{message['username']}**, \n\n" \
                            f"Une nouvelle carte est apparue dans votre recherche : **{message['name_search']}** associée à votre compte **AlterTracker**."
    
        # Champs détaillés
        embed.add_field(name="Nom", value=message['name_card'], inline=True)
        embed.add_field(name="Référence", value=message['reference'], inline=True)
    
        # Image de la carte
        embed.set_image(url=message['url_image_card'])
    
        # Footer et timestamp
        embed.set_footer(text="Merci pour votre confiance • AlterTracker © 2025")
        embed.timestamp = discord.utils.utcnow()
    
        if member:
            await member.send(embed=embed)
            await member.send(f"👉 [Cliquez ici pour voir la carte]({message['lien_vers_alerts']})")
        return web.Response(text="Alert sent")
    except discord.NotFound:
        return web.Response(status=404, text="Membre introuvable")
    except Exception as e:
        print(f"[ERROR] Erreur fetch_member : {e}", flush=True)
        return web.Response(status=500, text="Erreur lors de la récupération du membre")

async def handle_send_chat(request):
    data = await request.json()
    discord_id = data.get("discord_id")
    message = data.get("embed_message")
    guild = bot.get_guild(int(os.getenv("GUILD_ID")))

    if not guild:
        print("[ERROR] Guild non trouvée", flush=True)
        return web.Response(status=500, text="Guild non trouvée")

    try:
        member = await guild.fetch_member(int(discord_id))  # ⬅️ force un appel API
        print(f"[INFO] Membre {member.display_name} récupéré", flush=True)
        embed = discord.Embed(
            title="🔔 Votre offre d'achat suscite de l'intêret",
            color=discord.Color.green()
        )
    
        embed.set_author(name=f"AlterTracker", icon_url="https://altertracker.com/favicon.ico")  # si tu as un logo en url
    
        # Description de bienvenue personnalisée
        embed.description = f"\nBonjour **{message['username']}**, \n\n" \
                            "Un vendeur souhaite discuter avec vous concernant votre offre d'achat sur **AlterTracker**."
    
        # Champs détaillés
        embed.add_field(name="Nom", value=message['name_card'], inline=True)
        embed.add_field(name="Référence", value=message['reference'], inline=True)
        embed.add_field(name="Prix", value=message['price'], inline=True)
        embed.add_field(name="Date de détection", value=message['date_effective'], inline=True)
    
        # Image de la carte
        embed.set_image(url=message['url_image_card'])
    
        # Footer et timestamp
        embed.set_footer(text="Merci pour votre confiance • AlterTracker © 2025")
        embed.timestamp = discord.utils.utcnow()
    
        if member:
            await member.send(embed=embed)
            await member.send(f"👉 [Cliquez ici pour accéder au chat]({message['lien_vers_chat']})")
        return web.Response(text="Alert sent")
    except discord.NotFound:
        return web.Response(status=404, text="Membre introuvable")
    except Exception as e:
        print(f"[ERROR] Erreur fetch_member : {e}", flush=True)
        return web.Response(status=500, text="Erreur lors de la récupération du membre")


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
    app.router.add_post("/testmessage", handle_test_message)
    app.router.add_post("/sendalert", handle_send_alert)
    app.router.add_post("/sendalertnewcard", handle_send_alert_new_card)
    app.router.add_post("/sendchat", handle_send_chat)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

# Lancer discord bot + serveur web
async def main():
    await start_web()
    await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

asyncio.run(main())
