import subprocess

from flask import Blueprint
from flask import request
from flask import render_template
from flask import session
from flask import abort

bp = Blueprint("terminalviews", __name__)


@bp.route("/terminal", methods = ["get"])
def terminalview():
    if "online" not in session:
        return redirect("/")
    if session["shared"]:
        return redirect("/")
    return render_template("terminal.html")


@bp.route("/execute", methods = ["post"])
def executecommand():
    if "online" not in session:
        return redirect("/")
    if session["shared"]:
        return redirect("/")

    #Bash process for terminal
    proc=proc=subprocess.Popen(
        ["export TERM='';/bin/bash"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True)

    #Get command
    cmd=request.form['command']
    #Send command to shell
    result, err=proc.communicate(cmd)
    return result
