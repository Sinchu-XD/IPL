import asyncio
import requests
from pyrofork import Client
from pyrogram.types import Message

# ✅ Telegram API Credentials
API_ID = 25024171  # Get from my.telegram.org
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7726535663:AAGalIgbZaBHRGhbAc0fdWmSithGcRjdEzg"

# ✅ CricAPI Credentials
CRIC_API_KEY = "9a7a66e7-f1d5-4899-ad9f-21a1a172f58e"
MATCHES_API = f"https://api.cricapi.com/v1/currentMatches?apikey={CRIC_API_KEY}"

# ✅ Set your target Telegram chat ID
TARGET_CHAT_ID = -1002209504301  # Replace with your Telegram group/channel ID

# ✅ Start PyroFork Client
app = Client("IPLBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ Store last update to prevent duplicate messages
last_ball = None  

async def get_live_match():
    """Fetches live IPL matches and returns match details."""
    try:
        response = requests.get(MATCHES_API)
        data = response.json()

        if "data" not in data or not data["data"]:
            return None, "⚠️ No match data available!"

        for match in data["data"]:
            if "Indian Premier League" in match.get("name", ""):
                return match, None  # ✅ Found IPL match

        return None, "❌ No live IPL matches found!"
    except Exception as e:
        return None, f"🚨 API Error: {str(e)}"

async def send_live_updates():
    """Continuously fetches and sends ball-by-ball updates."""
    global last_ball
    while True:
        match, error = await get_live_match()
        
        if error:
            print(error)  # ✅ Log errors
            await asyncio.sleep(30)  # Retry in 30s
            continue

        # ✅ Get match details
        match_id = match["id"]
        match_name = match["name"]
        live_api = f"https://api.cricapi.com/v1/match_info?apikey={CRIC_API_KEY}&id={match_id}"

        try:
            response = requests.get(live_api)
            data = response.json()

            if "data" not in data or "score" not in data["data"]:
                print("⚠️ No live score available!")
                await asyncio.sleep(30)
                continue
            
            score = data["data"]["score"]
            commentary = data["data"].get("commentary", [])
            
            if not commentary:
                print("⚠️ No live commentary found!")
                await asyncio.sleep(30)
                continue

            # ✅ Get the latest ball update
            latest_ball = commentary[0]

            # ✅ Prevent duplicate messages
            if latest_ball == last_ball:
                await asyncio.sleep(10)
                continue

            last_ball = latest_ball  # ✅ Update last ball

            # ✅ Prepare message
            message = f"🏏 **{match_name}**\n\n"
            message += f"📊 **Score:** {score}\n\n"
            message += f"🎙️ **Last Ball:** {latest_ball}"

            # ✅ Send update to Telegram
            await app.send_message(TARGET_CHAT_ID, message)
            print("✅ Update sent!")

        except Exception as e:
            print(f"🚨 Error fetching match info: {e}")

        await asyncio.sleep(10)  # ✅ Check every 10 seconds

@app.on_message(filters.command("start"))
async def start_bot(client, message: Message):
    """Starts the bot and live updates."""
    await message.reply("✅ **IPL Bot is running!** Fetching live updates...")
    await send_live_updates()

if __name__ == "__main__":
    print("🚀 Starting IPL Live Score Bot...")
    asyncio.run(send_live_updates())  # ✅ Run the auto-update function
