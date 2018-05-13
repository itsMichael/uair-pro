import subprocess
import os
import base64

from flask import Blueprint
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import abort
from flask import make_response

from werkzeug import secure_filename
import flask

from loaders import load_playlist, save_playlist
from loaders import IMAGES_EXTENSIONS, MUSIC_EXTENSIONS


bp = Blueprint("filemanagerviews", __name__)

SHARED_PATH=os.path.expanduser("~/UAir Shared")


def decodeutf8(text):
    try:
        text=text.decode("utf-8")
    except:pass
    return text


def encodeutf8(text):
    try:
        text=text.encode("utf-8")
    except:pass
    return text


@bp.route("/files", methods=["GET", "POST"])
def filemanager():
    if "online" not in session:
        return redirect("/")

    if request.method=="GET":
        #vars
        default_path=os.path.expanduser("~/")
        oldpath=session["sciezka"]
        parent=request.args.get('parent', None)
        home=request.args.get('home', None)
        subfolder=request.args.get('folder', "")
        subfolder=subfolder.replace("../", "")
        subfolder=decodeutf8(subfolder)

        #CHANGE DEFAULT FOLDER WHEN SHARED VIEW
        if session["shared"]:
            default_path=SHARED_PATH
            if not os.path.exists(default_path):
                os.mkdir(default_path)

        #poprzedni folder
        if parent:
            session["sciezka"]=os.path.dirname(session["sciezka"])
        #zmiana podfolderu
        if subfolder and not parent:
            nowyfolder=os.path.join(session["sciezka"], subfolder)
            #go to subfolder
            if os.path.isdir(nowyfolder):
                session['sciezka']=nowyfolder
            else:
                session['sciezka']=oldpath
        #home if path invalid in shared view
        if session["shared"]:
            if not session['sciezka'].startswith(default_path):
                session['sciezka']=default_path
        #home if not action
        if home:
            session['sciezka']=default_path

        #czy wyswietlac ukryte pliki
        ukryte=session.get("hidden", 0)

        #folder
        folder=session['sciezka']
        folder=decodeutf8(folder)

        #pobieramy pliki
        try:
            lista=os.listdir(folder)
        except OSError:
            #Restore path when permission denied
            lista=os.listdir(oldpath)
            folder=oldpath
            session['sciezka']=oldpath

        lista_plikow=[]
        lista_folderow=[]

        #Rozdzielamy listowanie na pliki i foldery
        for plik in lista:
            plik=decodeutf8(plik)
            #create path
            sciezka=os.path.join(folder, plik)
            sciezka=decodeutf8(sciezka)
            #Is file
            if os.path.isfile(sciezka):
                if plik.startswith(".") and not ukryte:
                    continue
                lista_plikow.append(plik)
            #Is folder
            elif os.path.isdir(sciezka):
                if plik.startswith(".") and not ukryte:
                    continue
                lista_folderow.append(plik)

        #sortowanie plikow i folderow

        lista_plikow=sorted(lista_plikow, key=unicode.lower)
        lista_folderow=sorted(lista_folderow, key=unicode.lower)

        return render_template('filemanager.html',
            pliki=lista_plikow,
            foldery=lista_folderow
            )


@bp.route("/download", methods=["GET", "POST"])
def downlaodfile():
    if "online" not in session:
        return redirect("/")

    sciezka=session['sciezka']

    path=request.args.get("path", "")
    path=base64.b64decode(path)

    if not path:
        #pobieramy nazwe pliku wyslana przez get
        nazwa=request.args["plik"]
        nazwa=base64.b64decode(nazwa)
        nazwa=decodeutf8(nazwa)
        #sciezka pliku
        sciezka=os.path.join(sciezka, nazwa)
    else:
        sciezka=path
        nazwa=os.path.basename(sciezka)
        nazwa=decodeutf8(nazwa)

    #avoid get file outside shared folder
    sciezka=sciezka.replace("../", "")

    #avoid download outside shared folder
    if session["shared"]:
        shared_path=SHARED_PATH
        if not sciezka.startswith(SHARED_PATH):
            sciezka=SHARED_PATH

    #sprawdzamy czy plik istnieje
    if not os.path.exists(sciezka):
        return "File not found %s" % sciezka
    nn=nazwa.lower()

    try:
        nazwa=nazwa.encode('utf-8')
    except:pass
    #get extension
    ext=os.path.splitext(nn)[1].lower()
    #Wysylamy plik (tworzymy obiekt response odpowiedz serwera)
    if ext in IMAGES_EXTENSIONS:
        a=flask.send_file(sciezka,attachment_filename=nazwa)
    else:
        a=flask.send_file(sciezka, as_attachment=True,\
            attachment_filename=nazwa)
    #zwaracy widok
    return a


@bp.route("/upload", methods = ["post"])
def uploadfile():
    #Check login state
    if "online" not in session:
        return redirect("/")

    fp=request.files['uploadfile']
    if not fp:
        return redirect("/files?keep=1")
    filename=secure_filename(fp.filename)
    try:
        fp.save(os.path.join(session['sciezka'], filename))
    except:pass
    return redirect("/files?keep=1")


@bp.route("/audio", methods = ["get"])
def serveaudio():
    #Check login state
    if "online" not in session:
        return redirect("/")

    filename=request.args.get("filename", "")
    filename=encodeutf8(filename)
    filename=base64.b64decode(filename)

    fpath=request.args.get("path", "")
    fpath=encodeutf8(fpath)
    fpath=base64.b64decode(fpath)

    if not filename and not fpath:return ""

    if filename:
        path=os.path.join(session['sciezka'], filename)
    else:
        path=fpath

    ext=os.path.splitext(path)[1]
    if ext not in MUSIC_EXTENSIONS:
        return ""

    if not os.path.isfile(path):
        return ""
    return flask.send_file(path)


@bp.route("/fileinfo", methods = ["get"])
def fileinfo():
    #Check login state
    if "online" not in session:
        return redirect("/")

    ff=request.args.get("file","")
    ff=base64.b64decode(ff)
    if not ff:
        return ""
    ff=decodeutf8(ff)
    fpath=os.path.join(session["sciezka"], ff)

    #check for file exist
    if not os.path.exists(fpath):
        return ""

    info=os.stat(fpath)
    fsize=info.st_size
    if fsize>=1073741824:
        fsize_r=str(round(info.st_size/1073741824.0, 2))+" GB"
    elif fsize>=1048576:
        fsize_r=str(round(info.st_size/1048576.0, 2))+" MB"
    elif fsize>=1024:
        fsize_r=str(round(info.st_size/1024.0, 2))+" KB"
    else:
        fsize_r=str(fsize)+" B"
    return "<p>Size: "+str(fsize_r)+"</p>"

@bp.route("/addsong", methods = ["get"])
def addsong():
    #Check login state
    if "online" not in session:
        return redirect("/")
    if session["shared"]:
        return redirect("/")

    fname=request.args.get("file","")
    fname=base64.b64decode(fname)
    if not fname:
        return ""
    #Load song
    songs=load_playlist("main")
    #Add song
    spath=os.path.join(session["sciezka"], fname)
    fname= os.path.splitext(fname)[0]
    songs.append([fname, spath])
    #save playlist
    save_playlist("main", songs)
    return ""

@bp.route("/sethiddenfiles", methods = ["get"])
def sethiddenfiles():
    #Check login state
    if "online" not in session:
        return redirect("/")

    checked=int(request.args.get("state", 0))

    resp=make_response(redirect("/settings"))
    if checked:
        resp.set_cookie("hidden", 1)
    else:
        resp.set_cookie("hidden", "")
    return resp
