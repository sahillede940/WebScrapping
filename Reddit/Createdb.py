dir = "Reddit/output"

from peewee import *
import os
import json
import sqlite3

# I want to measure time taken to insert 1000 records
import time


db = SqliteDatabase("Reddit/Posts.db")


class Posts(Model):
    title = CharField()
    description = TextField()
    url = CharField()

    class Meta:
        database = db


db.connect()
db.create_tables([Posts])
i = 0
start_time = time.time()
for file in os.listdir(dir):
    if file.endswith(".json"):
        i += 1
        with open(f"{dir}/{file}", "r") as f:
            post = json.load(f)
            Posts.create(
                title=post["title"],
                description=post["description"],
                url=post["metadata"]["url"],
            )

        if i % 1000 == 0:
            print(f"Time {i}: {(time.time() - start_time).__round__(2)}s")

print(f"Time taken to insert  records: {time.time() - start_time}")

db.close()
