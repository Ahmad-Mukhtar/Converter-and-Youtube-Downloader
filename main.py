import os

import gridfs
from bson.objectid import ObjectId
from flask import Flask, request, send_file
from flask_cors import CORS
from flask_pymongo import PyMongo

from convert import to_mp3
from storage import util
from yotube_downlaod import youtubedownlaoder

server = Flask(__name__)
CORS(server)
mongo_video = PyMongo(server, uri="mongodb://localhost:27017/videos")
mongo_mp3 = PyMongo(server, uri="mongodb://localhost:27017/mp3s")
mongo_youtube = PyMongo(server, uri="mongodb://localhost:27017/youtube")

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)
mongo_youtube_db = mongo_youtube.db


@server.route("/")
def index():
    return "Hello"


@server.route("/youtubedownload", methods=["GET"])
def download_youtube_video():
    url = request.args.get("uid")
    delete_previous_files()
    name, res = youtubedownlaoder.DownloadVideo(url)
    if res == 200:
        f = open(name, "rb")
        print(name)
        mongo_youtube_db.filenames.insert_one({'filename': name})
        return send_file(f, download_name=f'{name}')
    else:
        print(name)
        return "internal server error", 500


@server.route("/upload", methods=["POST"])
def upload():
    global id
    if len(request.files) > 1 or len(request.files) < 1:
        return "exactly one file required", 400
    for _, f in request.files.items():
        id, res = util.upload(f, fs_videos)
        if res == 500:
            return id, res
    delete_mp3s_files()
    mp3_id, res = to_mp3.start(str(id), fs_videos, fs_mp3s)
    if res == 200:
        fs_videos.delete(ObjectId(str(id)))
        return mp3_id, res
    return "conversion error", 500


@server.route("/download", methods=["GET"])
def download():
    fid_string = request.args.get("fid")
    if not fid_string:
        return "fid is require", 400
    try:
        out = fs_mp3s.get(ObjectId(fid_string))
        return send_file(out, download_name=f'{fid_string}.mp3')
    except Exception as err:
        print(err)
        return "inetrnal server error", 500


def delete_previous_files():
    result = mongo_youtube_db.filenames.find()
    for doc in result:
        os.remove(doc['filename'])
        mongo_youtube_db.filenames.delete_one({'filename': doc['filename']})


def delete_mp3s_files():
    files = list(fs_mp3s.find())
    for gridfile in files:
        fs_mp3s.delete(gridfile._id)


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=8080)
