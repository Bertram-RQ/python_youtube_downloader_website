
# YouTube Downloader Website

This YouTube Downloader is built with python, html, css, and javascript

**this program is intended for personal use**

it allows you to download youtube videos (may not work with age restricted videos) and download them directly from the main page


## Installation

Step 1: install [Python](https://www.python.org/downloads/)

Step 2: install [FFmpeg](https://phoenixnap.com/kb/ffmpeg-windows)

Step 3: install packages

```bash
pip install -r requirements.txt
```

or 

```bash
pip install yt_dlp
pip install flask
pip install requests
```

Step 4: setup IP and Port to use (you usually won't need to change this if you're running it on your own machine)

```python
ip_address = "127.0.0.1"
port = 5500
```

## Running

To run the program just go into the website and double click the `python_website.py` file or 

run `py python_website.py` in cmd in the website folder (or any other terminal) 

(**`python_website.py`** is the **filename** i set so if you changed it then the same applies with whatever you put at the **filename**)
## Authors

- [BertramRQ](https://github.com/Bertram-RQ)


## Features


- Supports Youtube and Tiktok (tiktok is possibly buggy)
- Opens In Browser Automatically When Run
- Supports Video Download (MP4)
- Up To 1080p Downloads
- Supports Audio Only Download (MP3, M4A, WEBM, AAC, FLAC, OPUS, OGG, WAV)
- Shows video name, channel name, (both with link) and thumbnail when finished Downloading
- one Downside It does not have an automatic removal system (i might make it) so there's a button that'll delete all the files


## FAQ

#### Is the code well optimized?

no


#### Does it Download videos fast?

depends on your internet connection but it does download quite fast for me


#### Was chatgpt used to make this program?

Yes

#### Do i actually know what the code does?

Yes

#### Am i very Smart?

No


## License

[MIT](https://github.com/Bertram-RQ/python_youtube_downloader_website/blob/main/LICENSE)

