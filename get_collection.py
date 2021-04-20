from pymongo import DESCENDING
from pymongo.collection import Collection


# メンバー名ごとの動画数をカウントする
def count_videos(collection: Collection, search_words: list):
    members_count_dict = {}
    for search_word in search_words:
        members_count_dict[search_word] = collection.count({"snippet.title": {"$regex": search_word, "$options": "i"}})
    members_count_dict_sorted = sorted(members_count_dict.items(), key=lambda x: x[1], reverse=True)
    return members_count_dict_sorted


# 再生数が多い順にソートして、最初の5件のidを取得する
def get_videos_id_top_viewcount(collection: Collection, name: str):
    for item in collection.find({"snippet.title": {"$regex": name, "$options": "i"}}).sort("statistics.viewCount", DESCENDING).limit(5):
        yield item["id"]


# 投稿数が新しい順にソートして最初の5件のidを取得する
def get_videos_id_latest_published(collection: Collection, name: str):
    for item in collection.find({"snippet.title": {"$regex": name, "$options": "i"}}).sort("snippet.publishedAt", DESCENDING).limit(5):
        yield item["id"]
