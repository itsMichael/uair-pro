import subprocess
import base64

from flask import Blueprint
from flask import request
from flask import render_template
from flask import session
from flask import abort
from flask import redirect

from loaders import load_playlist, save_playlist

bp = Blueprint("musicviews", __name__)


def encodeutf8(text):
    try:
        text=text.encode("utf-8")
    except:pass
    return text


@bp.route("/music", methods = ["get"])
def musicplayerview():
    if "online" not in session:
        return redirect("/")
    if session["shared"]:
        return redirect("/")
    #load playlist
    playlist=load_playlist("main")
    for song in playlist:
        song[1]=encodeutf8(song[1])
        song[1]=base64.b64encode(song[1])
    #Song in playlist
    # [0] title [1] Full path to file
    return render_template("music.html", playlist=playlist)


@bp.route("/removesong", methods = ["get"])
def removesong():
    if "online" not in session:
        return redirect("/")
    if session["shared"]:
        return redirect("/")
    #get id
    idd=int(request.args.get("id", 0))

    #load playlist
    playlist=load_playlist("main")
    #check pop
    if idd not in range(0, len(playlist)):
        return ""
    #pop song
    playlist.pop(int(idd))
    save_playlist("main", playlist)
    return ""

@bp.route("/movesong", methods = ["get"])
def movesong():
    if "online" not in session:
        return redirect("/")
    if session["shared"]:
        return redirect("/")
    #get id
    idd=int(request.args.get("id", 0))
    movedown=int(request.args.get("down", 0))

    #load playlist
    playlist=load_playlist("main")
    #check pop
    if idd not in range(0, len(playlist)):
        return ""

    #pop song
    if movedown:
        song=playlist.pop(idd)
        playlist.insert(idd+1, song)
    else:
        song=playlist.pop(idd)
        if idd==0:idd=1
        playlist.insert(idd-1, song)

    save_playlist("main", playlist)
    return ""
