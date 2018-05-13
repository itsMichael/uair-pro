import os
import json


IMAGES_EXTENSIONS=[".jpg", ".jpeg",".png", ".gif", ".tiff", ".bmp",]
MUSIC_EXTENSIONS=[".mp3"]

def load_playlist(pl_name):
    try:
        path=pl_name+"_playlist.json"
        path=os.path.join(os.path.expanduser("~/"), path)
        data=json.load(open(path))
    except:
        import traceback
        traceback.print_exc()
        return []
    return data


def save_playlist(pl_name, data):
    try:
        path=pl_name+"_playlist.json"
        path=os.path.join(os.path.expanduser("~/"), path)
        json.dump(data, open(path, "w"))
    except:
        import traceback
        traceback.print_exc()
        return False
    return True


def save_config(data):
    json.dump(data, open (os.path.expanduser("~/.u-air.json"), "w"))


def load_config():
    data = {}
    data["local_ip"] = "127.0.0.1"
    data["global_ip"] = "0.0.0.0"
    data["port"] = 5000
    data["lang"] = "en"
    data["startup"] = False
    data["password"] = ""
    data["gen_password"] = ""
    data["gen_password_shared"] = ""
    data["status"] = 0
    data["images_path"] = os.path.expanduser("~/Pictures")

    #load config from file
    try:
        data = json.load(open (os.path.expanduser("~/.u-air.json")))
    except:pass
    return data
