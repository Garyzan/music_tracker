import asyncio
import json
import logging
import os
import requests
import sys

from datetime import date, timedelta
from dotenv import load_dotenv
from logging import log
from ratelimit import limits, sleep_and_retry

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

## Environment

load_dotenv()
TOKEN : str = os.getenv("TOKEN", "")

ALLOWLIST = []
try:
    with open("allowlist", "r") as f:
        ALLOWLIST = [int(user_id) for user_id in f.readlines()]
except FileNotFoundError:
    log(logging.ERROR, "Allowlist file not found. Exiting....")
    exit()

dp = Dispatcher()


## Command handlers

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    if not message.from_user.id in ALLOWLIST:
        log(logging.INFO, f"Message from blocked user {message.from_user.id}")
        return
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

@dp.message(Command("add"))
@dp.message(Command("track"))
async def add_tracking(message: Message) -> None:
    if not message.from_user.id in ALLOWLIST:
        log(logging.INFO, f"Message from blocked user {message.from_user.id}")
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
        log(logging.INFO, f"Message from blocked user {message.from_user.id}")
        return
    
    filepath = f"tracks/{message.from_user.id}.json"
    if not os.path.isfile(filepath):
        await message.answer(f"No artists tracked")
        return
    
    await message.answer(f"Added to queue...")
    
    with open(filepath, 'r') as f:
        tracking: dict = json.load(f)
    for artist_id, last_date in tracking.items():
        resp = get_releases_since(artist_id, last_date)
        if resp != False:
            tracking[artist_id] = date.today().strftime('%Y-%m-%d')

    await message.answer(f"Done")

@dp.message(Command("delete"))
@dp.message(Command("remove"))
async def remove_tracking(message: Message) -> None:
    if not message.from_user.id in ALLOWLIST:
        log(logging.INFO, f"Message from blocked user {message.from_user.id}")
        return
    
    if(len(message.text.split(" ")) == 1):
        await message.answer("Please include an artists name or MusicBrainz ID")
        return
    
    artist_ids = message.text.split(" ")[1:]
    remove_from_trackfile(message.from_user.id, artist_ids)
    await message.answer(f"No longer tracking {', '.join(artist_ids)}!")


## Helpers

### TODO: implement x.x

@sleep_and_retry
@limits(calls=1, period=1.1)
def mbdb_get(req_string):
    return requests.get(req_string)

def get_releases_since(artist_id: str, date: str) -> list[str] | bool:
    req_string = f"https://musicbrainz.org/ws/2/release?fmt=json&query=arid:{artist_id}%20AND%20date:[{date}%20TO%20*]"
    r = mbdb_get(req_string)
    if r.status_code != 200:
        log(logging.ERROR, f"Error returned: {r.status_code}: {r.text}")
        return False
    print(r.status_code)
    print(f"{r.text}")
    return True

def add_to_trackfile(uid: int, artist_ids: list[str]):
    filepath = f"tracks/{uid}.json"
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            tracking: dict = json.load(f)
    else:
        tracking = {}
    for artist_id in artist_ids:
        tracking[artist_id] = date.today().strftime('%Y-%m-%d')
    with open(filepath, 'w') as f:
        json.dump(tracking, f)

def remove_from_trackfile(uid: int, artist_ids: list[str]):
    filepath = f"tracks/{uid}.json"
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            tracking: dict = json.load(f)
            
        for artist_id in artist_ids:
            if artist_id in tracking.keys():
                del tracking[artist_id]

        with open(filepath, 'w') as f:
            json.dump(tracking, f)
    else:
        log(logging.INFO, "Attempted to remove artist from empty trackfile")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())