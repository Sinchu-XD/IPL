import logging
import signal
import sys
import time
import requests
import asyncio
from pyrogram import Client, filters

# Configure logging
logging.basicConfig(level=logging.INFO)

# Your API credentials
API_ID = 25024171  # Get from my.telegram.org
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7726535663:AAFVBNgn5z-gUK7Tr7XoKTS3bopW3OLBSPM"
CHAT_ID = -4752836661

# Initialize Pyrogram Client
app = Client("cricket_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)

def wait_time(g_time):
    global interrupted
    for remaining in range(g_time, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
        if interrupted:
            print("Gotta go")
            break

def batsman_data(r):
    return [f"{b['player']['battingName']} {b['runs']}({b['balls']})" for b in r['supportInfo']['liveSummary'].get('batsmen', [])]

def bowler_data(r):
    return [f"{b['player']['battingName']} {b['overs']}-{b['maidens']}-{b['conceded']}-{b['wickets']}" for b in r['supportInfo']['liveSummary'].get('bowlers', [])]

try:
    response = requests.get("https://hs-consumer-api.espncricinfo.com/v1/pages/matches/current?latest=true", timeout=10)
    if response.status_code == 200 and response.text.strip():
        url = response.json()
        matches_detail = [[m['scribeId'], m['slug'], m['series']['objectId'], m['series']['slug']] for m in url.get('matches', []) if m.get('status') == 'Live']
    else:
        matches_detail = []
except requests.exceptions.RequestException as e:
    logging.error(f"Request failed: {e}")
    matches_detail = []

matches_detail_str = "\n".join([f"live{i+1} --> {m[1]}" for i, m in enumerate(matches_detail)])

@app.on_message(filters.command(["start", "help"]))
async def send_welcome(client, message):
    await message.reply_text("Hi, I am a Cricket Score Bot! I will update you with live scores.")
    if matches_detail:
        await message.reply_text(matches_detail_str)
    else:
        await message.reply_text("No Live coverage going on!! \n-----BYE----")

@app.on_message(filters.command("upcoming"))
async def upcoming_matches(client, message):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(
            "https://hs-consumer-api.espncricinfo.com/v1/pages/matches/current?latest=false",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200 and response.text.strip():
            data = response.json()
            upcoming_matches = [
                f"{m['series']['name']} - {m['teams'][0]['team']['name']} vs {m['teams'][1]['team']['name']}"
                for m in data.get('matches', []) if m.get('status') == 'Upcoming'
            ]
            
            if upcoming_matches:
                await message.reply_text("Upcoming Matches:\n" + "\n".join(upcoming_matches))
            else:
                await message.reply_text("No upcoming matches found.")
        else:
            await message.reply_text(f"Failed to fetch upcoming matches. Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching upcoming matches: {e}")
        await message.reply_text("Error fetching upcoming matches.")


@app.on_message(filters.text)
async def send_live_scores(client, message):
    if message.text.lower().startswith("live"):
        msg = message.text.strip('live')
        if not msg.isdigit():
            return
        a = int(msg)
        if a < 1 or a > len(matches_detail):
            return await message.reply_text("Invalid match selection!")
        
        select_match_url = f'https://www.espncricinfo.com/series/{matches_detail[a-1][3]}-{matches_detail[a-1][2]}/{matches_detail[a-1][1]}-{matches_detail[a-1][0]}/live-cricket-score'
        await message.reply_text(f"Fetching live updates: {select_match_url}")
        cache = []
        while True:
            try:
                url = f"https://hs-consumer-api.espncricinfo.com/v1/pages/match/details?seriesId={matches_detail[a-1][2]}&matchId={matches_detail[a-1][0]}&latest=true"
                r = requests.get(url, timeout=10).json()
                if 'recentBallCommentary' in r and r['recentBallCommentary']:
                    recent_ball = r['recentBallCommentary']['ballComments'][0]
                    four, six, wicket = 'Four Runs ' if recent_ball['isFour'] else '', 'SIX Runs ' if recent_ball['isSix'] else '', 'OUT ' if recent_ball['isWicket'] else ''
                    if recent_ball['oversActual'] not in cache:
                        cache.append(recent_ball['oversActual'])
                        recent = f"{recent_ball['oversActual']} {recent_ball['title']}, {four}{six}{wicket}"
                        await client.send_message(CHAT_ID, recent)
                        if str(recent_ball['oversActual']).endswith('.6'):
                            batsman_info, bowler_info = batsman_data(r), bowler_data(r)
                            output = f"{recent_ball['over']['team']['abbreviation']} - {recent_ball['over']['totalRuns']}/{recent_ball['over']['totalWickets']}\n"
                            output += f"{recent_ball['over']['overRuns']} runs * {recent_ball['over']['overWickets']} wckts\n"
                            output += f"batting=> {' || '.join(batsman_info)}\n"
                            output += f"bowling=> {' || '.join(bowler_info)}"
                            await client.send_message(CHAT_ID, output)
                        await asyncio.sleep(40)
                    else:
                        await asyncio.sleep(30)
                else:
                    await message.reply_text("No Live commentary available for this match")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching match details: {e}")
                await asyncio.sleep(30)

if __name__ == "__main__":
    app.run()
