import glob
import os
import pathlib
import shutil
import yt_dlp
import re

pmsg = 0
smsg = ""
gmsg = ""

title = None
video_id = None
reg = "^(https?\:\/\/)?((www\.)?youtube\.com|youtu\.be)\/.+$"


def getopts(url):
    global title, video_id
    opts_list = []
    formid = []
    if not re.match(reg, url):
        return "invalid", None, None
    with yt_dlp.YoutubeDL({"noplaylist": "true"}) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            video_id = info["id"]
        except yt_dlp.utils.DownloadError:
            return "invalid", None, None
        info = ydl.sanitize_info(info)
        title = info["title"]
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
    return opts_list, formid, title


class MyLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    global pmsg, smsg, gmsg
    if d['status'] == 'downloading':
        x = d['_percent_str'].replace("%", "")
        pmsg = float(x) / 100
        try:
            speed = round(d["speed"] / 1048576, 2)
            eta = d["eta"]
            down = round(d['downloaded_bytes'] / 1048576, 2)
        except TypeError:
            speed = ''
            eta = ''
            down = ''
        smsg = f"speed:{speed} MB/s \neta: {eta} sec \ndownloaded: {down} MB"

    if d['status'] == 'finished':
        gmsg = "Download complete, Downloading audio\n and Processing"


def download(url, formid, audio, folder):
    global title, video_id, gmsg
    gmsg = "downloading"
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
        if pathlib.Path(folder).exists():
            gmsg = "Downloading"
            while True:
                try:
                    ydl.download(url)
                    tempfile = glob.glob(f"*{video_id}*")[0]
                    pat = os.path.join(folder, tempfile)
                    shutil.move(tempfile, pat)
                    gmsg = "Completed"
                    break
                except yt_dlp.utils.DownloadError as e:
                    if "ffmpeg" in repr(e):
                        gmsg = "Error:ffmpeg not installed"
                        break
                    elif "giving up" in e.msg:
                        continue
                    else:
                        gmsg = e.msg
                        break
        else:
            gmsg = "folder does not exist"
