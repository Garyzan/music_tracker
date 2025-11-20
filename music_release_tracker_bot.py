import asyncio
import json
import logging
import os
import sys

import mbdb_interface
import file_handler

from dotenv import load_dotenv
from logging import log

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
    file_handler.add_artists(message.from_user.id, artist_ids)
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
    for artist_id in file_handler.get_artists(message.from_user.id):
        last_date = file_handler.get_last_date(message.from_user.id, artist_id)
        resp = mbdb_interface.get_releases_since(artist_id, last_date)
        if resp.status_code != 200:
            log(logging.ERROR, f"Error returned: {resp.status_code}: {resp.text}")
            await(message.answer(f"Could not retrieve releases for MBID {artist_id} at this time"))
        else:
            file_handler.update_last_date(message.from_user.id, artist_id)
            resp_j = resp.json()
            if resp_j['count'] == 0:
                await message.answer(f"No new releases for {artist_id}")

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
    file_handler.remove_artists(message.from_user.id, artist_ids)
    await message.answer(f"No longer tracking {', '.join(artist_ids)}!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())