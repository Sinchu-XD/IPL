import asyncio
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters, idle
from pyrogram.types import Message

# 🔹 Your Telegram Bot Credentials
API_ID = 25024171  # Get this from https://my.telegram.org
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7726535663:AAGalIgbZaBHRGhbAc0fdWmSithGcRjdEzg"

# 🔹 Cricbuzz URL for live match data
CRICBUZZ_URL = "https://www.cricbuzz.com/cricket-match/live-scores"

# 🔹 Channel/Group ID where updates will be sent
CHAT_ID = -1002209504301  # Replace with your Group/Channel ID

# 🔹 Initialize Pyrogram Client
app = Client("IPLBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# 📡 Function to fetch live match details from Cricbuzz
async def fetch_live_ipl_score():
    try:
        response = requests.get(CRICBUZZ_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        matches = soup.find_all(class_="cb-col cb-col-100 cb-lv-main")
        live_matches = []

        for match in matches:
            match_info = match.find(class_="cb-lv-scrs-well cb-lv-scrs-well-live")
            if match_info:
                title = match_info["title"]
                score = match_info.text.strip()
                link = match.find("a")["href"]
                full_link = f"https://www.cricbuzz.com{link}"

                live_matches.append(f"🏏 **{title}**\n📊 {score}\n🔗 [More Info]({full_link})")

        if not live_matches:
            return "❌ No live IPL matches found!"

        return "\n\n".join(live_matches)

    except Exception as e:
        return f"⚠️ Error fetching score: {e}"


# 📡 Function to send automatic updates every 30 seconds
async def send_live_updates():
    last_message = ""

    while True:
        score_update = await fetch_live_ipl_score()

        if score_update != last_message:
            await app.send_message(CHAT_ID, score_update, disable_web_page_preview=True)
            last_message = score_update

        await asyncio.sleep(30)  # 🔄 Update every 30 seconds


# 🎯 Command to manually check scores
@app.on_message(filters.command("score"))
async def score(client, message: Message):
    score_update = await fetch_live_ipl_score()
    await message.reply(score_update, disable_web_page_preview=True)


# 🎯 Start Command
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("🏏 **IPL Live Score Bot Started!**\nI will update scores automatically.")


# 🚀 Main Function to Start the Bot
async def main():
    print("🏏 IPL Bot is running...")
    await app.start()
    asyncio.create_task(send_live_updates())  # Start auto-updates
    await idle()


if __name__ == "__main__":
    asyncio.run(main())
    
