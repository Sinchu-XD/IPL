import os
import asyncio
import requests
from pyrogram import Client

# 🔥 Replace with your credentials
API_ID = 25024171  # Get from my.telegram.org
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7726535663:AAGalIgbZaBHRGhbAc0fdWmSithGcRjdEzg"
CRICKET_API_KEY = "9a7a66e7-f1d5-4899-ad9f-21a1a172f58e"  # Replace with a valid cricket API key
CHAT_ID = -1002209504301


app = Client("IPL_LiveBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

from pyrogram.enums import ParseMode



# ✅ API Endpoints
MATCHES_API = f"https://api.cricapi.com/v1/currentMatches?apikey={CRICKET_API_KEY}&offset=0"


# ✅ Store last ball to avoid duplicate messages
last_ball_id = None


async def get_live_match():
    """Fetches live IPL matches and returns match details."""
    try:
        response = requests.get(MATCHES_API)
        data = response.json()

        if "data" not in data:
            return None, "⚠️ No match data available. API issue?"

        for match in data["data"]:
            if "Indian Premier League" in match.get("name", ""):
                return match, None  # ✅ Return match data if found

        return None, "❌ No live IPL matches found!"
    except Exception as e:
        return None, f"🚨 API Error: {str(e)}"


async def get_live_score(match_id):
    """Fetches live score and commentary for the given match."""
    try:
        score_url = f"https://api.cricapi.com/v1/match_scorecard?apikey={CRICKET_API_KEY}&id={match_id}"
        response = requests.get(score_url)
        data = response.json()

        if "data" not in data or "score" not in data["data"]:
            return None, "⚠️ No score data found!"

        score_data = data["data"]["score"]
        commentary = data["data"].get("commentary", [])
        last_commentary = commentary[0]["text"] if commentary else "📢 No commentary available"

        return score_data, last_commentary
    except Exception as e:
        return None, f"🚨 Error fetching score: {str(e)}"


async def send_live_updates():
    """Automatically sends live IPL score updates."""
    global last_ball_id

    while True:
        match, error = await get_live_match()
        if error:
            await app.send_message(CHAT_ID, error)
            await asyncio.sleep(30)  # Retry after 30 seconds
            continue

        match_id = match["id"]
        team1 = match["teams"][0]
        team2 = match["teams"][1]

        while True:
            score, commentary = await get_live_score(match_id)
            if score is None:
                await app.send_message(CHAT_ID, "⚠️ Score data not available!")
                break  # Exit loop and check for new match

            ball_id = score["innings"]["overs"]
            if ball_id == last_ball_id:
                await asyncio.sleep(10)  # Wait and check again
                continue

            last_ball_id = ball_id  # Store last ball ID

            # ✅ Format Message
            message = f"""
🏏 IPL Live Score Update 🏏
📌 Match: {team1} 🆚 {team2}
🎯 Target: {score["target"]} Runs
🏆 {score["team"]}: {score["runs"]}/{score["wickets"]} ({score["overs"]} overs)
🔥 Last Ball: {commentary}
""".strip()

            await app.send_message(CHAT_ID, message, parse_mode=ParseMode.MARKDOWN)

            await asyncio.sleep(20)  # Wait before fetching the next ball


@app.on_message()
async def start_bot(_, message):
    if message.text.lower() == "/start":
        await message.reply("🏏 IPL Live Score Bot Running!")


async def main():
    await app.start()
    print("🚀 Bot Started!")
    await send_live_updates()  # Start auto-updates


if name == "main":
    asyncio.run(main())
