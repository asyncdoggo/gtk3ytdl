import glob
import os
import pathlib
import shutil
import threading
import gi
import yt_dlp

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

title = None
video_id = None


# YDL
def getopts(url):
    global title, video_id
    opts_list = []
    formid = []
    if "watch" not in url:
        return "invalid", None
    with yt_dlp.YoutubeDL({"noplaylist": "true"}) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            video_id = info["id"]
        except yt_dlp.utils.DownloadError:
            return "invalid", None
        info = ydl.sanitize_info(info)
        title = info["title"]
        selectlabel.set_text(f"selected video:\n{title}")
        formats = info["formats"]

        i = 0
        for f in formats:
            try:
                a = f["fps"]
                b = f["filesize"]
                c = f["ext"]
                if b:
                    fsize = str(round(b / 1024 ** 2, 2))
                else:
                    b = 0
                opts_list.append([i, str(f["format"]), str(a), str(f["ext"]), fsize])
                formid.append(f["format_id"])
                i += 1
            except KeyError:
                pass
    return opts_list, formid


class MyLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'downloading':
        x = d['_percent_str'].replace("%", "")
        GLib.idle_add(lambda: prog.set_fraction(float(x) / 100))
        try:
            speed = round(d["speed"] / 1048576, 2)
            eta = d["eta"]
            down = round(d['downloaded_bytes'] / 1048576, 2)
        except TypeError:
            speed = ''
            eta = ''
            down = ''
        GLib.idle_add(lambda: speedeta.set_text(f"speed:{speed} MB/s \neta: {eta} sec \ndownloaded: {down} MB"))

    if d['status'] == 'finished':
        GLib.idle_add(lambda: errorlabel.set_text("Download complete, Downloading audio\n and Processing"))


def download(url, formid, audio):
    global title, video_id

    ydl_opts = {
        "noplaylist": "true",
        'format': f"{formid}+bestaudio/best",
        'logger': MyLogger(),
        'progress_hooks': [my_hook]
    }

    if audio:
        ydl_opts['format'] = str(formid)
        ydl_opts['postprocessors'] = [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav', 'preferredquality': 'best'}]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        folder = browsetext.get_text()
        if pathlib.Path(folder).exists():
            errorlabel.set_text("Downloading")
            try:
                ydl.download(url)
                tempfile = glob.glob(f"*{video_id}*")[0]
                pat = os.path.join(folder, tempfile)
                shutil.move(tempfile, pat)
                errorlabel.set_text("Completed")
                downbutton.set_sensitive(True)

            except yt_dlp.utils.DownloadError as e:
                downbutton.set_sensitive(True)
                if "ffmpeg" in repr(e):
                    errorlabel.set_text("Error:ffmpeg not installed")
                else:
                    errorlabel.set_text(e.msg)
        else:
            errorlabel.set_text("Incorrect Path")
            downbutton.set_sensitive(True)


#######################################


build = Gtk.Builder()
build.add_from_file("window.glade")


def browsefile(widget):
    dialog = Gtk.FileChooserDialog(
        title="Please choose a file", parent=window, action=Gtk.FileChooserAction.SELECT_FOLDER
    )
    dialog.add_buttons(
        Gtk.STOCK_CANCEL,
        Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OPEN,
        Gtk.ResponseType.OK,
    )

    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        x = dialog.get_filename()
        browsetext.set_text(x)
    elif response == Gtk.ResponseType.CANCEL:
        pass
    dialog.destroy()


def fillopts(widget):
    s1.clear()
    threading.Thread(target=updatestuff).start()
    optslist.set_model(s1)


def updatestuff():
    global formatids
    prog.set_fraction(0)
    errorlabel.set_text("")
    selectlabel.set_text("")

    url = urltext.get_text()
    speen.start()
    opts, formatids = getopts(url)
    if opts == "invalid":
        errorlabel.set_text("Invalid url")
    else:
        for k in opts:
            s1.append(k)
    speen.stop()


def downloadstart(widget):
    global formatids
    downbutton.set_sensitive(False)
    select = optslist.get_selection()
    listore, iterer = select.get_selected()
    try:
        index = int(listore.get_value(iterer, 0))
        aud = audonly.get_active()
        url = urltext.get_text()
        formid = formatids[index]
        errorlabel.set_text("")
        threading.Thread(target=download, args=(url, formid, aud)).start()
    except TypeError:
        downbutton.set_sensitive(True)
        errorlabel.set_text("Select a value from the list first")


# setup
formatids = []

prog: Gtk.ProgressBar = build.get_object("prog")
window: Gtk.Window = build.get_object("window1")
urltext: Gtk.Entry = build.get_object("urltext")
browsebutton: Gtk.Button = build.get_object("browsebutton")
browsetext: Gtk.Entry = build.get_object("browsetext")
showopts: Gtk.Button = build.get_object("showopts")
downbutton: Gtk.Button = build.get_object("download")
audonly: Gtk.ToggleButton = build.get_object("audonly")
optslist: Gtk.TreeView = build.get_object("optslist")
speen: Gtk.Spinner = build.get_object("speen")
errorlabel: Gtk.Label = build.get_object("errorlabel")
selectlabel: Gtk.Label = build.get_object("selectlabel")
speedeta: Gtk.Label = build.get_object("speedeta")
selectlabel.set_line_wrap(True)
errorlabel.set_line_wrap(True)
speedeta.set_line_wrap(True)

# define optslist
s1: Gtk.ListStore = Gtk.ListStore(int, str, str, str, str)
optslist.set_model(s1)
for i, column_title in enumerate(["Index", "Format", "FPS", "Codec", "Filesize(MB)"]):
    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn(column_title, renderer, text=i)
    optslist.append_column(column)
#

window.set_default_size(600, 700)
browsebutton.connect("clicked", browsefile)
downbutton.connect("clicked", downloadstart)
showopts.connect("clicked", fillopts)

window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
