import os
import subprocess
import time
import hashlib

from flask import Blueprint
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import abort
from flask import current_app
from flask import make_response

from loaders import IMAGES_EXTENSIONS
import base64



bp = Blueprint("mainviews", __name__)


def hash_password(secretkey, password):
    hashed=hashlib.md5()
    hashed.update(secretkey+password)
    return hashed.hexdigest()


@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method=="GET":
        if "online" in session:
            return redirect("/info")
        pip=session["conf"]["global_ip"]
        lip=session["conf"]["local_ip"]
        return render_template("index.html", pip=pip, lip=lip)

    elif request.method=="POST":
        haslo=request.form.get("pass","")

        if "conf" in session:
            passwords=[session["conf"]["password"],
                session["conf"]["gen_password"]]
        else:
            passwords=[]

        if not haslo:
            msg="<script>alert('Enter password')</script>"
            return render_template("index.html", msg=msg)

        dane_poprawne=False
        #Get hashed password
        hashed=hash_password(
                current_app.config["SECRET_KEY"],
                haslo)
        del haslo
        #Check predefinied and generated password
        for password in passwords:
            if password==hashed:
                dane_poprawne=True
                session["shared"]=False
                break
        #Check shared password
        if hashed==session["conf"]["gen_password_shared"]:
            dane_poprawne=True
            session["shared"]=True
        #Show incorrect password message
        if not dane_poprawne:
            msg="<script>alert('Invalid password')</script>"
            return render_template("index.html", msg=msg)

        session["online"]=1
        session["sciezka"]=os.path.expanduser("~")
        return redirect("/info")


@bp.route("/logout", methods=["GET"])
def logout():
    if "online" not in session:
        return redirect("/")
    del session["online"]
    return redirect("/")

@bp.route("/settings", methods = ["get"])
def settingsview():
    if "online" not in session:
        return redirect("/")
    return render_template("settings.html")

@bp.route("/info", methods = ["get"])
def infoview():
    if "online" not in session:
        return redirect("/")
    currtime=time.strftime("%T %Z", time.localtime())
    currdate=time.strftime("%A %x", time.localtime())
    uptime=subprocess.check_output("uptime")
    return render_template("info.html",
        time=currtime,
        date=currdate,
        uptime=uptime,
        )
@bp.route("/screens", methods = ["get"])
def screenview():
    if "online" not in session:
        return redirect("/")
    if session["shared"]:
        return redirect("/")
    try:
        os.system("cd ~ && mkdir screens")
    except: pass
    #get path
    imagespath=os.path.expanduser('~')+"/screens/"
    #get files
    pathgen=os.listdir(imagespath)
    images=[]
    for pp in pathgen:
        fpath=os.path.join(imagespath, pp)
        if os.path.isfile(fpath):
            ext=os.path.splitext(pp)[1].lower()
            if ext in IMAGES_EXTENSIONS:
                images.append([base64.b64encode(fpath), os.path.basename(fpath)])
    return render_template("screen.html", images=images)
    
@bp.route("/screentake", methods = ["get"])
def screentake():
    if "online" not in session:
        return redirect("/")
    if session["shared"]:
        return redirect("/")
    try:
        os.system("cd ~ && mkdir screens")
    except: pass
    os.system("scrot ~/screens/%Y-%m-%d-%T-screenshot.png")
    return redirect("/screens")
    
@bp.route("/screendelete", methods = ["get"])
def screendel():
    if "online" not in session:
        return redirect("/")
    if session["shared"]:
        return redirect("/")
    try:
        os.system("cd ~ && mkdir screens")
    except: pass
    os.system("rm -r ~/screens/*")
    return redirect("/screens")


@bp.route("/settheme", methods = ["get"])
def settheme():
    if "online" not in session:
        return redirect("/")
    theme=request.args.get("theme", 0)
    resp=make_response(redirect('/settings'))
    resp.set_cookie("theme", theme)
    return resp

@bp.route("/setlang", methods = ["get"])
def setlang():
    if "online" not in session:
        return redirect("/")
    lang=request.args.get("lang", "en")
    resp=make_response(redirect('/settings'))
    resp.set_cookie("lang", lang)
    return resp
