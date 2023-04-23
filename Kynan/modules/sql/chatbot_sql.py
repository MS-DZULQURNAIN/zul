import threading

from sqlalchemy import Column, String

from Kynan.modules.sql import BASE, SESSION


class KynanChats(BASE):
    __tablename__ = "kynan_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


KynanChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_kynan(chat_id):
    try:
        chat = SESSION.query(KynanChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()


def set_kynan(chat_id):
    with INSERTION_LOCK:
        Kynanchat = SESSION.query(KynanChats).get(str(chat_id))
        if not Kynanchat:
            Kynanchat = KynanChats(str(chat_id))
        SESSION.add(Kynanchat)
        SESSION.commit()


def rem_kynan(chat_id):
    with INSERTION_LOCK:
        Kynanchat = SESSION.query(KynanChats).get(str(chat_id))
        if Kynanchat:
            SESSION.delete(Kynanchat)
        SESSION.commit()
