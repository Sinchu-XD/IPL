import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters

API_ID = 25024171  # Get from my.telegram.org
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7726535663:AAGqwmKwB2RYT3wiFu0408qAayxBp1-AMzU"



bot = Client("CricbuzzBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

CRICBUZZ_URL = "https://www.cricbuzz.com/cricket-match/live-scores"

async def get_matches():
    response = requests.get(CRICBUZZ_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    live_matches = []
    completed_matches = []
    
    for match in soup.find_all("div", class_="cb-lv-scrs-well cb-lv-scrs-well-live"):
        title = match.find("a").text.strip()
        link = "https://www.cricbuzz.com" + match.find("a")["href"]
        live_matches.append(f"🏏 {title}\n🔗 [Live Match]({link})")
    
    for match in soup.find_all("div", class_="cb-lv-scrs-well cb-lv-scrs-well-complete"):
        title = match.find("a").text.strip()
        link = "https://www.cricbuzz.com" + match.find("a")["href"]
        completed_matches.append(f"✅ {title}\n🔗 [Completed Match]({link})")
    
    return live_matches, completed_matches

@bot.on_message(filters.command("matches"))
async def send_matches(client, message):
    live_matches, completed_matches = await get_matches()
    
    response_text = "**🏏 Live & Completed Matches**\n\n"
    
    if live_matches:
        response_text += "**🔥 Live Matches:**\n" + "\n".join(live_matches) + "\n\n"
    else:
        response_text += "No live matches currently.\n\n"
    
    if completed_matches:
        response_text += "**✅ Completed Matches:**\n" + "\n".join(completed_matches) + "\n\n"
    else:
        response_text += "No recently completed matches.\n\n"
    
    await message.reply_text(response_text, disable_web_page_preview=True)

bot.run()
