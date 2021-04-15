import os
import logging
import time
from typing import Iterator, List
from apiclient.discovery import build
from pymongo import MongoClient, ReplaceOne, DESCENDING
from pymongo.collection import Collection

YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

logging.getLogger("googleapiclient.discovery_cashe").setLevel(logging.ERROR)


def main():
    mongo_client = MongoClient(f"mongodb://{USERNAME}:{PASSWORD}@mongo:27017/")
    collection = mongo_client.youtube.videos

    search_words = ["岸優太", "平野紫耀", "永瀬廉", "神宮寺勇太", "髙橋海人", "岩橋玄樹", "king&prince"]
    for search_word in search_words:
        for items_per_page in search_videos(search_word):
            save_to_mongodb(collection, items_per_page)
            time.sleep(1)


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


def save_to_mongodb(collection: Collection, items: List[dict]):
    for item in items:
        item["_id"] = item["id"]

        for key, value in item["statistics"].items():
            item["statistics"][key] = int(value)

    operations = [ReplaceOne({"_id": item["_id"]}, item, upsert=True) for item in items]
    result = collection.bulk_write(operations)
    # logging.info(result)
    logging.info(f"Upserted {result.upserted_count} documents.")


def count_videos(collection: Collection, search_words: list):
    members_count_dict = {}
    for search_word in search_words:
        members_count_dict[search_word] = collection.count({"snippet.title": {"$regex": search_word, "$options": "i"}})
    members_count_dict_sorted = sorted(members_count_dict.items(), key=lambda x: x[1], reverse=True)
    return members_count_dict_sorted


def show_top_videos(collection: Collection):
    for item in collection.find().sort("statistics.viewCount", DESCENDING).limit(5):
        print(item["statistics"]["viewCount"], item["snippet"]["title"])


# 再生数が多い順にソートして、最初の5件のidを取得する
def get_videos_id_top_viewcount(collection: Collection, name: str):
    # for search_word in search_words:
    #     for item in collection.find({"snippet.title": {"$regex": search_word, "$options": "i"}}).sort("statistics.viewCount", DESCENDING).limit(5):
    for item in collection.find({"snippet.title": {"$regex": name, "$options": "i"}}).sort("statistics.viewCount", DESCENDING).limit(5):
        yield item["id"]


# 投稿数が新しい順にソートして最初の5件のidを取得する
def get_videos_id_latest_published(collection: Collection, name: str):
    for item in collection.find({"snippet.title": {"$regex": name, "$options": "i"}}).sort("snippet.publishedAt", DESCENDING).limit(5):
        yield item["id"]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
