#! /usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import sys
import random
import socket
import subprocess
import signal
import hashlib
import subprocess


from functions import lt
from langs import langs
from loaders import load_config, save_config


ROOT_PATH=os.path.dirname(__file__)
ICON_PATH=os.path.join(ROOT_PATH, "static/launcher.png")
PIDFILE_PATH=os.path.expanduser("~/.uair.pid")
DEFAULT_IMAGES_PATH=os.path.expanduser("~/Pictures")

try:
    import gtk
    CLIMODE=False
    if len(sys.argv)>1 and sys.argv[1]=="cli":
        CLIMODE=True
        sys.argv=sys.argv[1:]
except:
    CLIMODE=True

CLIMODE = False



def check_pidfile():
    if os.path.exists(PIDFILE_PATH):
        return int(open(PIDFILE_PATH).read())
    else:
        return False


def create_pidfile(pid):
    ff=open(PIDFILE_PATH, "w")
    ff.write(str(pid))
    ff.close()


def delete_pidfile():
    if check_pidfile():
        os.remove(PIDFILE_PATH)
        return True
    else:
        return False


def remove_orphaned_pidfile(pid):
    if not os.path.exists("/proc/%s" % str(pid)):

        result=delete_pidfile()
        if result:
            print("Removed orphaned pid file")


def generate_password(length=5):
    alphabet = "abcdefghijkmnoprstuwxyz1234567890"
    pwd = ''
    for count in range(length):
        for x in random.choice(alphabet):
            pwd+=x
    return pwd

def hash_password(password):
    from main import SECRET_KEY
    #hash password
    hashed=hashlib.md5()
    hashed.update(SECRET_KEY+password)
    return hashed.hexdigest()

def get_local_ip_address():
    import socket
    try:
        s = socket.socket()
        s.connect(('google.com', 80))
        ip=s.getsockname()[0]
    except:
        ip=""
    if ip:
        return ip
    else:
        return "127.0.0.1"

def get_global_ip_address():
    import urllib2
    try:
        ip=urllib2.urlopen('http://icanhazip.com').read()
        ip=ip.strip()
    except:
        ip=""
    if ip:
        return ip
    else:
        return "127.0.0.1"

def start_server(config):
    #Dont start server when is running
    if check_pidfile():
        print("Server already started.")
        return

    #create server path
    path=os.path.join(ROOT_PATH, "main.pyc")

    #Start server
    cmd=["nohup", "python", path,"launch"]
    server=subprocess.Popen(cmd)

    #create pid file diable start button
    create_pidfile(server.pid)
    return server

def stop_server(config):
    #stop www server by sending SIGINT signal
    pid=check_pidfile()
    if pid:
        #remove pid file
        delete_pidfile()
        #Kill process
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:pass

        print("Web server stopped")
        ddd = subprocess.Popen("/usr/bin/notify-send Server Stopped", shell=True)
        ddd.poll()
        return True
    else:
        print("Server not started.")
    return False


######################
# CLI Launcher
######################
if CLIMODE:
    #ignore not run as script
    if not __name__=="__main__":
        exit(0)
    #ignore arguments
    if len(sys.argv)<2:
        print("Usage: sudo python launcher.pyc start/stop")
        print("launcher.pyc password <newpassword>")
        print("launcher.pyc port <new port>")
        exit(0)
    #ignore others commands
    if sys.argv[1] not in ["start", "stop", "password", "port"]:
        print("Invalid command")
        exit(0)
    #remove pid
    remove_orphaned_pidfile(check_pidfile())
    #load config
    try:
        config=load_config()
    except: pass
    if sys.argv[1]=="start":
        if check_pidfile():
            print("Server already started.")
            exit(0)
        gip=get_global_ip_address()
        lip=get_local_ip_address()
        #print addresses
        print("Local IP: %s" % lip)
        print("Public IP: %s" % gip)
        #gen passwords
        pass1=generate_password()
        pass2=generate_password()
        config["gen_password"]=hash_password(pass1)
        config["gen_password_shared"]=hash_password(pass2)
        print("Login password:%s" % pass1)
        print("Shared password:%s" % pass2)
        config["local_ip"]=lip
        config["global_ip"]=gip
        save_config(config)
        start_server(config)
        config["status"]=1
        save_config(config)



    if sys.argv[1]=="stop":
        done=stop_server(config)
        if done:
            config["status"]=0
            save_config(config)

    if sys.argv[1]=="password" and len(sys.argv)>2:
        config["password"]=hash_password(sys.argv[2].strip())
        save_config(config)
        print("New password set")

    if sys.argv[1]=="port":
        if len(sys.argv)>2:
            try:
                config["port"]=int(sys.argv[2].strip())
                save_config(config)
                print("Port set to %s "% int(sys.argv[2].strip()))
            except:pass
        else:
            print("Current port: %s "% config["port"])

    #exit
    exit(0)


