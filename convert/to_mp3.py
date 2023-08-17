import json, tempfile, os
import time

from bson.objectid import ObjectId
import moviepy.editor


def start(videoid, fs_videos, fs_mp3s):
    out = fs_videos.get(ObjectId(videoid))
    generated_filename = "temp_mp3"
    with open(generated_filename, "wb") as local_file:
        local_file.write(out.read())
    audio = moviepy.editor.VideoFileClip(generated_filename).audio
    local_file.close()
    tf_path = tempfile.gettempdir() + "/" + videoid + ".mp3"
    audio.write_audiofile(tf_path)
    audio.close()
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_path)
    return str(fid), 200

