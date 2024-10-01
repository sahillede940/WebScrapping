import re, os
from peewee import SqliteDatabase, Model, CharField, TextField
from dotenv import load_dotenv
import time

load_dotenv()

db = SqliteDatabase(os.getenv("DB_URL"))


class Posts(Model):
    title = CharField()
    description = TextField()
    url = CharField()

    class Meta:
        database = db


url_pattern = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)


def remove_urls(text, id):
    return re.sub(url_pattern, "", text)


def remove_urls_from_db():
    start_time = time.time()
    db.connect()
    i = 0
    for post in Posts.select():
        i += 1
        post.description = remove_urls(post.description, post.id)
        post.save()
        if i % 1000 == 0:
            print(f"Time elapsed: {(time.time() - start_time).__round__(2)}s")

    print(f"Total Time Taken: {(time.time() - start_time).__round__(4)}s")

    db.close()


def check_if_url_removed():
    db.connect()
    for post in Posts.select():
        if re.search(url_pattern, post.description):
            print(f"URL found in post {post.id}")
    db.close()


if __name__ == "__main__":
    remove_urls_from_db()
    check_if_url_removed()
