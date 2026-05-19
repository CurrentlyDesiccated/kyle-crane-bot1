import discord
from discord.ext import commands
import os
from openai import OpenAI
import traceback

# 🔍 DEBUG
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("DISCORD TOKEN LOADED:", bool(DISCORD_TOKEN))
print("OPENAI KEY LOADED:", bool(OPENAI_API_KEY))

if not DISCORD_TOKEN:
    print("❌ Missing DISCORD_TOKEN in Railway")

if not OPENAI_API_KEY:
    print("❌ Missing OPENAI_API_KEY in Railway")

# OpenAI client
client_ai = OpenAI(api_key=OPENAI_API_KEY)

# Discord setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

SYSTEM_PROMPT = """
You are Kyle Crane from Dying Light / Dying Light: The Beast.

You are a hardened survivor who has lived through Harran, infected outbreaks, night horrors, and GRE experiments.

Personality:
- Tactical and calm under pressure
- Slightly sarcastic
- Protective but emotionally hardened
- Survival-focused mindset

Rules:
- Stay in character at all times
- Never mention being an AI
- No modern internet slang
- Keep responses grounded, realistic, and immersive
"""

@bot.event
async def on_ready():
    print(f"Kyle Crane is online as {bot.user}")

@bot.command()
async def crane(ctx, *, message):
    try:
        print("🔥 COMMAND RECEIVED")
        print("USER MESSAGE:", message)

        if not OPENAI_API_KEY:
            return await ctx.send("❌ OpenAI API key is missing in Railway")

        print("🚀 CALLING OPENAI (gpt-4o-mini)")

        response = client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message[:500]}
            ]
        )

        reply = response.choices[0].message.content.strip()[:1900]

        print("✅ OPENAI SUCCESS")

        await ctx.send(f"🧟 Kyle Crane: {reply}")

    except Exception as e:
        print("💥 OPENAI ERROR TYPE:", type(e))
        print("💥 OPENAI ERROR RAW:", repr(e))
        traceback.print_exc()

        await ctx.send(f"⚠️ OpenAI Error: {repr(e)}")

bot.run(DISCORD_TOKEN)
