import html
import os
import json
import importlib
import time
import re
import sys
import traceback
import Kynan.modules.sql.users_sql as sql
from sys import argv
from typing import Optional
from telegram import __version__ as telever
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from platform import python_version as y
from Kynan import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    BOT_NAME,
    BOT_USERNAME,
    OWNER_ID,
    PORT,
    SUPPORT_CHAT,
    TOKEN,
    URL,
    WEBHOOK,
    SUPPORT_CHAT,
    dispatcher,
    StartTime,
    telethn,
    pbot,
    updater,
)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from Kynan.modules import ALL_MODULES
from Kynan.modules.helper_funcs.chat_status import is_user_admin
from Kynan.modules.helper_funcs.misc import paginate_modules
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown
from Zul.manage import DASAR, LANJUT, AHLI, PRO
from Zul.jasa import JASA


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["Dtk", "Mnt", "Jam", "Hari"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ", ".join(time_list)

    return ping_time

KYNAN_IMG = "https://telegra.ph/file/d3b40cbdcbd84bfca790d.jpg"

PM_START_TEXT = """
**ʜᴀʟᴏ {}

𝘿𝙯𝙈𝙪𝙨𝙞𝙘𝙍𝙤𝙗𝙤𝙩 ᴅɪʙᴜᴀᴛ ᴜɴᴛᴜᴋ
ᴍᴇɴɢᴇʟᴏʟᴀ ᴅᴀɴ ᴍᴇᴍᴜᴛᴀʀ ᴍᴜꜱɪᴋ
ᴅɪɢʀᴜᴘ ᴀɴᴅᴀ ᴅᴇɴɢᴀɴ ʙᴇʀʙᴀɢᴀɪ ꜰɪᴛᴜʀ.
━━━━━━━━━━━━━━━━━━━━━━━━
➥ ᴜᴘᴛɪᴍᴇ » {}
➥ ᴜsᴇʀs   » {}
➥ ɢʀᴏᴜᴘs » {}
━━━━━━━━━━━━━━━━━━━━━━━━
ᴋʟɪᴋ ʙᴜᴛᴛᴏɴ ᴍᴀɴᴀɢᴇ ᴜɴᴛᴜᴋ ᴘᴇɴɢᴀᴛᴜʀᴀɴ
ᴍᴀɴᴀɢᴇ ᴅᴀɴ ᴋʟɪᴋ ʙᴜᴛᴛᴏɴ ᴍᴜsɪᴄ ᴜɴᴛᴜᴋ
ᴘᴇɴɢᴀᴛᴜʀᴀɴ ᴍᴜsɪᴄ ⚠️**
"""

buttons = [
    [
        InlineKeyboardButton(text="ᴛᴀᴍʙᴀʜᴋᴀɴ ɢᴡ ᴋᴇ ɢʀᴏᴜᴘ ʟᴜ➕", url="t.me/DzMusicRobot?startgroup=true"),
    ],
    [
        InlineKeyboardButton(text="ᴍᴀɴᴀɢᴇ", callback_data="kynan_support"),
        InlineKeyboardButton(text="ᴍᴜsɪᴄ", callback_data="kynan_"),
    ],
    [
        InlineKeyboardButton(text="ᴊᴀsᴀ ʙᴏᴛ🤖", callback_data="kynan_jasa"),
    ],
    [
        InlineKeyboardButton(text="ᴄʜᴀɴɴᴇʟ", url="https://t.me/MSPR0JECT"),
        InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url="https://t.me/envSample"),
    ],
    [
        InlineKeyboardButton(text="ᴛᴜᴛᴜᴘ", callback_data="close"),
    ],
]


HELP_STRINGS = """
Klik tombol di bawah ini untuk mendapatkan deskripsi tentang perintah spesifik."""

DONATE_STRING = """Jika ingin berdonasi agar bot ini tetap hidup, kamu bisa contact @kiritonibos."""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("Kynan.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=False,
        reply_markup=keyboard,
    )


def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Penguji halo! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("Orang ini mengedit pesan")
    print(update.effective_message)


def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="«", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_text(
                PM_START_TEXT.format(
                    #photo=KYNAN_IMG,
                    escape_markdown(first_name),
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats()
                    ),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=5,
                disable_web_page_preview=False,
            )
    else:
        update.effective_message.reply_text(
            f"<b>Aktif</b>\n<b>Ping :</b> <code>{uptime}</code>",
            parse_mode=ParseMode.HTML
       )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Berikut adalah bantuan untuk *{}* modul:\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="«", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


