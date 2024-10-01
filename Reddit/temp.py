import os
from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    TextField,
    IntegerField,
    ForeignKeyField,
    SQL,
)

db = SqliteDatabase(os.getenv("DB_URL"))


class Posts(Model):
    title = CharField()
    description = TextField()
    url = CharField()

    class Meta:
        database = db


class CurrentPostIds(Model):
    post_id = IntegerField()
    previous_post_id = IntegerField()

    class Meta:
        database = db


class TotalPosts(Model):
    total_posts = IntegerField(default=0)

    class Meta:
        database = db


class Categories(Model):
    category = CharField()
    key = IntegerField()

    class Meta:
        database = db


class PostCategories(Model):
    post = ForeignKeyField(Posts, backref="categories", on_delete="CASCADE")
    category = ForeignKeyField(Categories, backref="posts", on_delete="CASCADE")

    class Meta:
        database = db
        primary_key = False
        constraints = [SQL('UNIQUE(post_id, category_id)')]


db.connect()
# db.create_tables([Posts, CurrentPostIds, TotalPosts, Categories, PostCategories])

cur = Categories.select()
for c in cur:
    print(c.category, c.key)


# categories = Categories.select()
# for category in categories:
#     print(category.category, category.key)

# db.create_tables([TotalPosts])

# cur = TotalPosts.get_by_id(1)
# cur.total_posts = 0
# posts = Posts.select().limit(200)

# for post in posts:
#     print(post.id)
#     if post.id > 861:
#         break
#     cur.total_posts += 1
# print(cur.total_posts)
# cur.save()


# LOOK FOR PARTICULAR POST

# cur = Posts.get_by_id(2)
# with open("temp.txt", "w") as f:
#     f.write(cur.title)
#     f.write("\n")
#     # f.write("".join(cur.description.split(" ")[:250]))
#     f.write(cur.description)
#     print(len(cur.description.split(' ')))

# PRINT TOP 10 POSTS ID

# for post in Posts.select().limit(200):
#     print(post.id)


db.close()