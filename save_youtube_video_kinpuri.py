import os
import logging
import time
from typing import Iterator, List
from apiclient.discovery import build
from pymongo import MongoClient, ReplaceOne
from pymongo.collection import Collection


YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
DB_URL = os.environ["DB_URL"]

logging.getLogger("googleapiclient.discovery_cashe").setLevel(logging.ERROR)


def main():
    # ローカルDB
    # mongo_client = MongoClient(f"mongodb://{USERNAME}:{PASSWORD}@mongo:27017/")
    # collection = mongo_client.youtube.videos

    # MongoDB atlas
    mongo_client = MongoClient(DB_URL)
    collection = mongo_client.youtube.videos

    search_words = ["岸優太", "平野紫耀", "永瀬廉", "神宮寺勇太", "髙橋海人", "king&prince"]

    for search_word in search_words:
        for items_per_page in search_videos(search_word):
            save_to_mongodb(collection, items_per_page)
            time.sleep(1)


# youtubeAPIを叩く
def search_videos(query: str, max_pages: int = 5) -> Iterator[List[dict]]:
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    search_request = youtube.search().list(part="id", q=query, type="video", maxResults=50)

    i = 0
    while search_request and i < max_pages:
        search_response = search_request.execute()
        video_ids = [item["id"]["videoId"] for item in search_response["items"]]

        videos_response = youtube.videos().list(part="snippet,statistics", id=",".join(video_ids)).execute()

        yield videos_response["items"]

        search_request = youtube.search().list_next(search_request, search_response)
        i += 1


# DBに保存する
def save_to_mongodb(collection: Collection, items: List[dict]):
    for item in items:
        item["_id"] = item["id"]

        for key, value in item["statistics"].items():
            item["statistics"][key] = int(value)

    operations = [ReplaceOne({"_id": item["_id"]}, item, upsert=True) for item in items]
    result = collection.bulk_write(operations)
    # logging.info(result)
    logging.info(f"Upserted {result.upserted_count} documents.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
