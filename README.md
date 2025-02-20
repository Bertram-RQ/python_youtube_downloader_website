
# YouTube Downloader Website

This YouTube Downloader is built with python, html, css, and javascript

**this program is intended for personal use**

it allows you to download youtube and tiktok videos (may not work with age restricted videos) and download them directly from the main page


## Installation

Step 1: install [Python](https://www.python.org/downloads/)

> [!NOTE]
> Remember to add it to [PATH](https://phoenixnap.com/kb/add-python-to-path)

Step 2: install [FFmpeg](https://phoenixnap.com/kb/ffmpeg-windows)

> [!NOTE]
> Remember to add it to [PATH](https://phoenixnap.com/kb/ffmpeg-windows#Step_3_Add_FFmpeg_to_PATH)

Step 3: install packages

```bash
pip install -r requirements.txt
```

or 

```bash
pip install yt_dlp
pip install flask
pip install requests
pip install emoji
pip install sqlalchemy
```

Step 4: setup IP and Port to use (you usually won't need to change this if you're running it on your own machine)

```python
ip_address = "127.0.0.1"
port = 5500
use_user_address = False  # whether or not to use the "ip_address" variable this will just get the ip that the user connected to aka the website then uses that instead of "ip_address"

use_user_ids = False  # recommended for multiple users, this will create an id for each person and then save it with each download so only downloads from said person can be used, these ids will be saved locally to each user, this will prevent people from getting previously downloaded videos that other users downloaded and stopping them from removing files they did not download (this is NOT secure)

use_automatic_removal_system = True  # will remove any files that exceeds the "removal_time_seconds" variable
removal_time_seconds = 1 * 60 * 60  # (1 * 60 * 60 = 1 hour) amount of time in seconds that the file should remain when it exceeds this time it will be deleted aslong as "use_automatic_removal_system" is used
checking_time_seconds = 30 * 60  # (30 * 60 = 30 minutes) amount of time in seconds between checks for file removal

max_video_length_seconds = 10 * 60 * 60  # (10 * 60 * 60 = 10 hours) video length in seconds that the downloader can handle

allow_sync_button = True  # only if "use_automatic_removal_system" is in use
enable_remove_files_button = True  # recommended for local use
enable_debug_button = False  # don't use only for developer testing new features

enable_automatic_browser_opening = True  # recommended for ease of use
```


### Docker

[instructions here](https://hub.docker.com/r/bertramrq/python-yt-downloader-website)


## Running

To run the program just go into the website folder and double click the `python_website.py` file or 

run `py python_website.py` in cmd in the website folder (or any other terminal) 

(**`python_website.py`** is the **filename** i set so if you changed it then the same applies with whatever you put as the **filename**)
## Authors

- [BertramRQ](https://github.com/Bertram-RQ)


## Features


- Supports Youtube and Tiktok (tiktok is possibly buggy)
- Opens In Browser Automatically When Run
- Supports Video Download (MP4)
- Up To 1080p Downloads
- Supports Audio Only Download (MP3, M4A, WEBM, AAC, FLAC, OPUS, OGG, WAV)
- Shows video name, channel name, (both with link) and thumbnail when finished Downloading
- Automatic Removal system Configurable via Config variables
- ability to get previously downloaded video back
- simple user system (NOT secure)
- Quite Configurable


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

