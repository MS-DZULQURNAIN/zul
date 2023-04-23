import time
import os
import re
import codecs
from typing import List
from random import randint
from Kynan.modules.helper_funcs.chat_status import user_admin
from Kynan.modules.disable import DisableAbleCommandHandler
from Kynan import (
    dispatcher,
    WALL_API,
)
import requests as r
import wikipedia
from requests import get, post
from telegram import (
    Chat,
    ChatAction,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Message,
    MessageEntity,
    TelegramError,
)
from telegram.error import BadRequest
from telegram.ext.dispatcher import run_async
from telegram.ext import CallbackContext, Filters, CommandHandler
from Kynan import StartTime
from Kynan.modules.helper_funcs.chat_status import sudo_plus
from Kynan.modules.helper_funcs.alternate import send_action, typing_action

MARKDOWN_HELP = f"""
➣ Markdown is a very powerful formatting tool supported by telegram. {dispatcher.bot.first_name} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.
ᐉ <code>_italic_</code>: membungkus teks dengan '_' akan menghasilkan teks miring
ᐉ <code>*bold*</code>: membungkus teks dengan '*' akan menghasilkan teks tebal
ᐉ <code>`code`</code>: membungkus teks dengan '`' akan menghasilkan teks monospace, juga dikenal sebagai 'code'
ᐉ <code>[beberapa teks](beberapaURL)</code>: ini akan membuat tautan - pesan hanya akan ditampilkan <code>beberapa teks</code>, \
dan mengetuknya akan membuka halaman di <code>beberapaURL</code>.
➣ <b>Contoh:</b><code>[tes](contoh.com)</code>
ᐉ <code>[teks tombol](buttonurl:beberapaURL)</code>: ini adalah peningkatan khusus untuk memungkinkan pengguna memiliki telegram \
tombol di penurunan harga mereka. <code>teks tombol</code> akan menjadi apa yang ditampilkan pada tombol, dan <code>someurl</code> \
akan menjadi url yang dibuka.
➣ <b>Contoh:</b> <code>[Ini adalah tombol](buttonurl:example.com)</code>
➣ Jika Anda ingin beberapa tombol pada baris yang sama, gunakan :same, seperti itu:
<code>[satu](buttonurl://contoh.com)
[dua](buttonurl://google.com:same)</code>
➣ Ini akan membuat dua tombol pada satu baris, bukan satu tombol per baris.
➣ Ingatlah bahwa pesan Anda <b>MUST</b> berisi beberapa teks selain hanya sebuah tombol!
"""


@user_admin
def echo(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    else:
        message.reply_text(
            args[1], quote=False, parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    message.delete()


def markdown_help_sender(update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Coba teruskan pesan berikut kepada saya, dan Anda akan melihat, dan Gunakan #test!"
    )
    update.effective_message.reply_text(
        "/save tes Ini adalah tes markdown. _italics_, *bold*, code, "
        "[URL](contoh.com) [tombol](buttonurl://github.com/Onlymeriz) "
        "[tombol2](buttonurl://google.com:same)"
    )


def markdown_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        update.effective_message.reply_text(
            "Hubungi saya di pm",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Bantuan Markdown",
                            url=f"t.me/{context.bot.username}?start=markdownhelp",
                        )
                    ]
                ]
            ),
        )
        return
    markdown_help_sender(update)


def wiki(update: Update, context: CallbackContext):
    kueri = re.split(pattern="wiki", string=update.effective_message.text)
    wikipedia.set_lang("en")
    if len(str(kueri[1])) == 0:
        update.effective_message.reply_text("Masukkan kata kunci!")
    else:
        try:
            pertama = update.effective_message.reply_text("🔄 Memuat...")
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔧 Info lebih lanjut...",
                            url=wikipedia.page(kueri).url,
                        )
                    ]
                ]
            )
            context.bot.editMessageText(
                chat_id=update.effective_chat.id,
                message_id=pertama.message_id,
                text=wikipedia.summary(kueri, sentences=10),
                reply_markup=keyboard,
            )
        except wikipedia.PageError as e:
            update.effective_message.reply_text(f"⚠ Error: {e}")
        except BadRequest as et:
            update.effective_message.reply_text(f"⚠ Error: {et}")
        except wikipedia.exceptions.DisambiguationError as eet:
            update.effective_message.reply_text(
                f"⚠ Error\n Ada terlalu banyak permintaan! Ekspresikan lebih banyak!\nKemungkinan hasil kueri:\n{eet}"
            )


@send_action(ChatAction.UPLOAD_PHOTO)
def wall(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    msg = update.effective_message
    msg_id = update.effective_message.message_id
    args = context.args
    query = " ".join(args)
    if not query:
        msg.reply_text("Please enter a query!")
        return
    caption = query
    term = query.replace(" ", "%20")
    json_rep = r.get(
        f"https://wall.alphacoders.com/api2.0/get.php?auth={WALL_API}&method=search&term={term}"
    ).json()
    if not json_rep.get("success"):
        msg.reply_text("An error occurred!")

    else:
        wallpapers = json_rep.get("wallpapers")
        if not wallpapers:
            msg.reply_text("No results found! Refine your search.")
            return
        index = randint(0, len(wallpapers) - 1)  # Choose random index
        wallpaper = wallpapers[index]
        wallpaper = wallpaper.get("url_image")
        wallpaper = wallpaper.replace("\\", "")
        context.bot.send_photo(
            chat_id,
            photo=wallpaper,
            caption="Preview",
            reply_to_message_id=msg_id,
            timeout=60,
        )
        context.bot.send_document(
            chat_id,
            document=wallpaper,
            filename="wallpaper",
            caption=caption,
            reply_to_message_id=msg_id,
            timeout=60,
        )


__help__ = """
➣ *Perintah yang tersedia:*
ᐉ /markdownhelp*:* ringkasan singkat tentang cara kerja penurunan harga di telegram - hanya dapat dipanggil dalam obrolan pribadi
ᐉ /paste*:* Menyimpan konten yang dibalas ke `nekobin.com` dan membalas dengan url
ᐉ /react*:* Bereaksi dengan reaksi acak 
ᐉ /ud <word>*:* Ketik kata atau ekspresi yang ingin Anda cari gunakan
ᐉ /reverse*:* Melakukan pencarian gambar terbalik dari media yang dibalas.
ᐉ /wiki <pertanyaan>*:* wikipedia permintaan Anda
ᐉ /wall <pertanyaan>*:* dapatkan wallpaper dari wall.alphacoders.com
ᐉ /cash*:* pengonversi mata uang
➣ Contoh:
 `/cash 1 USD INR`  
      _OR_
 `/cash 1 usd inr`
 Keluaran: `1.0 USD = 75.505 INR`
➣ *Modul Musik:*
ᐉ /song or /song (query): unduh video dari youtube
ᐉ /music or /song (query): unduh lagu dari server yt. (API BASED)
ᐉ /lyrics (song name) : Plugin ini mencari lirik lagu dengan nama lagu.
"""

ECHO_HANDLER = DisableAbleCommandHandler(
    "echo", echo, filters=Filters.chat_type.groups, run_async=True)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, run_async=True)
WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki)
WALLPAPER_HANDLER = DisableAbleCommandHandler("wall", wall, run_async=True)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(WIKI_HANDLER)
dispatcher.add_handler(WALLPAPER_HANDLER)

__mod_name__ = "Extras"
__command_list__ = ["id", "echo", "wiki", "wall"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
    WIKI_HANDLER,
    WALLPAPER_HANDLER,
]
