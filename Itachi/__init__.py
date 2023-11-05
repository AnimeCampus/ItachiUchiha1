import os
import logging
import time 
import sys
import asyncio
from Itachi.config import *
from pyrogram import Client
import telegram.ext as tg
from telethon.sessions import MemorySession
from telethon import TelegramClient
from Itachi.utils.quoteapi import Quotly
from rich.table import Table
from rich.console import Console 
from aiohttp import ClientSession
from Python_ARQ import ARQ
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

IMPORTED = {}
HELPABLE = {}
MODULES = {}
quotly = Quotly()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
LOGGER = logging.getLogger("Itachi")

LOG = Console()
StartTime = time.time()
loop = asyncio.get_event_loop()
aiohttpsession = ClientSession()
mongo = MongoClient(MONGO_DB_URL)
db = mongo.Itachi

if sys.version_info[0] < 3 and sys.version_info[1] < 6:
    LOG.print("You Must Have Python3 Version Exiting...")
    sys.exit(1)

def get_readable_time(seconds: int) -> str:
    time_string = ""
    if seconds < 0:
        raise ValueError("Input value must be non-negative")

    if seconds < 60:
        time_string = f"{round(seconds)}s"
    else:
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        if days > 0:
            time_string += f"{round(days)}days, "
        if hours > 0:
            time_string += f"{round(hours)}h:"
        time_string += f"{round(minutes)}m:{round(seconds):02d}s"

    return time_string


MOD_LOAD = []
MOD_NOLOAD = []    
BOT_ID = 5520008350
BOT_USERNAME = "Itachi_UchihaXBot"
BOT_NAME = "Itachi Uchiha"

arq = ARQ("arq.hamker.dev",ARQ_API_KEY, aiohttpsession)

app = Client (
      "ItachiUchihaXXXX",
      api_id=API_ID,
      api_hash=API_HASH,
      bot_token=BOT_TOKEN,
      sleep_threshold=0,
      plugins=dict(root="Itachi/modules")
      )
pbot = Client (
      "ITACHIBDB",
      api_id=API_ID,
      api_hash=API_HASH,
      bot_token=BOT_TOKEN,
      sleep_threshold=0,
      plugins=dict(root="Itachi/plugins")
      )

ALPHA = Client (
      "ItachiXX",
      api_id=API_ID,
      api_hash=API_HASH,
      bot_token=BOT_TOKEN
)
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
WORKERS = 9
defaults = tg.Defaults(run_async=True)
updater = tg.Updater(BOT_TOKEN, workers=WORKERS, use_context=True)
dispatcher = updater.dispatcher
async def init():
    LOG.print("Itachi Uchiha Bot Starting....")    
    await app.start()
    await ALPHA.start()
    await pbot.start()
    await telethn.start(bot_token=BOT_TOKEN)
    x =  db.sudo.find().to_list(length=None)
    for i in await x :
        config.SUDO_USERS.append(i["user_id"])
    config.SUPER_USERS.extend(SUDO_USERS)
    msg = "Sudo Users :-\n"
    for m in set(SUDO_USERS):
        try:
            mention = (await app.get_users(int(m))).first_name 
            msg += f"• {mention}\n"
        except Exception as e:
            print(e)
    LOG.print(f"Loaded Sudo Users. :- \n\n{msg}") 
    
    LOG.print("Successfully Executed Everything.")
    
app.run()
loop.run_until_complete(init()) 
