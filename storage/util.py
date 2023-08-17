

def upload(f, fs):
    try:
        fid = fs.put(f)
        return fid,200
    except Exception as err:
        print(err)
        return "internal server error", 500

