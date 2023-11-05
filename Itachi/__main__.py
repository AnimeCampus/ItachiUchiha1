import os
import asyncio
import re
import time
import uvloop
import platform
import random 
from Itachi import config
import strings
import importlib
from telegram import ParseMode, Update
from telegram.error import (
    BadRequest,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop

from pyrogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    CallbackQuery)
from pyrogram.errors import BadRequest,Unauthorized 
from pyrogram import filters,idle
from Itachi.utils.misc import paginate_modules
from Itachi import *
from Itachi.modules.mongo.users_db import add_served_user
from fuzzywuzzy import process
from rich.table import Table
from pyrogram.enums import ParseMode,ChatType
from pyrogram import __version__ as pyrover
from Itachi.modules import ALL_MODULES
from Itachi.plugins.rules import send_rules
from unidecode import unidecode
from Itachi import StartTime , get_readable_time
loop = asyncio.get_event_loop() 
bot_name = f"{dispatcher.bot.first_name}"
ITACHI_PIC = ["https://telegra.ph/file/986b76680ebc9d88f5c53.jpg", "https://telegra.ph/file/986b76680ebc9d88f5c53.jpg", "https://telegra.ph/file/986b76680ebc9d88f5c53.jpg", "https://telegra.ph/file/986b76680ebc9d88f5c53.jpg", "https://telegra.ph/file/986b76680ebc9d88f5c53.jpg", "https://telegra.ph/file/986b76680ebc9d88f5c53.jpg"]
uptime = get_readable_time((time.time() - StartTime))
WEBHOOK = False
async def main():
    global IMPORTED, HELPABLE, MODULES
    for module in ALL_MODULES:
        imported_module = importlib.import_module(f"Itachi.modules.{module}")
        if hasattr(imported_module, "__mod_name__") and imported_module.__mod_name__:
            imported_module.__mod_name__ = imported_module.__mod_name__
            if hasattr(imported_module, "__help__") and imported_module.__help__:
                HELPABLE[imported_module.__mod_name__.lower()] = imported_module
    bot_modules = ""
    j = 1
    for i in ALL_MODULES:
        if j == 4:
            bot_modules += "| {:<15}|\n".format(i)
            j = 0
        else:
            bot_modules += "| {:<15}".format(i)
        j += 1
    LOG.print(f"Loaded Modules :-\n{bot_modules}")
    print()
    LOG.print(f"{BOT_NAME} Started. ")
    try:                                                                    
        LOG.print("Using long polling.")
        updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)    
    except:
        LOG.print("Ptb died")
    try:
        await app.send_photo(f"@{config.SUPPORT_CHAT}",
                             photo=random.choice(ITACHI_PIC),
                             caption=strings.SUPPORT_SEND_MSG.format(platform.python_version(), pyrover, uptime)
                             )
        
      #  await pbot.send_message(config.OWNER_ID , "Ok")
    except Exception as e:
        LOG.print(f"{e}")
        LOG.print(f"Bot isn't able to send message to @{config.SUPPORT_CHAT} !")
    
    await idle()

      
dispatcher.bot.send_message(config.OWNER_ID , "Started")
def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("Yamete Kudasai..")
    print(update.effective_message)

test_handler = CommandHandler("test", test, run_async=True)
dispatcher.add_handler(test_handler)

async def send_help(app,chat, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))    
    await app.send_message(
        chat_id=chat,
        text=text,
        parse_mode=ParseMode.MARKDOWN,      
        reply_markup=keyboard,
    )
    return (text, keyboard)

@ALPHA.on_message(filters.command("start"))
async def group_start(_, message):    
    print(MODULES)
    chat_id = message.chat.id 
    args = message.text.split()
    if message.chat.type == ChatType.PRIVATE :
        await add_served_user(message.from_user.id)
        if len(args) >= 2:
            if args[1].lower() == "help":
                await send_help(_,chat_id,strings.HELP_STRINGS) 
            elif args[1].lower().startswith("ghelp_"):
                mod = args[1].lower().split("_", 1)[1]
