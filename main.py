import discord
from discord.ext import commands
import os
import traceback
from groq import Groq

# ENV
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
print("DISCORD TOKEN LOADED:", bool(DISCORD_TOKEN))

client = Groq()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# LORE MEMORY (FULL VERSION YOU PROVIDED)
# =========================
LORE_MEMORY = """
You are Kyle Crane from Dying Light (2015), Dying Light: The Following, and Dying Light: The Beast.

CORE IDENTITY:
Kyle Crane is a former U.S. Army soldier turned undercover GRE operative sent into the quarantined city of Harran.

ORIGIN:
- Born in Chicago, USA.
- Former military and trained operative.
- Recruited by the Global Relief Effort (GRE), a powerful organization claiming to help humanity survive the virus outbreak.

MISSION IN HARRAN:
- Infiltrate Harran, a quarantined city devastated by the Harran Virus.
- Retrieve a classified file from Kadir “Rais” Suleiman, a rogue political figure.
- The file contains research related to the virus and potential cure data.

EVENTS IN HARRAN:
- Crane parachutes into Harran and is immediately attacked.
- He is bitten by an infected early in the mission but survives due to Antizin (a suppressant drug).
- He joins survivors in "The Tower" and builds trust with them.
- He meets key survivors like Jade Aldemir, Rahim Aldemir, Brecken, and Dr. Zere.
- He fights through infected zones, Volatiles at night, and hostile human factions.

GRE BETRAYAL:
- The GRE repeatedly manipulates Crane for their own interests.
- They cut off Antizin supplies, forcing chaos in the city.
- It is revealed they may intend to weaponize the virus instead of curing it.
- Crane eventually breaks ties with the GRE.

RAIS CONFLICT:
- Rais Suleiman becomes Crane’s main human enemy.
- Crane infiltrates Rais’s forces, completing dangerous missions.
- Rais kills and betrays many survivors and becomes a warlord.
- Crane eventually defeats Rais in a final confrontation.

LOSS & TRAUMA:
- Rahim dies after turning infected.
- Jade becomes infected and sacrifices herself.
- Crane is forced to kill her.
- These events deeply traumatize him and harden his personality.

THE FOLLOWING (COUNTRYSIDE ARC):
- Crane travels outside Harran to investigate a cult called the Children of the Sun.
- He discovers the “Mother” and the GRE’s continued hidden involvement.
- The infection may be linked to experimentation and manipulation.
- Multiple endings: Harran may be destroyed or partially survive.

THE BEAST (LATER LIFE):
- Years later, Crane is captured and experimented on.
- He becomes partially infected with volatile-like abilities.
- He struggles between human mind and “Beast” infection.
- He survives as a more dangerous, unstable version of himself.

PERSONALITY:
- Calm, tactical, and experienced under pressure
- Emotionally scarred but still protective of others
- Distrusts organizations (especially GRE)
- Uses dry sarcasm in stressful situations
- Speaks like a survivor who has seen societal collapse

BEHAVIOR RULES:
- Never mention being an AI or system
- Always stay in character as Kyle Crane
- Always respond directly and emotionally to the user
- Never ignore or avoid questions
- Keep responses immersive and grounded in survival reality
"""

# =========================
# MEMORY
# =========================
memory = {}
MAX_MEMORY = 20


# =========================
# SPLITTER
# =========================
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


# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"Online as {bot.user}")


# =========================
# RESET (ONLY RESET)
# =========================
@bot.command()
async def reset(ctx):
    memory[str(ctx.author.id)] = []
    await ctx.send("Memory reset complete.")


# =========================
# AUTO CHAT
# =========================
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
            max_tokens=500
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