class MainWindow(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("U-Air Launcher")
        self.set_icon_from_file(ICON_PATH)
        self.set_resizable(False)
        self.set_size_request(440, 320)
        self.set_border_width(20)
        self.set_position(gtk.WIN_POS_CENTER)

        #load config
        self.config=load_config()
        save_config(self.config)

        #www server process
        self.server=None

        #get lang from config
        self.lang=self.config.get("lang", "en")

        #connect close event
        self.connect("destroy", self.close_app)

        self.fixed = gtk.Fixed()

        self.label_status = gtk.Label("Status:")
        self.label_status.set_text(lt("Status", self.lang)+":")

        #local IP label
        self.label_local_ip = gtk.Label("Local IP:")
        label=lt("Local IP", self.lang)+": "+self.config["local_ip"]
        label+=":"+str(self.config["port"])
        self.label_local_ip.set_text(label)

        self.label_public_ip = gtk.Label("Public IP:")
        label=lt("Public IP", self.lang)+": "+self.config["global_ip"]+":"+str(self.config["port"])
        self.label_public_ip.set_text(label)
        self.label_gen_password = gtk.Label("Login password:")
        self.label_gen_password.set_text(lt("Login password", self.lang)+":")
        self.label_gen_password_shared = gtk.Label("Shared password:")
        self.label_gen_password_shared.set_text(lt("Shared password", self.lang)+":")
        self.label_set_gen_password = gtk.Label("...")
        self.label_set_gen_password_shared = gtk.Label("...")
        self.button_regenerate = gtk.Button("Regenerate password")
        self.button_regenerate.set_label(lt("Regenerate password", self.lang))
        self.button_regenerate.connect("clicked", self.regenerate)

        self.button_start = gtk.Button("Start")
        self.button_start.set_label(lt("Start", self.lang))
        self.button_start.connect("clicked", self.start)
        self.button_start.set_size_request(110, 50)
        self.button_stop = gtk.Button("Stop")
        self.button_stop.set_label(lt("Stop", self.lang))
        self.button_stop.connect("clicked", self.stop)
        self.button_stop.set_size_request(110, 50)

        self.button_options = gtk.Button("Options")
        self.button_options.set_label(lt("Options", self.lang))
        self.button_options.set_size_request(130, 30)
        self.button_options.connect("clicked", self.show_option_window)
        self.button_about = gtk.Button("About")
        self.button_about.set_label(lt("About", self.lang))
        self.button_about.set_size_request(130, 30)
        self.button_about.connect("clicked", self.show_about_window)
        self.button_quit = gtk.Button("Quit")
        self.button_quit.set_label(lt("Quit", self.lang))
        self.button_quit.set_size_request(130, 30)
        self.button_quit.connect("clicked", self.close_app)

        self.img_banner = gtk.Image()
        self.img_banner.set_from_file(os.path.join(ROOT_PATH,
            "static/banner1.png"))

        self.fixed.put(self.img_banner, 0, 0)
        self.fixed.put(self.label_status, 5, 5)
        #self.fixed.put(self.label_local_ip, 3, 130)
        #self.fixed.put(self.label_public_ip, 200 ,130)
        self.fixed.put(self.label_local_ip, 5, 110)
        self.fixed.put(self.label_public_ip, 5 ,130)
        self.fixed.put(self.button_regenerate, 70, 200)

        self.fixed.put(self.button_start, 0, 230)
        self.fixed.put(self.button_stop, 120, 230)

        self.fixed.put(self.label_gen_password, 0, 160)
        self.fixed.put(self.label_set_gen_password, 150, 160)
        self.fixed.put(self.label_gen_password_shared, 0, 180)
        self.fixed.put(self.label_set_gen_password_shared, 150, 180)

        self.fixed.put(self.button_options, 250, 170)
        self.fixed.put(self.button_about, 250, 210)
        self.fixed.put(self.button_quit, 250, 250)
        self.add(self.fixed)
        #show all
        self.show_all()
        #create pictures folder if not exist
        if not os.path.exists(DEFAULT_IMAGES_PATH):
            os.mkdir(DEFAULT_IMAGES_PATH)
        #remove pid file when process not exist
        remove_orphaned_pidfile(check_pidfile())
        #set status
        self.setstatus()
        #update start stop buttons
        self.toggle_start_stop_buttons()
        #generate new login password
        self.gen_login_password()
        self.gen_shared_password()

    def regenerate(self, widgget, data=None):
        self.gen_login_password()
        self.gen_shared_password()

    def setstatus(self):
        self.config["status"]=bool(check_pidfile())

        #get and save global ip
        gip=get_global_ip_address()
        self.config["global_ip"]=gip
        self.label_public_ip.set_text(lt("Public IP", self.lang)+": "+\
            self.config["global_ip"]+":"+str(self.config["port"]))

        # get and save local IP
        lip=get_local_ip_address()
        self.config["local_ip"]=lip
        self.label_local_ip.set_text(lt("Local IP", self.lang)+": "+\
            self.config["local_ip"]+":"+str(self.config["port"]))

        if self.config["status"]:
            self.label_status.set_text("Status: "+lt("Online", self.lang))
        else:
            self.label_status.set_text("Status: "+lt("Offline", self.lang))

    def toggle_start_stop_buttons(self):
        serverpid=check_pidfile()
        if serverpid:
            self.button_start.set_sensitive(False)
            self.button_stop.set_sensitive(True)
        else:
            self.button_start.set_sensitive(True)
            self.button_stop.set_sensitive(False)

    def start(self, widget, data=None):
        """Start web server"""
        if self.server:return

        serv=start_server(self.config)
        if serv:
            self.server=serv

        self.toggle_start_stop_buttons()

        #set status
        self.setstatus()
        save_config(self.config)

        print("Web server started")
        ddd = subprocess.Popen("/usr/bin/notify-send Server Started", shell=True)
        ddd.poll()

    def stop(self, widget, data=None):
        """Stop web server"""
        if stop_server(self.config):
            self.server=None
        self.setstatus()
        self.toggle_start_stop_buttons()
        #save config
        save_config(self.config)

    def close_app(self, widget, data=None):
        exit(0)

    def show_option_window(self, widget, data=None):
        OptionWindow(self.config)

    def show_about_window(self, widget, data=None):
        AboutWindow(self.config)

    def gen_login_password(self):
        pwd=generate_password()
        hpwd=hash_password(pwd)
        self.config["gen_password"] = hpwd
        save_config(self.config)
        #set text for widget with password
        self.label_set_gen_password.set_text(pwd)

    def gen_shared_password(self):
        pwd=generate_password()
        hpwd=hash_password(pwd)
        self.config["gen_password_shared"] = hpwd
        save_config(self.config)
        #set text for widget with password
        self.label_set_gen_password_shared.set_text(pwd)


class OptionWindow(gtk.Window):

    def __init__(self, config):

        self.config=config
        self.lang=self.config.get("lang", "en")
        gtk.Window.__init__(self)
        self.set_title(lt("Options", self.lang))
        self.set_resizable(False)
        self.set_size_request(300, 250)
        self.set_border_width(20)
        self.set_position(gtk.WIN_POS_CENTER)

        self.connect("destroy", self.close_window)
        self.fixed = gtk.Fixed()
        self.label_set_pass = gtk.Label("Password:")
        self.label_set_pass.set_text(lt("Password", self.lang)+":")
        self.entry_set_pass = gtk.Entry()
        self.label_startup = gtk.Label("Load in startup Ubuntu")
        self.label_startup.set_text(lt("Load in startup Ubuntu", self.lang))
        self.check_startup = gtk.CheckButton()
        self.check_startup.set_active(self.config["startup"])
        self.check_startup.connect("toggled", self.entry_checkbox)
        self.label_set_port = gtk.Label("Port:")
        self.label_set_port.set_text(lt("Port", self.lang)+":")
        self.entry_set_port = gtk.Entry()
        self.entry_set_port.set_text(str(self.config["port"]))
        self.label_choose_image = gtk.Label("Choose images folder")
        self.label_choose_image.set_text(lt("Choose images folder", self.lang)+":")
        self.chooser_image_folder = \
            gtk.FileChooserButton(lt("Choose images folder", self.lang))
        self.chooser_image_folder.set_action(
            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER
            )
        self.chooser_image_folder.set_size_request(150,35)
        self.label_set_language = gtk.Label("Set language:")
        self.label_set_language.set_text(lt("Set language", self.lang)+":")
        self.combo_language = gtk.combo_box_new_text()

        #add languages
        for lang in langs:
            self.combo_language.append_text(lang)
        self.combo_language.set_active(langs.keys().index(\
            self.config["lang"]))

        self.combo_language.connect("changed", self.select_language)
        #get images path
        imgpath=self.config.get("images_path", \
            os.path.expanduser("~/Pictures"))
        self.chooser_image_folder.set_filename(imgpath)
        self.button_save = gtk.Button("Save")
        self.button_save.set_size_request(130, 30)
        self.button_save.connect("clicked", self.onsave)

        self.fixed.put(self.label_set_pass, 10, 5)
        self.fixed.put(self.entry_set_pass, 90, 0)
        #self.fixed.put(self.check_startup, 5, 42)
        #self.fixed.put(self.label_startup, 40, 44)
        self.fixed.put(self.label_set_port, 10, 44)
        self.fixed.put(self.entry_set_port, 90 ,42)
        self.fixed.put(self.label_choose_image, 10, 90)
        self.fixed.put(self.chooser_image_folder, 10, 110)
        self.fixed.put(self.label_set_language, 10, 150)
        self.fixed.put(self.combo_language, 10, 170)
        self.fixed.put(self.button_save, 120, 170)
        self.add(self.fixed)

        self.show_all()

    def select_language(self, combo_language, data=None):
        model = self.combo_language.get_model()
        index = self.combo_language.get_active()
        self.config["lang"]=langs.keys()[index]
        dlg=gtk.MessageDialog(self, gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE,
            "Launcher restart required.")
        dlg.run()
        dlg.destroy()

    def onsave(self, widget, data=None):
        """Save options configuration"""
        from main import SECRET_KEY

        passwd = self.entry_set_pass.get_text()
        check = self.check_startup.get_active()
        port = self.entry_set_port.get_text()
        hashed=hashlib.md5()
        hashed.update(SECRET_KEY+passwd)
        if passwd:
            self.config["password"] = hashed.hexdigest()
        self.config["startup"] = check
        self.config["port"] = int(port)
        self.config["images_path"] = self.chooser_image_folder.get_filename()
        save_config(self.config)
        self.destroy()

    def add_startup(self, data=None):
        a = os.path.expanduser("~")
        b = ".xinitrc"
        c = os.path.join(a,b)
        if not os.path.isfile(c):
            os.system("cd ~ && touch .xinitrc")
            open(c, 'w').write("/opt/uair/bin/uairlauncher start")
        elif os.path.isfile(c):
            open(c, 'a').write("/opt/uair/bin/uairlauncher start")

    def del_startup(self, data=None):
        try:
            zrodlo = open('~/.xinitrc').readlines()
            cel = open('~/.xinitrc', 'a')
            for s in zrodlo:
                cel.write(s.replace("/opt/uair/bin/uairlauncher start", ""))
            cel.close()
        except:
            pass

    def entry_checkbox(self, widget):
        global b_entry_checkbox
        b_entry_checkbox = self.check_startup.get_active()
        if b_entry_checkbox:
            self.add_startup()
        else:
            self.del_startup()
        return


    def close_window(self, widget, data=None):
        self.destroy()


class AboutWindow(gtk.Window):

    def __init__(self, config):
        self.config=config
        self.lang=self.config.get("lang", "en")
        gtk.Window.__init__(self)
        self.set_resizable(False)
        self.set_title(lt("About", self.lang))
        self.set_size_request(540, 250)
        self.set_border_width(20)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", self.close_window)
        self.fixed = gtk.Fixed()
        self.label_about = gtk.Label(lt("U-Air\n\
---------------------\n\
U-Air allow you to browse upload and download your files, wherever you are.\n\
You forget take any file from home to your friend ? Now its not problem.\n\
You can easly browse your files, upload new and listen MP3 songs.", self.lang))
        self.label_authors=gtk.Label("Authors:")
        self.label_authors.set_text(lt("Authors", self.lang)+":")
        author1="Michal Rosiak <michal0468@gmail.com>"
        author2="Marcin Swierczynski <orneo1212@gmail.com>"
        self.label_autor1 = gtk.Label(author1)
        self.label_autor2 = gtk.Label(author2)
        self.fixed.put(self.label_about, 5, 10)
        self.fixed.put(self.label_authors, 5, 120)
        self.fixed.put(self.label_autor1, 10, 150)
        self.fixed.put(self.label_autor2, 10, 180)
        self.add(self.fixed)
        self.show_all()

    def close_window(self, widget, data=None):
        self.destroy()

#class HelpConsole():
#    def __init__(self):
#        print "Help Console:\n"
#        print "start_console - Start web server in console"

if __name__ == "__main__":
    main=MainWindow()

    #get arguments
    if "start" in sys.argv:
        main.hide()
        main.start(None)
        main.close_app(None)
    elif "stop" in sys.argv:
        main.hide()
        main.stop(None)
        main.close_app(None)
    try:
        gtk.main()
    except:
        import traceback
        traceback.print_exc()
        main.stop(None)
