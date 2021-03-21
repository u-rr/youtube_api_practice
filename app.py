import os
from pymongo import MongoClient
from flask import Flask, render_template
from save_youtube_video_kinpuri import count_videos, get_videos_id

app = Flask(__name__)

YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

mongo_client = MongoClient(f"mongodb://{USERNAME}:{PASSWORD}@mongo:27017/")
collection = mongo_client.youtube.videos
search_words = ["岸優太", "平野紫耀", "永瀬廉", "神宮寺勇太", "髙橋海人", "岩橋玄樹", "king&prince"]


@app.route("/")
def index():

    # count_videos = main()
    count_video = count_videos(collection, search_words)

    return render_template("index.html", title="youtubeAPIアプリ", count_video=count_video)


@app.route("/岸優太")
def show_videos():
    video_id = get_videos_id(collection, search_words)
    return render_template("view_videos.html", title="view_videos", video_id=video_id)


if __name__ == "__main__":
    app.run(debug=True)
