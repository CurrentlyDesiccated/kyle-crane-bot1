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

# 🧟 CORE KYLE CRANE LORE MEMORY
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

# 🧠 MEMORY STORAGE
memory = {}
MAX_MEMORY = 20

# =========================
# SAFE SPLITTER
# =========================
def split_message(text, limit=1950):
    chunks = []
    while len(text) > limit:
        cut = text.rfind(".", 0, limit)

        if cut == -1:
            cut = limit

        chunks.append(text[:cut+1].strip())
        text = text[cut+1:].strip()

    if text:
        chunks.append(text)

    return chunks

# =========================
# BOT READY
# =========================
@bot.event
async def on_ready():
    print(f"Kyle Crane is online as {bot.user}")

# =========================
# AUTO REPLY SYSTEM
# =========================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    try:
        user_id = str(message.author.id)

        print("🔥 USER:", message.content)

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
            max_tokens=600   # 🔥 THIS FIXES OVERLY LONG RESPONSES
        )

        reply = completion.choices[0].message.content

        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        # 💬 SAFE FULL RESPONSE
        chunks = split_message(reply)

        for chunk in chunks:
            await message.channel.send(chunk)

    except Exception as e:
        print("💥 ERROR:")
        traceback.print_exc()
        await message.channel.send(f"⚠️ Error: {repr(e)}")

    await bot.process_commands(message)

# =========================
# RESET COMMAND
# =========================
@bot.command()
async def reset(ctx):
    user_id = str(ctx.author.id)
    memory[user_id] = []
    await ctx.send("🧠 Your survival memory has been wiped. Start fresh.")

bot.run(DISCORD_TOKEN)
