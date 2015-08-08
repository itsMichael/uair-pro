import os
import subprocess
import base64

from flask import Blueprint
from flask import request
from flask import render_template
from flask import session
from flask import abort
from flask import redirect

from loaders import load_playlist
from loaders import IMAGES_EXTENSIONS

bp = Blueprint("imagesviews", __name__)

IMAGES_PATH=os.path.expanduser("~/Pictures")


@bp.route("/gallery", methods = ["get"])
def galleryview():
    if "online" not in session:
        return redirect("/")
    if session["shared"]:
        return redirect("/")
    #get path
    imagespath=session["conf"].get("images_path",IMAGES_PATH)
    #get files
    pathgen=os.listdir(imagespath)
    images=[]
    for pp in pathgen:
        fpath=os.path.join(imagespath, pp)
        if os.path.isfile(fpath):
            ext=os.path.splitext(pp)[1].lower()
            if ext in IMAGES_EXTENSIONS:
                images.append([base64.b64encode(fpath), os.path.basename(fpath)])
    return render_template("gallery.html", images=images)
