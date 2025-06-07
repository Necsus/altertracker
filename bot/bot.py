import discord
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Charger les variables d'environnement depuis le fichier .env

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True
intents.guilds = True

client = discord.Client(intents=intents)

API_BASE_URL = os.getenv("API_BASE_URL")  # URL de votre API Flask

@client.event
async def on_ready():
    print(f"[✅] Bot connecté en tant que {client.user}")

@client.event
async def on_message(message):
    # On ignore les messages du bot lui-même
    if message.author == client.user:
        return

    # On écoute uniquement les messages privés (DM)
    if isinstance(message.channel, discord.DMChannel):
        print(f"[📥] DM reçu de {message.author.id}: {message.content}")

        # Prépare les données à envoyer au backend
        payload = {
            "sender_id": str(message.author.id),
            "content": message.content
        }

        try:
            res = requests.post(f"{API_BASE_URL}/api/chat/messages/from-discord", json=payload)
            if res.status_code == 201:
                await message.channel.send("✅ Message envoyé au serveur.")
            else:
                await message.channel.send("❌ Erreur serveur.")
        except Exception as e:
            await message.channel.send("❌ Erreur de connexion au backend.")
            print(f"[❌] Exception lors de l'envoi: {e}")

# Lancer le bot
client.run(os.getenv("DISCORD_BOT_TOKEN"))