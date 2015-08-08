#! /usr/bin/python2
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
import json
import os
import sys
import time

from flask import Flask
from flask import session
from flask import request

import mainviews
import terminalviews
import musicviews
import filemanagerviews
import imagesviews
from functions import lt

SECRET_KEY="26365489416208998729485465"

app = Flask(__name__)
app.register_blueprint(mainviews.bp, url_prefix="")
app.register_blueprint(terminalviews.bp, url_prefix="")
app.register_blueprint(musicviews.bp, url_prefix="")
app.register_blueprint(filemanagerviews.bp, url_prefix="")
app.register_blueprint(imagesviews.bp, url_prefix="")

app.debug=True
app.secret_key=SECRET_KEY

conf=json.load(open(os.path.expanduser("~/.u-air.json")))

@app.before_request
def init_config():
    #prevent to much requests DDOS attack
    #ct=int(time.time())
    #if ct==session.get("lastrequest",ct):
    #    session['numrequests']=session.get("numrequests",1)+1
    #else:
    #    session['numrequests']=1
    #if session['numrequests']==10:
    #    return ""

    #load config
    conf=json.load(open(os.path.expanduser("~/.u-air.json")))
    session["conf"]=conf
    #set session variables
    session["theme"]=request.cookies.get("theme", 0)
    session["hidden"]=request.cookies.get("hidden", 0)
    session["lang"]=request.cookies.get("lang", "en")
    #is shared view
    if "shared" not in session:
        session["shared"]=False

#add global functions to jinja2 templates
app.jinja_env.globals["lt"]=lt

if __name__=="__main__":
    if "launch" in sys.argv:
        app.debug=False
        app.run(host="0.0.0.0", port=int(conf["port"]))
    elif "debug" in sys.argv:
        app.debug=True
        app.run(host="0.0.0.0", port=int(conf["port"]))
    else:
        print("Use launcher to run web server")

