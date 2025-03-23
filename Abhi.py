import requests
import asyncio
from pyrogram import Client, filters

# ✅ Replace with your bot token & API key
BOT_TOKEN = "7726535663:AAGalIgbZaBHRGhbAc0fdWmSithGcRjdEzg"
CRICKET_API_KEY = 
CHAT_ID = -1002209504301  # ✅ Replace with your Group/Channel ID

# ✅ Initialize Pyrofork bot
app = Client("IPLBot", bot_token=BOT_TOKEN)

# ✅ Cricket API URLs (Modify as per your provider)
MATCHES_URL = f"https://api.cricapi.com/v1/currentMatches?apikey={CRICKET_API_KEY}&offset=0"
COMMENTARY_URL = "https://api.cricapi.com/v1/match_commentary?apikey={}&id={}"

previous_status = ""  # ✅ To prevent duplicate updates

async def get_live_ipl_score():
    """Fetches live IPL scores from API."""
    global previous_status
    try:
        response = requests.get(MATCHES_URL).json()
        if not response.get("data"):
            return "⚠️ No live IPL matches found!"

        match_data = ""
        for match in response["data"]:
            if "Indian Premier League" in match["name"]:  # ✅ Filter IPL Matches
                match_id = match["id"]
                team1 = match["teams"][0]
                team2 = match["teams"][1]
                status = match["status"]
                score = match.get("score", [])

                team1_score = f"{team1}: {score[0]['runs']}/{score[0]['wickets']} ({score[0]['overs']} overs)" if score else f"{team1}: Yet to bat"
                team2_score = f"{team2}: {score[1]['runs']}/{score[1]['wickets']} ({score[1]['overs']} overs)" if len(score) > 1 else f"{team2}: Yet to bat"

                commentary = await get_live_commentary(match_id)

                match_text = f"🏏 **{team1} vs {team2}**\n📊 {team1_score}\n📊 {team2_score}\n🔴 Status: {status}\n\n{commentary}"

                if match_text != previous_status:  # ✅ Prevents duplicate messages
                    previous_status = match_text
                    return match_text
                else:
                    return None  # ✅ No new updates, so don't send anything

        return None  # ✅ No live matches

    except Exception as e:
        return f"❌ Error fetching score: {e}"

async def get_live_commentary(match_id):
    """Fetches live commentary for a given match ID."""
    try:
        response = requests.get(COMMENTARY_URL.format(CRICKET_API_KEY, match_id)).json()
        if not response.get("data"):
            return "🔴 **No live commentary available.**"

        commentary_list = response["data"]["commentary"]
        latest_ball = commentary_list[0]["comment"] if commentary_list else "🎤 No latest ball update yet."

        return f"🎙 **Latest Ball:** {latest_ball}"

    except Exception as e:
        return f"❌ Error fetching commentary: {e}"

async def auto_send_scores():
    """Automatically sends IPL scores every minute in a specific chat."""
    while True:
        score_update = await get_live_ipl_score()
        if score_update:
            await app.send_message(CHAT_ID, score_update)
        await asyncio.sleep(60)  # ✅ Updates every 60 seconds

# ✅ Start bot
@app.on_message(filters.command("start"))
async def start(client, message):
    """Start message when bot is initiated."""
    await message.reply_text("🏏 **Welcome to IPL Live Score Bot!**\nThis bot sends live IPL updates automatically.")

# ✅ Run auto-updater in the background
async def main():
    await app.start()
    await asyncio.create_task(auto_send_scores())  # ✅ Auto-fetch scores & commentary
    await app.idle()

if __name__ == "__main__":
    asyncio.run(main())
