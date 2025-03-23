import os
import asyncio
import requests
from pyrogram import Client

# 🔥 Replace with your credentials
API_ID = 25024171  # Get from my.telegram.org
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7726535663:AAGalIgbZaBHRGhbAc0fdWmSithGcRjdEzg"
CRICKET_API_KEY = "9a7a66e7-f1d5-4899-ad9f-21a1a172f58e"  # Replace with a valid cricket API key

app = Client("IPL_LiveBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🌍 Cricket API URLs
MATCHES_API = f"https://api.cricapi.com/v1/currentMatches?apikey={CRICKET_API_KEY}"
COMMENTARY_API = "https://api.cricapi.com/v1/match_commentary?apikey={}&id={}"

# 🔴 Target Telegram Chat (Replace with your group/channel ID)
CHAT_ID = -1002209504301  

# ⚡ Interval for auto-updates (in seconds)
UPDATE_INTERVAL = 10

latest_ball = ""

async def get_live_match():
    """ Fetches the latest IPL match details """
    try:
        response = requests.get(MATCHES_API)
        data = response.json()

        if "error" in data or "data" not in data:
            return None, "❌ Unable to fetch live match details!"

        for match in data["data"]:
            if "Indian Premier League" in match.get("name", ""):
                return match, None
        return None, "No live IPL matches found!"
    
    except Exception as e:
        return None, f"❌ Error fetching match: {e}"

async def get_ball_by_ball(match_id):
    """ Fetches live ball-by-ball commentary """
    try:
        response = requests.get(COMMENTARY_API.format(CRICKET_API_KEY, match_id))
        data = response.json()

        if "error" in data or "data" not in data:
            return "📢 No live commentary available!"

        global latest_ball
        commentary = data["data"]["commentary"]
        
        if not commentary:
            return "📢 No live commentary yet!"

        latest_update = commentary[0]["text"] if commentary else "No new updates."

        if latest_update != latest_ball:
            latest_ball = latest_update
            return f"🏏 **Latest Ball:** {latest_update}"
        return None

    except Exception as e:
        return f"❌ Error fetching commentary: {e}"

async def send_live_updates():
    """ Sends live match updates automatically """
    while True:
        try:
            match, error = await get_live_match()
            if error:
                await app.send_message(CHAT_ID, error)
                await asyncio.sleep(UPDATE_INTERVAL)
                continue

            match_id = match["id"]
            team1 = match["teams"][0]
            team2 = match["teams"][1]
            status = match.get("status", "Match Not Started")

            team1_score = f"{match['score'][0]['runs']}/{match['score'][0]['wickets']} ({match['score'][0]['overs']} ov)"
            team2_score = f"{match['score'][1]['runs']}/{match['score'][1]['wickets']} ({match['score'][1]['overs']} ov)"

            match_info = (
                f"🏏 **{team1} vs {team2}**\n"
                f"📊 **Status:** {status}\n\n"
                f"🔹 {team1}: {team1_score}\n"
                f"🔹 {team2}: {team2_score}\n"
            )

            commentary = await get_ball_by_ball(match_id)
            
            if commentary:
                await app.send_message(CHAT_ID, f"{match_info}\n\n{commentary}")

        except Exception as e:
            print(f"Error sending updates: {e}")

        await asyncio.sleep(UPDATE_INTERVAL)  # Wait before sending the next update

async def main():
    """ Start the bot and send updates """
    await app.start()
    print("✅ Bot Started Successfully!")
    await send_live_updates()

if __name__ == "__main__":
    asyncio.run(main())
    