def kynan_about_callback(update, context):
    query = update.callback_query
    if query.data == "kynan_":
        query.message.edit_text(
            text="♬ ʙᴀɴᴛᴜᴀɴ ᴘᴇʀɪɴᴛᴀʜ ᴍᴜꜱɪᴄ."
            "\nᴘɪʟɪʜ ᴍᴇɴᴜ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ ᴜɴᴛᴜᴋ ᴍᴇʟɪʜᴀᴛ ʙᴀɴᴛᴜᴀɴ ᴍᴜꜱɪᴄ. ",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="ᴘᴇʀɪɴᴛᴀʜ ᴀᴅᴍɪɴ", callback_data="kynan_admin"),
                    InlineKeyboardButton(text="ᴘᴇʀɪɴᴛᴀʜ ʙᴏᴛ", callback_data="kynan_notes"),
                 ],
                 [
                    InlineKeyboardButton(text="ᴘᴇʀɪɴᴛᴀʜ ᴘʟᴀʏ", callback_data="source_"),
                    InlineKeyboardButton(text="ᴘᴇʀɪɴᴛᴀʜ ᴇxsᴛʀᴀ", callback_data="kynan_credit"),
                 ],
                 [
                    InlineKeyboardButton(text="«", callback_data="kynan_support"),
                 ]
                ]
            ),
        )
    elif query.data == "kynan_back":
        first_name = update.effective_user.first_name
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_text(
                
                PM_START_TEXT.format(
                    #photo=KYNAN_IMG,
                    escape_markdown(first_name),
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats()
                    ),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=5,
                disable_web_page_preview=False,
        )

    elif query.data == "kynan_admin":
        query.message.edit_text(
            text=f"*✮ PERINTAH ADMIN."
            "\n\n ➣ /pause - Jeda musik yang diputar."
            "\n ➣ /resume - Lanjutkan musik yang dijeda."
            "\n ➣ /skip - Lewati musik yang sedang diputar."
            "\n ➣ /end - Hentikan musik yang sedang diputar."
            "\n\n༊ Pengguna Auth."
            "\nPengguna Auth dapat menggunakan perintah admin tanpa hak admin di Group Anda."
            "\n ➣ /auth [Username] - Tambahkan pengguna ke AUTH LIST dari grup."
            "\n ➣ /unauth [Username] - Hapus pengguna dari AUTH LIST grup."
            "\n ➣ /authusers - Periksa DAFTAR AUTH grup",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="«", callback_data="kynan_")]]
            ),
        )
    elif query.data == "kynan_jasa":
        query.message.edit_text(
            text=JASA,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                    InlineKeyboardButton(text="️Admin 👤", url=f"tg://user?id={OWNER_ID}"),
                    
                  ],
                  [
                    
                    InlineKeyboardButton(text="«", callback_data="kynan_back"),
                  ]
                ]
            ),
        )
    elif query.data == "kynan_notes":
        query.message.edit_text(
            text="✮ PERINTAH BOT"
            "\n\n ➣ /mstats - Dapatkan 10 Trek Global Stats Teratas, 10 Pengguna Bot Teratas, 10 Obrolan Teratas di bot, 10 Teratas Dimainkan dalam obrolan, dll."
            "\n\n ➣ /msudolist - Periksa Sudo Pengguna Music,"
            "\n\n ➣ /lyrics [Nama Musik] mencari Lirik untuk Musik tertentu di web."
            "\n\n ➣ /song [Nama Trek] atau [Tautan YT] - Unduh trek apa pun dari youtube dalam format mp3 atau mp4."
            "\n\n ➣ /player -  Dapatkan Panel Bermain interaktif."
            "\n\n ➣ c singkatan dari pemutaran saluran."
            "\n\n ➣ /queue or /cqueue- Periksa Daftar Antrian Musik",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="«", callback_data="kynan_")]]
            ),
        )
    elif query.data == "kynan_support":
        query.message.edit_text(
            text="Selamat datang di menu panduan",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="💁🏻‍♂Perintah Dasar", callback_data="kynan_dasar"),
                    InlineKeyboardButton(text="Lanjutan🙋🏻‍♂", callback_data="kynan_lanjut"),
                 ],
                 [
                    InlineKeyboardButton(text="🕵🏻Ahli", callback_data="kynan_ahli"),
                    InlineKeyboardButton(text="Panduan Pro💆🏻‍♂", callback_data="kynan_pro"),
                 ],
                 [
                    InlineKeyboardButton(text="➕ Panduan Lengkap ➕", url="http://t.me/DzMusicRobot?start=help"),
                 ],
                 [
                    InlineKeyboardButton(text="🔙 Kembali", callback_data="kynan_back"),
                 
                 ]
                ]
            ),
        )


    elif query.data == "kynan_credit":
        query.message.edit_text(
            text="✮ PERINTAH EKSTRA"
            "\n\n༊ Perintah Ekstra."
            "\n\n ➣ /mstart - Mulai Bot Musik."
            "\n\n ➣ /mhelp - Dapatkan Menu Pembantu Perintah dengan penjelasan rinci tentang perintah."
            "\n\n ➣ /mping- Ping Bot dan periksa statistik Ram, Cpu, dll dari Bot."
            "\n\n༊ Pengaturan Music."
            "\n ➣ /msettings - Dapatkan pengaturan grup lengkap dengan tombol sebaris."
            "\n\n༊ Opsi di Pengaturan."
            "\n\n➣ Kamu Bisa set ingin Kualitas Audio Anda streaming di obrolan suara."
            "\n\n➣ You can set Kualitas Video Anda ingin streaming di obrolan suara."
            "\n\n➣ Auth Users:- Anda dapat mengubah mode perintah admin dari sini ke semua orang atau hanya admin. Jika semua orang, siapa pun yang ada di grup Anda dapat menggunakan perintah admin (seperti /skip, /stop dll)."
            "\n\n➣ Clean Mode: Saat diaktifkan, hapus pesan bot setelah 5 menit dari grup Anda untuk memastikan obrolan Anda tetap bersih dan baik."
            "\n\n➣ Command Clean : Saat diaktifkan, Bot akan menghapus perintah yang dieksekusi (/play, /pause, /shuffle, /stop etc) langsung."
            "\n\n➣ Play Settings."
            "\n\n • /playmode - Dapatkan panel pengaturan pemutaran lengkap dengan tombol tempat Anda dapat mengatur pengaturan pemutaran grup Anda."
            "\n\n༊ Opsi dalam mode putar."
            "\n\n➣ Mode Pencarian [Langsung atau Inline] - Mengubah mode pencarian Anda saat Anda memberikan mode /play."
            "\n\n➣ Perintah Admin [Semua orang atau Admin] - Jika semua orang, siapa pun yang ada di grup Anda akan dapat menggunakan perintah admin (seperti /skip, /stop dll)."
            "\n\n➣ Jenis Bermain [Everyone or Admins] - Jika admin, hanya admin yang ada di grup yang dapat memutar musik di obrolan suara",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="", callback_data="kynan_"),
                    InlineKeyboardButton(text="ᴍᴀɴᴀɢᴇ ✮", callback_data="help_back"),
                 ],
                 [
                    InlineKeyboardButton(text="«", callback_data="kynan_")
                 ]
                ]
            ),
        )
    elif query.data == "kynan_dasar":
        query.message.edit_text(
            text=DASAR,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🔙 Kembali ke Panduan", callback_data="kynan_support"),]]),)
    elif query.data == "kynan_lanjut":
        query.message.edit_text(
            text=LANJUT,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🔙 Kembali ke Panduan", callback_data="kynan_support"),]]),)
    elif query.data == "kynan_ahli":
        query.message.edit_text(
            text=AHLI,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🔙 Kembali ke Panduan", callback_data="kynan_support"),]]),)
    elif query.data == "kynan_pro":
        query.message.edit_text(
            text=PRO,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🔙 Kembali ke Panduan", callback_data="kynan_support"),]]),)

def Source_about_callback(update, context):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text="✮ PERINTAH PLAY."
            "\n\n༊Perintah Play."
            "\n\nPerintah yang tersedia = play , vplay , cplay."
            "\n\nPerintah ForcePlay = playforce , vplayforce , cplayforce."
            "\n\nc singkatan dari pemutaran Channel."
            "\nv singkatan dari pemutaran video."
            "\nforce singkatan dari force play."
            "\n\n ➣ /play atau /vplay atau /cplay  - Bot akan mulai memainkan kueri yang Anda berikan di obrolan suara atau Streaming tautan langsung di obrolan suara."
            "\n\n ➣ /playforce atau /vplayforce atau /cplayforce -  Force Play menghentikan trek yang sedang diputar pada obrolan suara dan mulai memutar trek yang dicari secara instan tanpa mengganggu/mengosongkan antrean."
            "\n\n ➣ /channelplay [Nama pengguna atau id obrolan] atau [Disable] - Hubungkan saluran ke grup dan streaming musik di obrolan suara saluran dari grup Anda."
            "\n\n༊Daftar Putar Server Bot."
            "\n ➣ /playlist  - Periksa Daftar Putar Tersimpan Anda Di Server."
            "\n ➣ /deleteplaylist - Hapus semua musik yang disimpan di daftar putar Anda."
            "\n ➣ /play  - Mulai mainkan Daftar Putar Tersimpan Anda dari Server",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="«", callback_data="kynan_")
                 ]
                ]
            ),
        )
    elif query.data == "source_back":
        first_name = update.effective_user.first_name
        query.message.edit_text(
                
                PM_START_TEXT.format(
                    #photo=KYNAN_IMG,
                    escape_markdown(first_name),
                    escape_markdown(uptime),
                    sql.num_users(),
                    sql.num_chats()
                    ),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=5,
                disable_web_page_preview=True,
        )

