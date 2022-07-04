import threading
import time
import gi
import ydlp

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

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
    global formatids
    prog.set_fraction(0)
    errorlabel.set_text("")
    selectlabel.set_text("")

    url = urltext.get_text()
    speen.start()
    opts, formatids, title = ydlp.getopts(url)
    selectlabel.set_text(f"selected video:\n{title}")
    if opts == "invalid":
        errorlabel.set_text("Invalid url")
    else:
        for k in opts:
            s1.append(k)
    speen.stop()
    optslist.set_model(s1)


def initdownload(widget):
    global formatids
    downbutton.set_sensitive(False)
    showopts.set_sensitive(False)
    select = optslist.get_selection()
    listore, iterer = select.get_selected()
    try:
        index = int(listore.get_value(iterer, 0))
        errorlabel.set_text("")
        threading.Thread(target=downloadstart, args=[index], daemon=True).start()
    except TypeError:
        downbutton.set_sensitive(True)
        showopts.set_sensitive(True)
        errorlabel.set_text("Select a value from the list first")


def downloadstart(index):
    aud = audonly.get_active()
    url = urltext.get_text()
    formid = formatids[index]
    folder = browsetext.get_text()
    t1 = threading.Thread(target=ydlp.download, args=(url, formid, aud, folder), daemon=True)
    t1.start()
    while t1.is_alive():
        time.sleep(0.2)
        GLib.idle_add(lambda: prog.set_fraction(ydlp.pmsg))
        GLib.idle_add(lambda: speedeta.set_text(ydlp.smsg))
        GLib.idle_add(lambda: errorlabel.set_text(ydlp.gmsg))

    downbutton.set_sensitive(True)
    showopts.set_sensitive(True)


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
downbutton.connect("clicked", initdownload)
showopts.connect("clicked", lambda x: threading.Thread(target=fillopts, args=x, daemon=True).start())

window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
