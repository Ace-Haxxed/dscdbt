import discord
import requests
import random
from keep_alive import keep_alive

keep_alive()

DISCORD_TOKEN = ""
OR_API_KEY = "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"
OR_API_URL = "https://openrouter.ai/api/v1/chat/completions"

SASSY_REMARKS = [
    "Oh really? That's what you're going with? Bold.",
    "I mean... if you say so.",
    "You must be fun at parties.",
    "Well aren't you just a ray of confusing sunshine.",
    "Wow. Such intellect. I'm quaking.",
    "If brains were dynamite, you wouldn’t have enough to blow your nose.",
    "Tell me more, oh wise one of questionable wisdom.",
    "You're a walking Wi-Fi dead zone of thoughts.",
    "I've met potatoes with more purpose.",
    "You're like a software update at 2am—nobody asked for this."
]

persona = "mean"

def format_reply(answer, persona="mean"):
    if persona == "nice":
        return answer.strip()
    else:
        if random.random() < 0.3:
            sassy_comment = random.choice(SASSY_REMARKS)
            return f"{sassy_comment}\n\n{answer.strip()}"
        else:
            return answer.strip()

def get_reply(prompt):
    global persona

    if any(word in prompt.lower() for word in ["thee", "thou", "thy"]):
        return "Verily, thou art more tangled than mine own charging cables. Begone with thy nonsense."

    if "roast me" in prompt.lower():
        roasts = [
            "You're like a cloud. When you disappear, it's a beautiful day.",
            "You're proof that evolution can go in reverse.",
            "You're not stupid; you just have bad luck thinking.",
            "You're like a null pointer—empty and crashing everything.",
            "You're so ugly, when you cry, the tears roll down the back of your head—it's a sad sight.",
            "You're so old, your birth-certificate expired.",
            "You're so old, you fart dust.",
            "You're like mustafa, a person who is a complete waste of space but can destroy America in a jump."
        ]
        return f"No need to say it because your parents would want to but since you asked: {random.choice(roasts)}"

    headers = {
        "Authorization": f"Bearer {OR_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are sarcastic and mean when persona is 'mean', and super nice and helpful when it's 'nice'."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(OR_API_URL, headers=headers, json=payload)
        data = response.json()

        if "choices" in data and data["choices"]:
            answer = data["choices"][0]["message"]["content"]
            return format_reply(answer, persona)
        elif "error" in data:
            return f"Error (OpenRouter): {data['error'].get('message', 'Unknown error')}"
        else:
            return "Unexpected response from OpenRouter."

    except Exception as e:
        return f"Error: {e}"

intents = discord.Intents.all()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    global persona

    # Ignore messages from itself, but respond to others
    if message.author.id == bot.user.id:
        return

    prompt = message.content.strip()
    if not prompt:
        return

    if prompt.lower() == "?switch_persona":
        persona = "nice" if persona == "mean" else "mean"
        await message.channel.send(f"'{persona}' ")
        return

    await message.channel.typing()
    reply = get_reply(prompt)

    # Add a ping to the reply (mention the user who sent the message)
    reply_with_ping = f"<@{message.author.id}> {reply}"

    if len(reply_with_ping) > 2000:
        chunks = [reply_with_ping[i:i+1900] for i in range(0, len(reply_with_ping), 1900)]
        for chunk in chunks:
            await message.channel.send(chunk)
    else:
        await message.channel.send(reply_with_ping)

bot.run(DISCORD_TOKEN)

