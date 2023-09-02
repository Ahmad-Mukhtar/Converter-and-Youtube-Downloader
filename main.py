import os

from bson.objectid import ObjectId
from flask import Flask, request, send_file
from flask_cors import CORS
from flask_pymongo import PyMongo
import gridfs
from dotenv import load_dotenv
from convert import to_mp3
from yotube_downlaod import youtubedownlaoder

server = Flask(__name__)
CORS(server)
load_dotenv(".env")
mongo_mp3 = PyMongo(server, uri=os.getenv('MP3_URL'))
mongo_youtube = PyMongo(server, uri=os.getenv('YOUTUBE_URL'))

fs_mp3s = gridfs.GridFS(mongo_mp3.db)
mongo_youtube_db = mongo_youtube.db


@server.route("/")
def index():
    return "Hello"


@server.route("/getResolutions", methods=["GET"])
def get_Resolutions():
    url = request.args.get("uid")
    resolutions, res = youtubedownlaoder.getResolutions(url)
    if res == 200:
        print(resolutions)
        return resolutions,res
    else:
        print(res)
        return "internal server error", 500


@server.route("/youtubedownload", methods=["GET"])
def download_youtube_video():
    url = request.args.get("uid")
    res=request.args.get("res")
    print(res)
    delete_previous_files()
    name, res = youtubedownlaoder.DownloadVideo(url,res)
    if res == 200:
        f = open(name, "rb")
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
    file_items = list(request.files.items()).pop()
    file_name = file_items[0]
    f = file_items[1]
    delete_mp3s_files()
    mp3_id, res = to_mp3.start(file_name, f, fs_mp3s)
    if res == 200:
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
    server.run(debug=False, threaded=True, host="0.0.0.0", port=5000)
