import asyncio
import logging
import sys
import requests
import os
import json
from datetime import date, timedelta
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

## Envorinment

load_dotenv()
TOKEN = os.getenv("TOKEN")

ALLOWLIST = []
try:
    with open("allowlist", "r") as f:
        ALLOWLIST = [int(user_id) for user_id in f.readlines()]
except FileNotFoundError:
    logging.log(logging.ERROR, "Allowlist file not found. Exiting....")
    exit()

dp = Dispatcher()


## Command handlers

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    if not message.from_user.id in ALLOWLIST:
        logging.log(logging.INFO, f"Message from blocked user {message.from_user.id}")
        return
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

@dp.message(Command("add"))
@dp.message(Command("track"))
async def add_tracking(message: Message) -> None:
    if not message.from_user.id in ALLOWLIST:
        logging.log(logging.INFO, f"Message from blocked user {message.from_user.id}")
        return
    
    if(len(message.text.split(" ")) == 1):
        await message.answer("Please include at least one MusicBrainz ID (multiple entries should be separated by spaces)")
        return
    
    artist_ids = message.text.split(" ")[1:]
    add_to_trackfile(message.from_user.id, artist_ids)
    await message.answer(f"Tracking {', '.join(artist_ids)}!")

@dp.message(Command("refresh"))
async def refresh(message: Message) -> None:
    if not message.from_user.id in ALLOWLIST:
        logging.log(logging.INFO, f"Message from blocked user {message.from_user.id}")
        return
    
    pass

@dp.message(Command("delete"))
@dp.message(Command("remove"))
async def remove_tracking(message: Message) -> None:
    if not message.from_user.id in ALLOWLIST:
        logging.log(logging.INFO, f"Message from blocked user {message.from_user.id}")
        return
    
    if(len(message.text.split(" ")) == 1):
        await message.answer("Please include an artists name or MusicBrainz ID")
        return
    
    artist_id = message.text[7:]
    add_to_trackfile(message.from_user.id, [artist_id])
    await message.answer(f"Tracking {artist_id}!")



## Helpers

### TODO: implement x.x
def get_releases_since(arid: str, date: str) -> list:
    req_string = f"https://musicbrainz.org/ws/2/release?fmt=json&query=arid:{arid}%20AND%20date:[{date}%20TO%20*]"
    #r = requests.get(req_string)
    #print(f"\n{r.text}")

def yesterday_str() -> str:
    return (date.today() - timedelta(days=1)).strftime('%y-%m-%d')

def add_to_trackfile(uid: int, arids: list[str]):
    filepath = f"tracks/{uid}.json"
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            tracking : dict = json.load(f)
    else:
        tracking = {}
    for arid in arids:
        tracking[arid] = yesterday_str()
    with open(filepath, 'w') as f:
        json.dump(tracking, f)

def remove_from_trackfile(uid: int, arids: list[str]):
    filepath = f"tracks/{uid}.json"
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            tracking : dict = json.load(f)
    else:
        logging.log(logging.INFO, "Attempted to remove artist from empty trackfile")
    for arid in arids:
        tracking[arid] = yesterday_str()
    with open(filepath, 'w') as f:
        json.dump(tracking, f)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())