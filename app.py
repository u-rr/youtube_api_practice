from flask import Flask, render_template
from save_youtube_video_practice import main

app = Flask(__name__)


@app.route("/")
def index():
    name = "Hoge"
    count_videos = main()

    return render_template("index.html", title="youtubeAPIアプリ", name=name, count_videos=count_videos)


if __name__ == "__main__":
    app.run(debug=True)