def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"➣ Hubungi saya di PM untuk mendapatkan bantuan {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="👨‍💼 Bantuan",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "➣ Pilih pengaturan.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Buka Di Private",
                            url="https://t.me/{}?start=help".format(
                                context.bot.username
                            ),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="Buka Disini",
                            callback_data="help_back",
                        )
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="«", callback_data="kynan_support")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "Ini adalah pengaturan Anda saat ini:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Sepertinya tidak ada pengaturan khusus pengguna yang tersedia :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Modul mana yang ingin Anda periksa {} pengaturan untuk?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Sepertinya tidak ada pengaturan obrolan yang tersedia :'(\nKirim ini "
                "dalam obrolan grup tempat Anda menjadi admin untuk menemukan pengaturannya saat ini!",
                parse_mode=ParseMode.MARKDOWN,
            )


def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* memiliki pengaturan berikut untuk *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="«",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hai, yang di sana! Ada beberapa pengaturan untuk {} - pergi ke depan dan memilih apa "
                "kamu tertarik.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hai, yang di sana! Ada beberapa pengaturan untuk {} - pergi ke depan dan memilih apa "
                "kamu tertarik.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Klik di sini untuk mendapatkan pengaturan obrolan ini, serta pengaturan Anda."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="sᴇᴛᴛɪɴɢs",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Klik di sini untuk memeriksa pengaturan Anda."

    else:
        send_settings(chat.id, user.id, True)


