import os
import tempfile

import moviepy.editor


def start(videoname,out, fs_mp3s):
    generated_filename = "temp_mp3"
    with open(generated_filename, "wb") as local_file:
        local_file.write(out.read())
    audio = moviepy.editor.VideoFileClip(generated_filename).audio
    local_file.close()
    tf_path = tempfile.gettempdir() + "/" + videoname + ".mp3"
    audio.write_audiofile(tf_path)
    audio.close()
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_path)
    return str(fid), 200

