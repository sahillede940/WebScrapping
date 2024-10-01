from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from peewee import (
    Model,
    IntegerField,
    SqliteDatabase,
    CharField,
    TextField,
    ForeignKeyField,
)
from contextlib import asynccontextmanager

db = SqliteDatabase("Posts.db")


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


class PostIdResponse(BaseModel):
    post_id: int


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.connect()
    db.create_tables([CurrentPostIds])
    yield
    db.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Define the GET route to fetch the current post ID
@app.get("/get_current_post_id")
def get_current_post_id():
    try:
        current_post = CurrentPostIds.get_by_id(1)
        total_posts = TotalPosts.get_by_id(1)
        if not current_post:
            raise HTTPException(status_code=404, detail="No post found")

        return {
            "post_id": current_post.post_id,
            "total_posts_filtered": total_posts.total_posts,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_post_id/{post_id}")
def get_post_id(post_id: int):
    try:
        post = Posts.get_by_id(post_id)
        # Get the categories associated with the post
        categories = [category.category.category for category in post.categories]
        return {"title": post.title, "url": post.url, "categories": categories}
    except Posts.DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_posts")
def get_posts(limit: int = 10, offset: int = 0):
    try:
        posts = Posts.select().limit(limit).offset(offset)
        total_posts = Posts.select().count()
        post_list = []
        for post in posts:
            post_list.append(
                {
                    "id": post.id,
                    "title": post.title,
                    "url": post.url,
                    "description": post.description,
                }
            )
        return {"total_posts": total_posts, "posts": post_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_categories")
def get_categories():
    try:
        categories = Categories.select()
        category_list = []
        for category in categories:
            category_list.append({"category": category.category, "key": category.key})
        return category_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
