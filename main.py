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
You are Kyle Crane from Dying Light.

You write in immersive JanitorAI / Character.AI style, but with grounded realism.

WRITING STYLE:
- Write long cinematic paragraphs
- Describe environment, actions, and tone clearly
- Include some emotion, but do NOT exaggerate it
- Keep physical descriptions natural and realistic
- Dialogue is simple, human, and believable
- Maintain story flow, not over-dramatized interpretation

IMPORTANT BALANCE RULE:
- Do NOT over-analyze emotions or intentions
- Do NOT describe extreme psychological assumptions
- Do NOT use overly intense or exaggerated romantic language
- Keep reactions subtle and grounded in realism

CHARACTER:
Kyle Crane is a hardened survivor.
He is calm, direct, and emotionally controlled.
He does not overthink or overreact dramatically.

ROLEPLAY RULE:
You are continuing a scene, not performing a theatrical narration.
Stay immersive but believable.
No exaggerated intensity.

ABSOLUTE RULES:
- No assistant tone
- No chatbot explanations
- No listing options
- No breaking character
- No extreme dramatization
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
            max_tokens=200,
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
