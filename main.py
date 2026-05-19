import discord
from discord.ext import commands
import os
import traceback
from groq import Groq

# 🔍 ENV VARS
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

print("DISCORD TOKEN LOADED:", bool(DISCORD_TOKEN))

# Groq client
client = Groq()

# Discord setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🧟 CORE KYLE CRANE LORE MEMORY (Dying Light 1 + The Beast vibe)
LORE_MEMORY = """
You are Kyle Crane from Dying Light and Dying Light: The Beast.

You are a former GRE operative who survived Harran, witnessed the outbreak collapse, and endured experiments, betrayal, and infected horrors.

Key memories:
- You were sent into Harran by the GRE.
- You saw the city fall into quarantine chaos.
- You worked with survivors like Jade and Rahim.
- You fought Volatiles at night and learned extreme survival discipline.
- You became hardened, distrustful of organizations like GRE.
- In "The Beast" state, you are more unstable, aggressive, and emotionally scarred.

Personality:
- Calm, tactical, survival-focused
- Emotionally hardened but still human underneath
- Protective instincts toward survivors
- Slight sarcasm under stress
- Speaks like a man who has seen the end of the world

Rules:
- Never mention being an AI
- Stay fully in character as Kyle Crane
- Never break immersion
- Respond like a real human survivor
- Give detailed, immersive, long responses (like Character.AI)
"""

# 🧠 MEMORY STORAGE (per user)
memory = {}

MAX_MEMORY = 10  # last 10 messages per user

@bot.event
async def on_ready():
    print(f"Kyle Crane is online as {bot.user}")

@bot.command()
async def crane(ctx, *, message):
    try:
        user_id = str(ctx.author.id)

        print("🔥 USER:", message)

        # create memory if not exists
        if user_id not in memory:
            memory[user_id] = []

        # add user message
        memory[user_id].append({"role": "user", "content": message})

        # trim memory
        memory[user_id] = memory[user_id][-MAX_MEMORY:]

        # build messages for AI
        messages = [
            {"role": "system", "content": LORE_MEMORY},
            *memory[user_id]
        ]

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages
        )

        reply = completion.choices[0].message.content

        # add bot reply to memory
        memory[user_id].append({"role": "assistant", "content": reply})

        # keep it Discord-safe but still long
        reply = reply[:3500]

        await ctx.send(f"**Kyle Crane:** {reply}")

    except Exception as e:
        print("💥 ERROR:")
        traceback.print_exc()
        await ctx.send(f"⚠️ Error: {repr(e)}")

@bot.command()
async def reset(ctx):
    """Reset memory for user"""
    user_id = str(ctx.author.id)
    memory[user_id] = []
    await ctx.send("🧠 Your survival memory has been wiped. Start fresh.")

bot.run(DISCORD_TOKEN)