def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 1337085565:
            update.effective_message.reply_text(
                "I'm free for everyone ❤️ If you wanna make me smile, just join"
                "[My Channel]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.send_photo(
                chat_id=f"@{SUPPORT_CHAT}",
                photo=KYNAN_IMG,
                caption=f"""
╼┅━━━━━━━━━━╍━━━━━━┅╾
*❏ ꝛɪᴛσ ꝛσʙσᴛ*
*├ ᴘʏᴛʜᴏɴ :* `{y()}`
*├ ʟɪʙʀᴀʀʏ :* `{telever}`
*├ ᴛᴇʟᴇᴛʜᴏɴ :* `{tlhver}`
*╰ ᴩʏʀᴏɢʀᴀᴍ :* `{pyrover}`
╼┅━━━━━━━━━━╍━━━━━━┅╾""",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                f"Bot isn't able to send message to @{SUPPORT_CHAT}, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    test_handler = CommandHandler("test", test, run_async=True)
    start_handler = CommandHandler("start", start, run_async=True)

    help_handler = CommandHandler("help", get_help, run_async=True)
    help_callback_handler = CallbackQueryHandler(
        help_button, pattern=r"help_.*", run_async=True
    )

    settings_handler = CommandHandler("settings", get_settings, run_async=True)
    settings_callback_handler = CallbackQueryHandler(
        settings_button, pattern=r"stngs_", run_async=True
    )

    about_callback_handler = CallbackQueryHandler(
        kynan_about_callback, pattern=r"kynan_", run_async=True
    )

    source_callback_handler = CallbackQueryHandler(
        Source_about_callback, pattern=r"source_", run_async=True
    )

    donate_handler = CommandHandler("donate", donate, run_async=True)
    migrate_handler = MessageHandler(
        Filters.status_update.migrate, migrate_chats, run_async=True
    )

    dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info(f"{dispatcher.bot.first_name} started, Using webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info(f"{dispatcher.bot.first_name} started, Using long polling.")
        updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
