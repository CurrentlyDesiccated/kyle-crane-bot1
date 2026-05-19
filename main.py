import discord
from discord.ext import commands
import os
import traceback
from groq import Groq

# 🔍 ENV VARS
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("DISCORD TOKEN LOADED:", bool(DISCORD_TOKEN))
print("GROQ KEY LOADED:", bool(GROQ_API_KEY))

# Groq client (FREE AI)
client_ai = Groq(api_key=GROQ_API_KEY)

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
        print("🔥 USER:", message)

        response = client_ai.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message[:500]}
            ]
        )

        reply = response.choices[0].message.content[:1900]

        await ctx.send(f"🧟 Kyle Crane: {reply}")

    except Exception as e:
        print("💥 ERROR:")
        traceback.print_exc()

        await ctx.send(f"⚠️ Error: {repr(e)}")

bot.run(DISCORD_TOKEN)
