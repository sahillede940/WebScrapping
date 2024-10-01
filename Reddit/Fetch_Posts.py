import praw
from dotenv import load_dotenv
import os
import json
import re
from search_queries import search_queries as search_keywords

load_dotenv()

reddit = praw.Reddit(
    client_id=os.environ.get("CLIENT_ID"),
    client_secret=os.environ.get("CLIENT_SECRET"),
    user_agent="Sahil",
    username="Substantial-Gate-218",
)

if not os.path.exists("./Reddit/output"):
    os.makedirs("./Reddit/output")

# check is file ./Reddit/track_keywords_no is present
if not os.path.exists("./Reddit/track_keywords_no"):
    with open("./Reddit/track_keywords_no.txt", "w") as f:
        f.write("0")
directory = "./Reddit/output"
existing_files = set(os.listdir(directory))

subreddit = reddit.subreddit("all")



def clean_filename(title):
    title = re.sub(r'[<>:"/\\|?*]', "_", title)
    max_length = 255
    if len(title) > max_length:
        title = title[:max_length]
    filename = f"./Reddit/output/{title}.json"
    return filename, title + ".json"

def get_posts(i, j, search_query):
    try:
        for submission in subreddit.search(search_query, limit=None):
            i += 1
            j += 1
            filename, title = clean_filename(submission.title if hasattr(submission, "title") else "")
            if title in existing_files:
                print(f"Already saved: {title[:20]}")
                continue

            data = {
                "title": submission.title if hasattr(submission, "title") else "",
                "description": (
                    submission.selftext if hasattr(submission, "selftext") else ""
                ),
                "metadata": {
                    "author": (
                        getattr(submission.author, "name", "Unknown Author")
                        if submission.author
                        else "Unknown Author"
                    ),
                    "url": getattr(submission, "url", "Unknown URL"),
                    "created": getattr(submission, "created_utc", "Unknown Time"),
                },
            }

            # Ensure submission.comments exists and is iterable
            comments = (
                submission.comments.list()
                if hasattr(submission, "comments") and submission.comments
                else []
            )

            for comment in comments:
                comment_body = getattr(comment, "body", "")
                if (
                    comment_body
                    and isinstance(comment_body, str)
                ):
                    data["description"] += f"\n\n{comment_body}"

            data["title"] = (
                data["title"].replace('"', "'")
                if isinstance(data["title"], str)
                else ""
            )
            data["description"] = (
                data["description"].replace('"', "'")
                if isinstance(data["description"], str)
                else ""
            )

            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                    print(f"Saved: {title[:20]}")
                    existing_files.add(title)

            except Exception as e:
                print("ERROR: ", title[:20], e)
                continue
        print(f"Total posts for {search_query}: {j}")

    except Exception as e:
        print(f"Error: {e}")
        print(f"Total posts: {i}")
        print(f"Total posts saved: {j}")


count = 0
start_from = 0
print(f"Starting from: {start_from}")

try:
    for keyword in search_keywords:
        if count < start_from:
            count += 1
            continue
        print('-'*100)
        print(f"Keyword: {keyword}")
        print('-'*100)
        with open("./Reddit/track_keywords_no.txt", "w") as f:
            f.write(str(count))
        i = 0
        j = 0
        get_posts(i, j, keyword)
        print(f"Total posts for {keyword}: {j}")
        count += 1
except Exception as e:
    print(f"Error: {e}")
    print(f"Total posts: {i}")
    print(f"Total posts saved: {j}")
