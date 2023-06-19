import os
import re
from platform import python_version as y
from telethon import events, Button
from telegram import __version__ as telever
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from Kynan.events import register
from Kynan import telethn as tbot


PHOTO = "https://telegra.ph/file/d3b40cbdcbd84bfca790d.jpg"

@register(pattern=("/alive"))
async def awake(event):
  TEXT = f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
  TEXT += f"┠➣ 𝘿𝙯𝙈𝙪𝙨𝙞𝙘𝙍𝙤𝙗𝙤𝙩\n"
  TEXT += f"┠➣ **ᴍʏ ᴏᴡɴᴇʀ : [🄼🅂 𝗗🆉𝗨𝗟𝚀𝐔𝐑𝐍Λ𝐈𝐍](https://t.me/MSDZULQRNN)**\n"
  TEXT += f"┠➣ **ᴘʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ :** `{y()}`\n"
  TEXT += f"┠➣ **ʟɪʙʀᴀʀʏ ᴠᴇʀsɪᴏɴ :** `{telever}` \n"
  TEXT += f"┠➣ **ᴛᴇʟᴇᴛʜᴏɴ ᴠᴇʀsɪᴏɴ :** `{tlhver}` \n"
  TEXT += f"┠➣ **ᴘʏʀᴏɢʀᴀᴍ ᴠᴇʀsɪᴏɴ :** `{pyrover}` \n"
  TEXT += "┗━━━━━━━━━━━━━━━━━━━━┛"
  BUTTON = [[Button.url("ʜᴇʟᴘ​", "https://t.me/DzMusicRobot?start=help"), Button.url("ᴅᴏɴᴀsɪ ​❤️", "https://telegra.ph/file/bdf23d4e78c8337249c26.png")]]
  await tbot.send_file(event.chat_id, PHOTO, caption=TEXT,  buttons=BUTTON)
