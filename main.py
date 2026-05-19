import discord
from discord.ext import commands
import os
from openai import OpenAI

# 🔍 DEBUG: check if Railway is giving the token
print("TOKEN =", os.getenv("DISCORD_TOKEN"))

# Load OpenAI client
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Discord setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🧟 Kyle Crane personality
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
        response = client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ]
        )

        reply = response.choices[0].message.content
        await ctx.send(f"🧟 Kyle Crane: {reply}")

    except Exception as e:
        await ctx.send("Something went wrong in the field...")
        print(e)

bot.run(os.getenv("DISCORD_TOKEN"))
