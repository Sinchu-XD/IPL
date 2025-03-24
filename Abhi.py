import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import json

# Replace with your bot token and API key
API_KEY = "9a7a66e7-f1d5-4899-ad9f-21a1a172f58e"
API_ID = 25024171  # Get from my.telegram.org
API_HASH = "7e709c0f5a2b8ed7d5f90a48219cffd3"
BOT_TOKEN = "7726535663:AAFVBNgn5z-gUK7Tr7XoKTS3bopW3OLBSPM"
API_URL = "https://api.cricapi.com/v1"


# Initialize the Pyrogram client
app = Client("IPLBt", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN) #replace with your api id and hash

async def get_ipl_matches():
    """Fetches list of IPL matches from the API."""
    try:
        url = f"{API_URL}/series?apikey={API_KEY}&offset=0"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and data['data'] is not None:
            ipl_series = [series for series in data['data'] if "Indian Premier League" in series.get('name', '')] #Get IPL series
            if not ipl_series:
                return "No IPL matches found."

            ipl_id = ipl_series[0]['id'] #get the id of the first ipl series found.

            matches_url = f"{API_URL}/series_matches?apikey={API_KEY}&id={ipl_id}&offset=0"
            matches_response = requests.get(matches_url)
            matches_response.raise_for_status()
            matches_data = matches_response.json()

            if 'data' in matches_data and matches_data['data'] is not None:
                matches = matches_data['data']
                match_list = []
                for match in matches:
                    match_name = match.get('name', 'Match name not found')
                    status = match.get('status', 'Status not found')
                    match_list.append(f"**{match_name}**\nStatus: {status}\n")

                return "\n".join(match_list)

            else:
                return "No IPL matches found."

        else:
            return "IPL series data not found."

    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"
    except json.JSONDecodeError:
        return "Error decoding JSON response."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@app.on_message(filters.command("ipl"))
async def ipl_command(client: Client, message: Message):
    """Handles the /ipl command."""
    ipl_matches = await get_ipl_matches()
    await message.reply_text(ipl_matches)

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handles the /start command."""
    await message.reply_text("Welcome to the IPL Bot! Use /ipl to get a list of IPL matches.")

async def main():
    """Main function to start the bot."""
    await app.start()
    print("Bot started. Listening for commands...")
    await asyncio.Future()  # Keep the bot running

if __name__ == "__main__":
    asyncio.run(main())
