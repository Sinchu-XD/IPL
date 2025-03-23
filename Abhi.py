import asyncio
import logging
from pycricbuzz import Cricbuzz
from pyrogram import Client, filters
from pyrogram.types import Message

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Configuration
API_ID = 25024171  # Get from my.telegram.org
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7726535663:AAGalIgbZaBHRGhbAc0fdWmSithGcRjdEzg"

app = Client("IPLBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def refresh():
    c = Cricbuzz()
    match = c.matches()
    if not match:
        return None
    
    mid = match[0]['id']
    result = {
        'matches': match[0],
        'livescore': c.livescore(mid=mid),
        'scorecard': c.scorecard(mid=mid),
        'matchinfo': c.matchinfo(mid=mid),
        'commentary': c.commentary(mid=mid)
    }
    return result

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text("Welcome to Cricket Bot!\n\nUse /info to get match information\nUse /score to get the live score")

@app.on_message(filters.command("score"))
async def score(client: Client, message: Message):
    result = refresh()
    if not result:
        await message.reply_text("No live matches available.")
        return
    
    try:
        batsman1 = result['livescore']['batting']['batsman'][0]
        batsman2 = result['livescore']['batting']['batsman'][1]
        bowler = result['livescore']['bowling']['bowler'][0]
        scorecard = result['scorecard']['scorecard'][0]

        text = (f"Batting: {scorecard['batteam']}\n"
                f"Score: {scorecard['runs']}/{scorecard['wickets']}\n"
                f"Overs: {scorecard['overs']}\n"
                f"{batsman1['name']}: {batsman1['runs']} ({batsman1['balls']})\n"
                f"{batsman2['name']}: {batsman2['runs']} ({batsman2['balls']})\n\n"
                f"Bowling: {scorecard['bowlteam']}\n"
                f"{bowler['name']}: {bowler['wickets']}-{bowler['runs']} ({bowler['overs']})\n\n"
                f"Commentary: {result['commentary']['commentary'][0]['comm']}")

        await message.reply_text(text)
    except KeyError:
        await message.reply_text("Unable to fetch live scores at the moment.")

@app.on_message(filters.command("info"))
async def info(client: Client, message: Message):
    result = refresh()
    if not result:
        await message.reply_text("No match information available.")
        return
    
    match = result['matches']
    try:
        text = (f"Match No: {match['mnum']}\n"
                f"Match State: {match['mchstate']}\n"
                f"Match Status: {match['status']}\n"
                f"Toss: {match['toss']}\n"
                f"Location: {match['venue_location']}")
        await message.reply_text(text)
    except KeyError:
        await message.reply_text("Unable to fetch match details.")

# Start the bot
if __name__ == "__main__":
    app.run()
    
