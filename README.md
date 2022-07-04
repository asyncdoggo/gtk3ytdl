# GTK3YDL
A GTK3 frontend for yt-dlp to download Youtube Videos


## Requirements:
Step 1:
1. <a href="https://ffmpeg.org">ffmpeg</a><br>
2. To install Gtk3 follow this guide:<br>
https://pygobject.readthedocs.io/en/latest/getting_started.html
####
step 2:
install yt_dlp using pip:<br>
<code>pip install yt_dlp</code>
<br>
On windows, only mingw is supported, use a virtualenv inheriting global packages and then run
<br>
<code>.\venv\bin\pip.exe install pycryptodomex brotli yt_dlp --plat win32 --only-binary :all: -t .\venv\lib --upgrade</code>
<br>
and then:
<br>
<code>.\venv\bin\pip.exe install yt_dlp --no-deps</code>