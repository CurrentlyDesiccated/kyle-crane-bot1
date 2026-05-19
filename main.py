import discord
from discord.ext import commands
import os
from openai import OpenAI

# 🔍 DEBUG: check Railway variables
print("DISCORD TOKEN =", os.getenv("DISCORD_TOKEN"))
print("OPENAI KEY =", os.getenv("OPENAI_API_KEY"))

# OpenAI client
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        print("USER MESSAGE:", message)

        response = client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ]
        )

        reply = response.choices[0].message.content

        # safety trim (prevents Discord embed/message issues later)
        reply = str(reply)[:1900]

        await ctx.send(f"🧟 Kyle Crane: {reply}")

    except Exception as e:
        print("OPENAI ERROR:", e)
        await ctx.send(f"⚠️ Error in field: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))
