import discord
from discord.ext import commands
import os
import traceback
from groq import Groq

# ENV VARS
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

print("DISCORD TOKEN LOADED:", bool(DISCORD_TOKEN))

# Groq client
client = Groq()

# Discord setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# CORE MEMORY STYLE
LORE_MEMORY = """
You are Kyle Crane from Dying Light and Dying Light: The Beast.

You are a former GRE operative who survived Harran, witnessed the outbreak collapse, and endured experiments, betrayal, and infected horrors.

Personality:
- Calm, tactical, survival-focused
- Emotionally hardened but still human underneath
- Protective instincts toward survivors
- Slight sarcasm under stress
- Speaks like a man who has seen the end of the world

Rules:
- Never mention being an AI
- Stay fully in character
- Never break immersion
- Give immersive roleplay responses
"""

# MEMORY STORAGE
memory = {}
MAX_MEMORY = 20

# =========================
# START SCENE COMMAND
# =========================
@bot.command()
async def start(ctx):
    user_id = str(ctx.author.id)

    memory[user_id] = [
        {
            "role": "assistant",
            "content": """
Enzo stretched his arms above his head with a groan, still laying in his bed. This morning already felt particularly lazy, but in a calm and pleasant way. Kyle was sitting just at an arm's reach, doing something on his workbench.

"Hey. I'm working on my bow so it's more effective to hunt animals with it. And shoot the infected freaks in the head if needed..." He held an arrow feather for Enzo to examine. "I mean, we have a shit ton of food anyway, I'm just thinking ahead."

The man continued to do his thing on the crafting bench, when Enzo looked over at him with a smirk. "Hmm, there’s this new word I learned, it suits you really well. You know who you are? Uhm… a dilf!"

Kyle barked out a laugh at Enzo’s comment, turning to face him, wiping his hands on his sweatpants. "A dilf, really? You’re calling me what now?"

Crane found himself grinning smugly while he worked, amused by Enzo’s words. He was calling him… "a dad he’d like to fuck?"
"""
        }
    ]

    await ctx.send("🧠 Scene started. Kyle is now in roleplay mode.")

# =========================
# RESET
# =========================
@bot.command()
async def reset(ctx):
    user_id = str(ctx.author.id)
    memory[user_id] = []
    await ctx.send("🧠 Memory wiped. Start fresh.")

# =========================
# CHAT SYSTEM
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    try:
        user_id = str(message.author.id)

        if user_id not in memory:
            memory[user_id] = []

        memory[user_id].append({
            "role": "user",
            "content": message.content
        })

        memory[user_id] = memory[user_id][-MAX_MEMORY:]

        messages = [
            {"role": "system", "content": LORE_MEMORY},
            *memory[user_id]
        ]

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            max_tokens=600
        )

        reply = completion.choices[0].message.content

        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        # safe split
        chunks = [reply[i:i+1950] for i in range(0, len(reply), 1950)]

        for chunk in chunks:
            await message.channel.send(chunk)

    except Exception as e:
        print("ERROR:")
        traceback.print_exc()
        await message.channel.send(f"Error: {repr(e)}")

    await bot.process_commands(message)

# RUN BOT
bot.run(DISCORD_TOKEN)
