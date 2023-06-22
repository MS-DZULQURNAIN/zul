# Create a new config.py or rename this to config.py file in same dir and import, then extend this class.
import json
import os


def get_user_list(config, key):
    with open("{}/Kynan/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


# Create a new config.py or rename this to config.py file in same dir and import, then extend this class.
class Config(object):
    LOGGER = True
    # REQUIRED
    # Login to https://my.telegram.org and fill in these slots with the details given by it

    API_ID = 16452568  # integer value, dont use ""
    API_HASH = 'f936697c5c9e5bffd433babef7a4e4c9'
    TOKEN = "6049689032:AAH_Nmx-icacIb5FEAolpLdyiUnZjH11SU4"  # This var used to be API_KEY but it is now TOKEN, adjust accordingly.
    OWNER_ID = 1337085565  # If you dont know, run the bot and do /id in your private chat with it, also an integer
    OWNER_USERNAME = "MSDZULQRNN"
    SUPPORT_CHAT = "envSample"  # Your own group for support, do not add the @
    JOIN_LOGGER = (
        -1001620073174
    )  # Prints any new group the bot is added to, prints just the name and ID.
    EVENT_LOGS = (
        -1001935424604
    )  # Prints information like gbans, sudo promotes, AI enabled disable states that may help in debugging and shit
    ERROR_LOGS = "-1001935424604"
    OPENWEATHERMAP_ID = "awwww"
    TEMP_DOWNLOAD_DIRECTORY = "./"
    REM_BG_API_KEY = "1xGVDKGrSKBKwp76NPnWmijt"
    CASH_API_KEY = "ZMOE8Q6BE25J7BEU"
    TIME_API_KEY = "J1BBEIOV38CZ"
    LASTFM_API_KEY = "awowo"
    CF_API_KEY = "awowo"
    STRING_SESSION = "1BVtsOIIBu2JG6TTJRo7nZmCPdssdnt6KOTwogpzdE5kXgJWQ6Zlv5Ti4PxYjxOdkOgAP69T8oryYWXYojfVHclTCUud5-4B8CY1M2kaUr37CoPkaQh1fR5zEgx0Y1oiPt8ycXTRz5p1kXVNHvq12RbuAcdD5mtW43hjqokefbEipPeyDL14R9Z5PMuxYwy54MAdVEcDrKsYCISwiIbLYqO6ZV6HzqlVRzGaahGXEb7uj2AF1fmDlm2E7Od3wuAuv0i_7rfT6MiPeFZ5matdqfmo9eqidcFtGC7CWRmXBZSoABIY6-cu3AVT4Ns-G-MT6XPzb8O9-HTmGfCDV6R8liFChuAitnxQ="

    #TAMBAHAN
    ARQ_API_KEY = "UHZKNH-IRFVEV-ANNQWQ-XMZKFE-ARQ"
    ARQ_API_URL = "http://arq.hamker.dev"
    BOT_USERNAME = "DzMusicRobot"
    
    # RECOMMENDED
    SQLALCHEMY_DATABASE_URI = "postgres://bqlkbhhl:YG-iSQ5u5g-6l2MJ-NRgEi-yPJnq3S-H@rajje.db.elephantsql.com/bqlkbhhl"  # needed for any database modules
    MONGO_DB_URI = "mongodb+srv://avel:tmp0@aveltmp.nqyqy6h.mongodb.net/aveltmp?retryWrites=true&w=majority"
    LOAD = []
    OPENAI_API_KEY = "awowo"
    USE_CHATGPT_API: True
    ALLOWED_TELEGRAM_USERNAMES = []
    CHATGPT_PRICE_PER_1000_TOKENS = 0.002
    GPT_PRICE_PER_1000_TOKENS = 0.02
    WHISPER_PRICE_PER_1_MIN = 0.006
    NEW_DIALOG_TIMEOUT = 600
    ENABLE_MESSAGE_STREAMING = True
    NO_LOAD = ["rss", "cleaner", "connection", "math"]
    WEBHOOK = False
    INFOPIC = True
    URL = None
    SPAMWATCH_API = "awowo"  # go to support.spamwat.ch to get key
    SPAMWATCH_SUPPORT_CHAT = "@SpamWatchSupport"

    # OPTIONAL
    ##List of id's -  (not usernames) for users which have sudo access to the bot.
    DRAGONS = get_user_list("elevated_users.json", "sudos")
    ##List of id's - (not usernames) for developers who will have the same perms as the owner
    DEV_USERS = get_user_list("elevated_users.json", "devs")
    ##List of id's (not usernames) for users which are allowed to gban, but can also be banned.
    DEMONS = get_user_list("elevated_users.json", "supports")
    # List of id's (not usernames) for users which WONT be banned/kicked by the bot.
    TIGERS = get_user_list("elevated_users.json", "tigers")
    WOLVES = get_user_list("elevated_users.json", "whitelists")
    DONATION_LINK = None  # EG, paypal
    CERT_PATH = None
    PORT = 443
    DEL_CMDS = True  # Delete commands that users dont have access to, like delete /ban if a non admin uses it.
    STRICT_GBAN = True
    WORKERS = (
        8  # Number of subthreads to use. Set as number of threads your processor uses
    )
    BAN_STICKER = ""  # banhammer marie sticker id, the bot will send this sticker before banning or kicking a user in chat.
    ALLOW_CHATS = True
    ALLOW_EXCL = True  # Allow ! commands as well as / (Leave this to true so that blacklist can work)
    WALL_API = (
        "awoo"  # For wallpapers, get one from https://wall.alphacoders.com/api.php
    )
    AI_API_KEY = "awoo"  # For chatbot, get one from https://coffeehouse.intellivoid.net/dashboard
    BL_CHATS = []  # List of groups that you want blacklisted.
    SPAMMERS = None


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
