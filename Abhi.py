import asyncio
import requests
from pyrogram import Client, filters, idle
from pyrogram.types import Message

# 🚀 Replace with your own API credentials
API_KEY = "814d366d83msh97b8ba89155c2a8p140352jsn4c9a3b3bb565"
API_URL = f"https://api.cricapi.com/v1/currentMatches?apikey={API_KEY}"

# 🏏 Telegram Bot Credentials
API_ID = 25024171  # Get from my.telegram.org
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7726535663:AAFI5nfBVIOJF_34ZDfe0zHQyViGDGLkP5A"

# 📲 Start Bot
app = Client("Abhi", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 📡 Function to fetch live match updates
async def fetch_ipl_score():
    try:
        response = requests.get(API_URL)
        data = response.json()

        # Debugging: Print API response
        print("API Response:", data)

        if "data" not in data or not data["data"]:
            return "❌ No live IPL matches found!"

        for match in data["data"]:
            if "Indian Premier League" in match.get("name", ""):
                teams = f"🏏 {match['teams'][0]} 🆚 {match['teams'][1]}"
                status = match.get("status", "Live")
                score = ""

                if "score" in match and match["score"]:
                    for innings in match["score"]:
                        score += f"📊 **{innings['inning']}**: {innings['runs']}/{innings['wickets']} in {innings['overs']} overs\n"

                return f"🏏 **LIVE IPL MATCH**\n📢 {teams}\n📊 {status}\n{score}"

        return "❌ No live IPL matches found!"

    except Exception as e:
        return f"⚠️ Error fetching score: {e}"

# 🔄 Function to send automatic updates
async def send_live_updates():
    chat_id = -1002209504301  # Replace with your group/channel ID
    last_message = ""

    while True:
        score_update = await fetch_ipl_score()

        if score_update != last_message:
            await app.send_message(chat_id, score_update)
            last_message = score_update

        await asyncio.sleep(30)  # ⏳ Check every 30 seconds

# 🎯 Start Command (for manual check)
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("🏏 **IPL Live Score Bot Started!**\nI will update scores automatically.")

# 🎯 Manual Score Check
@app.on_message(filters.command("score"))
async def score(client, message: Message):
    score_update = await fetch_ipl_score()
    await message.reply(score_update)

# 🚀 Main Function
async def main():
    print("🏏 IPL Bot is running...")
    await app.start()
    asyncio.create_task(send_live_updates())  # Start auto-updates
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
    