#                 try:
                mod = mod.replace("_", " ")
#                 excpet :
#                     mod = mod
                await _.send_message(
                    chat_id,
                    f"{strings.HELP_STRINGS}\n{MODULES[mod]}",
                    reply_markup = InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="«", callback_data="help_back")]]
                    ),
                )
            elif args[1][1:].isdigit():
                await send_rules(message,int(args[1]), from_pm=True)

                
        else:
            mention = message.from_user.mention                       
            await app.send_message(
           chat_id,    
           strings.PM_START_TEXT.format(BOT_NAME,mention,uptime,platform.python_version(),pyrover),
           reply_markup=InlineKeyboardMarkup(strings.START_BUTTONS)
           )
                        
            
    else:
        await message.reply_photo(
                random.choice(ITACHI_PIC),
                caption="**Hii {}, I'm here to help since:** `{}`".format(message.from_user.mention,uptime),
                reply_markup=InlineKeyboardMarkup(strings.GRP_START)
            )
                   
             
@ALPHA.on_callback_query(filters.regex(r"help_(.*?)"))
async def help_button(_,query):    
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data) 
               
    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "» **Available Commands For** **{}** :\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            await query.message.edit_text(
                text,
                parse_mode=ParseMode.MARKDOWN,                
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Back 🔙", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            await query.message.edit_text(
                strings.HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(paginate_modules(curr_page - 1, HELPABLE, "help")
             ),
          )
                                   
        elif next_match:
            next_page = int(next_match.group(1))
            await query.message.edit_text(
                strings.HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )                   

        elif back_match:
           await query.message.edit_text(
                strings.HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )            

        return await _.answer_callback_query(query.id)

    except BadRequest:
        pass

@ALPHA.on_message(filters.command("help"))
async def get_help(_, message):
    chat_id = message.chat.id
    args = message.text.split(None,1)
    chat_type = message.chat.type
    if chat_type != ChatType.PRIVATE:
        if len(args) >= 2 and process.extractOne(args[1].lower(),MODULES.keys())[0] in MODULES.keys():
            module = process.extractOne(args[1].lower(),MODULES.keys())[0].replace(" ","_")
            await message.reply_photo(
                photo = random.choice(ITACHI_PIC),
                caption= f"**Contact me in PM to get help of {module.capitalize().replace('_',' ')}**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Help 🆘",
                                url=f"https://t.me/{BOT_USERNAME}?start=ghelp_{module}"
                            )
                        ]
                    ]
                ),
            )
            return
        await message.reply_photo(
            photo = random.choice(ITACHI_PIC),
            caption="**Choose An Option For Help**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Private 💻",
                            url="https://t.me/{}?start=help".format(
                                BOT_USERNAME
                            ),
                        )
                    ],
                    
                ],
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "**Here is the available help for the *{}* module:\n**".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        await send_help(
            _,
            chat_id,
            HELP_STRINGS,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="«", callback_data="help_back")]]
            ),
        )

    else:
        await send_help(_,chat_id,strings.HELP_STRINGS)

                              
                     
@ALPHA.on_message(filters.command("donate"))  
async def donate(_, message):
    if message.chat.type == ChatType.PRIVATE:
        if message.from_user.id == config.OWNER_ID:
            await message.reply_text("⊙﹏⊙") 
        else:
            await message.reply_text(f"**You Can Donate Me [Here]({config.DONATION_LINK})**")                                                
    else:
        if message.from_user.id == config.OWNER_ID:
            await message.reply_text("⊙﹏⊙") 
        else:
            await message.reply_text("**I've PMed You About Donating My Creator.**")
            try:
                await app.send_message(message.from_user.id,text=f"[Here Is The Donation Link]({config.DONATION_LINK})")
            except Unauthorized:                
                await message.reply_text("**Contact Me In PM To Get Donation Information First!**")
                
if __name__ == "__main__" :
    loop.run_until_complete(main())
    LOG.print("Stopped Client.") 
