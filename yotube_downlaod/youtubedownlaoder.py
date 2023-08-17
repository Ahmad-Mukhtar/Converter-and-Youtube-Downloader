from pytube import YouTube


def DownloadVideo(link):
    youtubeObject = YouTube(link)
    res_list = youtubeObject.streams.filter(progressive=True)
    for stream in res_list:
        if stream.resolution == "360p":
            youtubeObject = youtubeObject.streams.get_by_resolution(stream.resolution)
            break
    try:
        youtubeObject.download()
    except Exception as err:
        print("An error has occurred")
        return err, 500
    print("Download is completed successfully")
    return youtubeObject.default_filename, 200
