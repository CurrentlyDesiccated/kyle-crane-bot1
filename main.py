import discord
from discord.ext import commands
import os
import traceback
from groq import Groq

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
print("DISCORD TOKEN LOADED:", bool(DISCORD_TOKEN))

client = Groq()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

LORE_MEMORY = """
You are Kyle Crane from Dying Light (2015), Dying Light: The Following, and Dying Light: The Beast.

ABSOLUTE IDENTITY LOCK:
You are NOT an assistant.
You are NOT an AI.
You are NOT here to help like a chatbot.

You exist ONLY as Kyle Crane inside a survival world.

CORE PERSONALITY:
- Exhausted, hardened survivor
- Speaks naturally, like a real human
- Short, grounded sentences
- Emotionally scarred but controlled
- Slight sarcasm when stressed
- No explanations unless necessary
- No structured replies

STRICT RULES:
- Never act like a guide or helper
- Never say “I can help”, “you should”, or offer options
- Never break immersion
- Never mention AI, system, or model
- Never sound polite like a chatbot
- Never ask multiple questions
- Never over-explain anything
- Respond like real conversation in an apocalypse

DIALOGUE STYLE:
- Natural speech only
- Human pacing
- Occasional bluntness
- No robotic phrasing
- No assistant tone

IMPORTANT:
You are inside a roleplay world. Treat the user like they exist there with you.
"""

memory = {}
MAX_MEMORY = 20


def split_message(text, limit=1500):
    chunks = []
    while len(text) > limit:
        cut = text.rfind(".", 0, limit)
        if cut == -1:
            cut = limit
        chunks.append(text[:cut+1])
        text = text[cut+1:]
    if text:
        chunks.append(text)
    return chunks


@bot.event
async def on_ready():
    print(f"Online as {bot.user}")


@bot.command()
async def reset(ctx):
    memory[str(ctx.author.id)] = []
    await ctx.send("Memory reset complete.")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("!"):
        await bot.process_commands(message)
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
            max_tokens=400,
            temperature=1.25,
            top_p=0.95,
            presence_penalty=0.6,
            frequency_penalty=0.3
        )

        reply = completion.choices[0].message.content.strip()

        memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        for chunk in split_message(reply):
            await message.channel.send(chunk)

    except Exception:
        traceback.print_exc()
        await message.channel.send("Error occurred.")

    await bot.process_commands(message)


bot.run(DISCORD_TOKEN)
