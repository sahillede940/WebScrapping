import os
import sqlite3
import json
import re
from dotenv import load_dotenv
from groq import Groq
from typing import List, Tuple, Optional
from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    TextField,
    IntegerField,
    ForeignKeyField,
)

db = SqliteDatabase(os.getenv("DB_URL"))
db.connect()


class CurrentPostIds(Model):
    post_id = IntegerField()
    previous_post_id = IntegerField()

    class Meta:
        database = db


class Posts(Model):
    title = CharField()
    description = TextField()
    url = CharField()

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


DB_PATH = "./Reddit/Posts.db"
MAX_WORDS = 250
SYSTEM_PROMPT = """
You are an AI assistant specialized in analyzing text to determine if it is directly relevant to a parcel shipping-related forum in the US, where users are carriers, vendors, shippers, and logistics companies. Additionally, you are tasked with identifying specific categories from the content. For each post, return a JSON object with two keys:

1. "is_relevant": Set to true if the post is directly relevant to the parcel shipping forum, otherwise false.
2. "categories": An array of category keys based on the content of the post. Select from the following categories:

    - 1: Shipping Insurance
    - 2: Delivery Delays
    - 3: Carrier Issues
    - 4: Customs and Border Regulations
    - 5: Packaging Concerns
    - 6: Tracking Information
    - 7: Payment and Invoicing
    - 8: General Shipping Inquiries
    - 9: Vendor Management
    - 10: Logistics Planning

**Instructions:**
- Analyze the provided post carefully.
- Do **not** include any additional text or explanations—only return the JSON object.
- Return relevant category keys as an array under the "categories" key, leaving it empty if no categories are applicable.
- Ensure the JSON syntax is correct.
- Strictly do not include anything other than the JSON object.

**Format to follow:**
{
  "is_relevant": true,
  "categories": [1, 3]
}
**Post:**
"""


def sanitize_json_string(json_string: str) -> str:
    try:
        sanitized = re.sub(r"[\x00-\x1f\x7f]", "", json_string)
        return sanitized
    except re.error as e:
        print(f"Regex error during sanitization: {e}")
        return json_string  # Return original if sanitization fails


def load_environment_variables() -> bool:
    try:
        load_dotenv()
        if not os.getenv("GROQ_API_KEY"):
            print("Error: GROQ_API_KEY not found in environment variables.")
            return False
        return True
    except Exception as e:
        print(f"Error loading environment variables: {e}")
        return False


def fetch_posts() -> List[Tuple]:
    try:
        cur = CurrentPostIds.get_by_id(1)
        cur_post_id = cur.post_id - 1
        print(f"Starting From Post ID: {cur_post_id + 1}")
        posts = Posts.select().where(Posts.id > cur_post_id)

        return [(post.id, post.title, post.description) for post in posts]
    except sqlite3.Error as e:
        print(f"Error fetching posts: {e}")
        return []


def analyze_post(
    client: Groq, post_content: str, system_prompt: str, max_words: int
) -> Optional[str]:
    try:
        truncated_post = " ".join(post_content.split()[:max_words])
        message_content = system_prompt + truncated_post

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message_content,
                }
            ],
            # model="llama3-8b-8192",
            model="llama-3.1-8b-instant",
        )

        ans = chat_completion.choices[0].message.content
        sanitized_ans = sanitize_json_string(ans)
        return sanitized_ans
    except Exception as e:
        print(f"Error analyzing post: {e}")
        return None


def initialize_groq_client(api_key: str, i: int) -> Optional[Groq]:
    print(f"Using {i+1}th API key")
    try:
        client = Groq(api_key=api_key)
        return client
    except Exception as e:
        print(f"Error initializing Groq client: {e}")
        return None


def main():
    if not load_environment_variables():
        return

    # Initialize Groq client
    api_keys = []
    api_keys.append(os.getenv("GROQ_API_KEY1"))
    api_keys.append(os.getenv("GROQ_API_KEY2"))
    api_keys.append(os.getenv("GROQ_API_KEY3"))
    api_keys.append(os.getenv("GROQ_API_KEY4"))
    api_keys.append(os.getenv("GROQ_API_KEY5"))
    api_keys.append(os.getenv("GROQ_API_KEY6"))
    total_api_keys = len(api_keys)

    i = 0
    client = initialize_groq_client(api_keys[i], i)
    if not client:
        return

    # Fetch posts
    rows = fetch_posts()

    if not rows:
        print("No posts retrieved from the database.")
        return

    # Analyze each post
    for idx, row in enumerate(rows, start=1):
        if idx % 29 == 0:
            i += 1
            api_key = api_keys[i % total_api_keys]
            client = initialize_groq_client(api_key, i % total_api_keys)

        cur = CurrentPostIds.get_by_id(1)
        cur.previous_post_id = cur.post_id
        cur.post_id = row[0]
        cur.save()
        print(f"Current Post ID: {cur.post_id}")

        try:
            post_content = row[2]
            if not isinstance(post_content, str):
                print(f"Row {idx}: Invalid post content. Skipping.")
                continue

            analysis_result = analyze_post(
                client, post_content, SYSTEM_PROMPT, MAX_WORDS
            )
            if analysis_result:
                # Optionally, validate JSON format
                try:
                    json_obj = json.loads(analysis_result)
                    print(json_obj)
                    if json_obj.get("is_relevant") is False:
                        Posts.delete().where(Posts.id == row[0]).execute()
                        print(f"Row {idx}: Post deleted.")
                    else:
                        cur = TotalPosts.get_by_id(1)
                        cur.total_posts += 1
                        cur.save()

                        for category in json_obj.get("categories", []):
                            PostCategories.create(post=row[0], category=category)

                except json.JSONDecodeError as e:
                    print(f"Row {idx}: Invalid JSON response: {e}")
                    print(f"Raw response: {analysis_result}")
            else:
                print(f"Row {idx}: Analysis failed.")
        except IndexError:
            print(f"Row {idx}: Unexpected row format. Skipping.")
        except Exception as e:
            print(f"Row {idx}: Unexpected error: {e}")


if __name__ == "__main__":
    main()
