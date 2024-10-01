import os
import json
from peewee import *
import sqlite3
from dotenv import load_dotenv

load_dotenv()

db = os.getenv("DB_URL")


db_f = SqliteDatabase("keyword_filtered.db")


class Posts(Model):
    title = CharField()
    description = TextField()
    url = CharField()

    class Meta:
        database = db_f


db_f.connect()

keywords = [
    "shipping",
    "delivery",
    "order",
    "package",
    "tracking",
    "shipment",
    "arrived",
    "lost",
    "damaged",
    "delayed",
    "late",
    "never",
    "missing",
    "refund",
    "return",
    "wrong",
    "incorrect",
    "change",
    "update",
    "cancel",
    "reschedule",
    "rebook",
    "reorder",
    "reissue",
    "renew",
    "revert",
    "revoke",
    "revalidate",
    "revisit",
]


def filter_with_keywords():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT * FROM my_table")
    rows = c.fetchall()
    conn.close()
    cnt = 0
    i = 0
    for row in rows:
        i += 1
        if i % 1000 == 0:
            print("i: ", i)
        key_count = 0
        for keyword in keywords:
            if keyword in row[2]:
                key_count += 1
            if key_count >= 10:
                cnt += 1

                Posts.create(title=row[1], description=row[2], url=row[3])

                break
    print("Total filtered: ", cnt)


filter_with_keywords()
