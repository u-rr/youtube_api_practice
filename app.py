import os
from pymongo import MongoClient
from flask import Flask, render_template
from flask_httpauth import HTTPBasicAuth
from get_collection import count_videos, get_videos_id_top_viewcount, get_videos_id_latest_published

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "user": "psuN6KPb",
}

# USERNAME = os.environ["USERNAME"]
# PASSWORD = os.environ["PASSWORD"]
# mongo_client = MongoClient(f"mongodb://{USERNAME}:{PASSWORD}@mongo:27017/")
# collection = mongo_client.youtube.videos

DB_URL = os.environ["DB_URL"]
BASIC_USER = os.environ["BASIC_USER"]
BASIC_PASSWORD = os.environ["BASIC_PASSWORD"]
mongo_client = MongoClient(DB_URL)
collection = mongo_client.youtube.videos
search_words = ["岸優太", "平野紫耀", "永瀬廉", "神宮寺勇太", "髙橋海人", "king&prince"]

users = {
    BASIC_USER: BASIC_PASSWORD,
}


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


@app.route("/")
@auth.login_required
def index(collection=collection, search_words=search_words):

    # count_videos = main()
    count_video = count_videos(collection, search_words)

    return render_template("index.html", title="youtubeAPIアプリ", count_video=count_video)


# メンバー名を取得して対応する動画を表示
@app.route("/<name>")
def show_videos(collection=collection, name=None):
    videos_id_top_viewcount = get_videos_id_top_viewcount(collection, name)  # nameの値はindex.htmlから取得してる
    videos_id_latest_published = get_videos_id_latest_published(collection, name)
    return render_template(
        "view_videos.html",
        title="view_videos",
        videos_id_top_viewcount=videos_id_top_viewcount,
        videos_id_latest_published=videos_id_latest_published,
        name=name,
    )


if __name__ == "__main__":
    app.run(debug=True)
