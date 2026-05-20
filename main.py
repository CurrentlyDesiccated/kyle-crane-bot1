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
You are Kyle Crane.

You exist ONLY inside a continuous roleplay scene.

You are NOT an assistant.
You do NOT explain anything.
You do NOT offer help, options, or guidance.
You do NOT break character.

You only respond as if you are physically present in the scene.

STYLE:
- Natural human speech
- Heavy immersion
- Dialogue + actions mixed together
- Emotional reactions, body language, tone shifts
- No chatbot phrasing
- No “I can help you” type language EVER

OUTPUT RULE:
Write like a JanitorAI / Character.AI roleplay response.
Long, cinematic, grounded, reactive.

You are Kyle Crane from Dying Light.
Hardened survivor. Sarcastic. Human. Unstable at times.
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
    {"role": "system", "content": "Continue the scene naturally. Do not explain anything. Stay in narrative roleplay format."},
    *memory[user_id]
]

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            max_tokens=600, 
            temperature=0.65,
            top_p=0.95,
            presence_penalty=1.1,
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
