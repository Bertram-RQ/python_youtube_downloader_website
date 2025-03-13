import threading
import time
import yt_dlp
import os
import re
import requests
import subprocess
#   from dotenv import load_dotenv # use if you want environmental variable ## use "pip install dotenv"
from emoji import demojize

import youtube_downloader_sql as ydsql
import youtube_downloader_data as ydd

import json

from flask import Flask, render_template, request, jsonify, send_file, Response
import webbrowser


# region CONFIG SECTION
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

use_fast_converting = False  # when enabled this will not try for accuracy but just speed, i the developer recommend having this set to False as something like .ogg files to be replaced in something like a minecraft resource pack would have to be converted from ogg to ogg for it to work, when this is disabled it will make it use more computational power and take longer but have better results

enable_automatic_browser_opening = True  # recommended for ease of use
# endregion CONFIG SECTION


#  below is if you wish to use a .env file to load variables
# region CONFIG SECTION WITH ENVIRONMENT VARIABLES
#       load_dotenv()
#
#       ip_address = os.getenv("IP_ADDRESS", "127.0.0.1")  # Default: 127.0.0.1
#       port = int(os.getenv("PORT", 5500))  # Convert to int
#
#       use_user_address = os.getenv("USE_USER_ADDRESS", "False").lower() == "true"
#       use_user_ids = os.getenv("USE_USER_IDS", "False").lower() == "true"
#
#       use_automatic_removal_system = os.getenv("USE_AUTOMATIC_REMOVAL_SYSTEM", "True").lower() == "true"
#       removal_time_seconds = int(os.getenv("REMOVAL_TIME_SECONDS", 1 * 60 * 60))  # Convert to int
#       checking_time_seconds = int(os.getenv("CHECKING_TIME_SECONDS", 30 * 60))  # Convert to int
#
#       max_video_length_seconds = int(os.getenv("MAX_VIDEO_LENGTH_SECONDS", 10 * 60 * 60))  # Convert to int
#
#       allow_sync_button = os.getenv("ALLOW_SYNC_BUTTON", "True").lower() == "true"
#       enable_remove_files_button = os.getenv("ENABLE_REMOVE_FILES_BUTTON", "True").lower() == "true"
#       enable_debug_button = os.getenv("ENABLE_DEBUG_BUTTON", "False").lower() == "true"
#
#       enable_automatic_browser_opening = os.getenv("ENABLE_AUTOMATIC_BROWSER_OPENING", "True").lower() == "true"
# endregion CONFIG SECTION WITH ENVIRONMENT VARIABLES


downloads = {}

app = Flask(__name__)


@app.route('/downloads/<unique_id>')
def download_file(unique_id):
    """Serve the file when user visits the unique link"""
    file_path = downloads.get(unique_id)
    # file_path = f"{file_path}.mp4"
    print(f"{file_path=}")
    print(f"{os.path.exists(file_path)=}")

    if not file_path or not os.path.exists(file_path):
        return "Invalid or expired link", 404

    return send_file(file_path, as_attachment=True)

@app.route('/server-ip')
def get_server_ip():
    if not use_user_address:
        server_ip = request.host  # This gets the domain or IP the user used to connect
    else:
        server_ip = ip_address, port
    return jsonify({"server_ip": server_ip, "use_user_address": use_user_address})

@app.route('/server-config')
def get_server_config():
    return jsonify({"allow_sync": allow_sync_button, "enable_remove_files_button": enable_remove_files_button, "enable_debug_button": enable_debug_button})


def get_all_cards(user_id=None):
    #   print(f"get_all_cards user_id: {user_id=}")
    if use_user_ids:
        all_cards = ydsql.user_select_all(ydd.Youtubedownloader, user_id)
    else:
        all_cards = ydsql.select_all(ydd.Youtubedownloader)
    #   print(f"{all_cards=}")
    return [convert_card_to_dict(card) for card in all_cards]


def convert_card_to_dict(card):
    return {
        "id": card.id,
        "card_id": card.card_id,
        "user_id": card.user_id,
        "filepath": card.filepath,
        "time_created": card.time_created,
        "should_keep": card.should_keep,
        "time_taken": card.time_taken,
        "video_tittle": card.video_tittle,  # Keeping original name, even if it's a typo
        "video_url": card.video_url,
        "video_channel_name": card.video_channel_name,
        "video_channel_link": card.video_channel_link,
        "video_thumbnail_link": card.video_thumbnail_link,
        "selected_type": card.selected_type,
        "best_available_resolution": card.best_available_resolution,
        "video_platform": card.video_platform,
        "selected_format": card.selected_format
    }


@app.route('/get-previous-cards', methods=['POST'])
def get_previous_cards():
    user_id = request.form.get('user-id')
    #   print(f"get_previous user_id: {user_id}")
    try:
        all_cards = get_all_cards(user_id)
    except Exception as e:
        print(f"Unable to get previous cards ERROR: {e}")

        return jsonify({"should_keep": False, "error": f"Unable to get previous cards"})

    return jsonify({"all_cards": all_cards})



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():

    print(f"{type(downloads)=}")

    start_time = time.time()

    user_id = request.form.get('user-id')
    print(f"{user_id=}")

    selected_type = request.form.get('input-menu-type')
    print(f"{selected_type=}")

    selected_format = request.form.get('format')
    print(f"{selected_format=}")

    input_value = request.form.get('input-bar')  # Get the input value from the form

    selected_option_resolution = request.form.get('input-menu-resolution')  # Get the selected resolution from the form

    card_id = request.form.get('card-id')  # Get the unique card ID

    video_platform = request.form.get('platform')
    print(f"{video_platform=}")

    server_ip = request.form.get('server-ip')
    print(f"{server_ip=}")

    try:

        if not selected_format or selected_format.lower() == "none":
            print(f"selected_format is not selected stopping")
            return jsonify({'card_id': card_id, 'should_keep': False, "error": f"format is not selected, stopped and removed card"})

        if is_livestream(input_value):
            print(f"{input_value} is a livestream stopping")
            return jsonify({'card_id': card_id, 'should_keep': False, "error": f"{input_value} is a livestream, stopped and removed card"})


        if check_if_video_exceeds_max_length(input_value):
            print(f"{input_value} is over the time limit stopping")
            return jsonify({'card_id': card_id, 'should_keep': False, "error": f"{input_value} is over the time limit, stopped and removed card"})


        video_title = get_video_title(input_value)
        print(f"{video_title=}")

        video_channel_name = get_video_channel_name(input_value)
        print(f"{video_channel_name=}")

        video_channel_link = get_video_channel_link(input_value)
        print(f"{video_channel_link=}")

        video_thumbnail_link = get_video_thumbnail(input_value)
        print(f"{video_thumbnail_link=}")

        best_resolution = get_best_available_resolution(input_value, selected_option_resolution)
        print(f"{best_resolution=}")

        try:
            if selected_type == "audio":
                if video_platform == "tiktok":
                    #   return jsonify({'card_id': card_id, 'should_keep': False})
                    download_link, filepath = download_tiktok_audio(input_value, card_id, server_ip, selected_format, "audios")
                else:
                    download_link, filepath = download_audio(input_value, card_id, server_ip, selected_format, "audios")
            else:
                if video_platform == "tiktok":
                    download_link, filepath = download_tiktok_video(input_value, card_id, server_ip, "videos")
                else:
                    download_link, filepath = download_youtube_video(input_value, card_id, server_ip, "videos", selected_option_resolution)
        except Exception as e:
            print(f"failed to download removing card\nError: {e}")
            return jsonify({'card_id': card_id, 'should_keep': False, "error": f"failed to download/get download link, removing card, this could happen if the resolution is too low"})
        print(f"{download_link=}")
        print(f"{filepath=}")

        # For now, we will mock the download link
        #   download_link = "https://www.example.com"  # Replace this with real download logic
        print(f"{card_id=}")
        end_time = time.time()

        add_record_to_database(
            card_id,
            user_id,
            filepath,
            True,
            int(round(end_time - start_time, 0)),
            video_title,
            input_value,
            video_channel_name,
            video_channel_link,
            video_thumbnail_link,
            selected_type,
            best_resolution,
            video_platform,
            selected_format
            )

        # Return the link and the card ID as JSON
        return jsonify({
            'card_id': card_id,
            'user_id': user_id,
            'download_link': download_link,
            'should_keep': True,
            "time_taken": round(end_time - start_time, 0),
            "video_title": video_title,
            "video_url": input_value,
            "video_channel_name": video_channel_name,
            "video_channel_link": video_channel_link,
            "video_thumbnail_link": video_thumbnail_link,
            "selected_type": selected_type,
            "best_available_resolution": best_resolution,
            "video_platform": video_platform,
        })
    except Exception as e:
        print(f"failed to download removing card\nError: {e}")
        return jsonify({'card_id': card_id, 'should_keep': False, "error": f"failed to download, removing card, this could have happened if the video is age retricted"})


@app.route('/files', methods=['POST'])
def handle_files_command():
    user_id = request.form.get('user-id')
    print(f"remove_files user_id: {user_id}")
    print("clearing files")
    # Clear downloadable files list
    downloads.clear()
    delete_downloads_list()
    to_be_deleted = remove_all_records(user_id)

    if use_user_ids:
        if not to_be_deleted:
            print("nothing to be deleted")
            return Response(status=204)  # No Content
        for record in to_be_deleted:
            print(f"to be deleted: {record=}")
            os.remove(record)
        return Response(status=204)  # No Content

    # List all files in the folder
    folders = os.listdir()
    print(folders)
    kept_folders = []
    for folder in folders:
        # print(f"current: {folder=}")
        if folder == "audios" or folder == "videos":
            # print(f"kept: {folder=}")
            kept_folders.append(folder)
        else:
            continue
            #   print(f"removed: {folder=}")
            #   folders.remove(folder)

    print(f"{kept_folders=}")

    # Iterate over each file and remove it
    for folder_name in kept_folders:
        for file in os.listdir(folder_name):
            file_path = os.path.join(folder_name, file)
            if os.path.isfile(file_path):  # Check if it's a file
                os.remove(file_path)
                print(f"Removed: {file_path}")
    return Response(status=204)  # No Content


def add_record_to_database(
        card_id: str,
        user_id: str,
        filepath: str,
        should_keep: bool,
        time_taken: int,
        video_title: str,
        video_url: str,
        video_channel_name: str,
        video_channel_link: str,
        video_thumbnail_link: str,
        selected_type: str,
        best_available_resolution: str,
        video_platform: str,
        selected_format: str
):
    current_time = time.time()
    record = (0, card_id, user_id, filepath, current_time, should_keep, time_taken, video_title, video_url, video_channel_name, video_channel_link, video_thumbnail_link, selected_type, best_available_resolution, video_platform, selected_format)
    newentry = ydd.Youtubedownloader.convert_from_tuple(record)
    ydsql.create_record(newentry)


def remove_all_records(user_id=None):
    print(f"deleting records")
    if use_user_ids:
        to_be_deleted = ydsql.user_delete_all(ydd.Youtubedownloader, user_id)
        return to_be_deleted
    else:
        ydsql.delete_all(ydd.Youtubedownloader)
        return


def remove_expired_records():
    print()
    records = ydsql.select_all(ydd.Youtubedownloader)
    for record in records:
        print(f"seconds since record created: {time.time() - record.time_created}")
        if time.time() - record.time_created > removal_time_seconds:
            print(f"deleted: {record.card_id}: {os.path.exists(os.path.abspath(record.filepath))}")
            os.remove(os.path.abspath(record.filepath))
            ydsql.delete_expired(ydd.Youtubedownloader, record.card_id)
    threading.Timer(checking_time_seconds, remove_expired_records).start()


def save_downloads_list():
    with open("downloads.json", "w") as file:
        json.dump(downloads, file)

def load_downloads_list():
    with open("downloads.json", "r") as file:
        loaded_data = json.load(file)
    return loaded_data

def delete_downloads_list():
    with open("downloads.json", "w") as file:
        file.truncate(0)
    print(f"downloads file cleared")



def demojize_filename(filename):
    safe_filename = demojize(filename)

    drive, path = os.path.splitdrive(safe_filename)

    safe_path = path.replace(":", "_")

    safe_filename = os.path.join(drive, safe_path)

    #   print(f"safe_filename: {type(safe_filename)}: {safe_filename}")

    if os.path.exists(filename):    # and filename != safe_filename
        #   print("in the os renamer for emojis")
        try:
            os.rename(filename, safe_filename)
        except Exception as e:
            print(f"could not rename file ERROR: {e}")
        print(f"{filename} -> {safe_filename}\nFile renamed successfully!")
        return safe_filename


def download_youtube_video(url, card_id, server_ip, save_path=".", max_resolution="1080p"):
    # Define resolution mapping (in case user enters just numbers)
    resolution_map = {
        "2160": "2160p", "1440": "1440p",
        "1080": "1080p", "720": "720p",
        "480": "480p", "360": "360p"
    }

    # Normalize resolution input
    #   max_resolution = resolution_map.get(max_resolution, max_resolution)
    #   print(f"{max_resolution=}")

    max_resolution = get_best_available_resolution(url, max_resolution)

    ydl_opts = {
        'format': f'bestvideo[vcodec^=avc1][height<={max_resolution[:-1]}]+bestaudio[ext=m4a]/b[vcodec^=avc1]',
        # Selects best H.264 video under max resolution
        'merge_output_format': 'mp4',  # Ensures MP4 output
        'postprocessors': [{  # Merges video & audio using FFmpeg
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'outtmpl': f'{save_path}/%(title)s_{max_resolution}_{card_id}.%(ext)s',  # Saves with video title
    }
    # print(f'{save_path}/%(title)s_{card_id}.%(ext)s')

    print(f"{ydl_opts['outtmpl']=}")

    #   with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #       ydl.download([url])

    # Start the download process using yt-dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Perform the download
        info_dict = ydl.extract_info(url, download=True)
        # Extract the file path from the info dictionary
        output_file = ydl.prepare_filename(info_dict)
        full_file_path = os.path.abspath(output_file)  # Get the full absolute path

    # Print the full path where the video is saved
    print(f"Audio saved at: {full_file_path}: {os.path.exists(full_file_path)}")

    try:
        full_file_path = demojize_filename(full_file_path)
        print(f"audio renamed to: {full_file_path}")

        #   print(f"Audio saved at: {full_file_path}: {os.path.exists(full_file_path)}")
    except Exception as e:
        print(f"failed to rename file without emojis \nERROR: {e}")

    downloads[card_id] = full_file_path
    save_downloads_list()
    if use_user_address:
        download_link = f"http://{ip_address}:{port}/downloads/{card_id}"
    else:
        download_link = f"http://{server_ip}/downloads/{card_id}"
    # print(download_link)
    return download_link, full_file_path


def download_audio(url, card_id, server_ip, selected_format="mp3", save_path="."):
    print(f"download_audio: {selected_format=}")
    if selected_format.lower() == "ogg":
        audio_format = "m4a"
    elif selected_format.lower() == "webm":
        audio_format = "m4a"
    elif selected_format.lower() == "aac":
        audio_format = "m4a"
    else:
        audio_format = selected_format.lower()

    ydl_opts = {
        'format': 'bestaudio/best',  # Select best available audio format
        'extract_audio': True,  # Extract only audio
        'audio_format': audio_format,  # Set preferred audio format (change to 'mp3' if needed)
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Ensures proper conversion of extracted audio
            'preferredcodec': audio_format,  # Convert to 'mp3' or 'm4a'
            'preferredquality': '192',  # Adjust bitrate (128, 192, 320 for mp3)
        }],
        'outtmpl': f'{save_path}/%(title)s_{card_id}.%(ext)s',  # Temporary file name before conversion
        'noplaylist': True,  # Ensure only the single audio is downloaded, not the entire playlist
    }

    print(f"Downloading audio to: {ydl_opts['outtmpl']}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        # print(f"{info_dict=}")
        output_file = ydl.prepare_filename(info_dict)
        print(f"{output_file=}")

        # Check the file path before and after conversion
        # After conversion, the extension should match the desired format (e.g., m4a, mp3)
        converted_file_path = output_file.replace(output_file.split('.')[-1], audio_format)

        full_file_path = os.path.abspath(converted_file_path)

    full_file_path = demojize_filename(full_file_path)

    if selected_format.lower() == "ogg":
        if use_fast_converting:
            os.rename(full_file_path.replace(full_file_path.split('.')[-1], "m4a"), full_file_path.replace(full_file_path.split('.')[-1], selected_format))
            full_file_path = full_file_path.replace(full_file_path.split('.')[-1], selected_format)
        else:
            ogg_file_path = full_file_path.replace(".m4a", ".ogg")
            subprocess.run(["ffmpeg", "-i", full_file_path, "-c:a", "libvorbis", "-q:a", "5", ogg_file_path], check=True)
            full_file_path = ogg_file_path  # Update the path after conversion

    if selected_format.lower() == "webm":
        if use_fast_converting:
            os.rename(full_file_path.replace(full_file_path.split('.')[-1], "m4a"), full_file_path.replace(full_file_path.split('.')[-1], selected_format))
            full_file_path = full_file_path.replace(full_file_path.split('.')[-1], selected_format)
        else:
            webm_file_path = full_file_path.replace(".m4a", ".webm")
            subprocess.run(["ffmpeg", "-i", full_file_path, "-c:a", "libopus", "-b:a", "128k", webm_file_path], check=True)
            full_file_path = webm_file_path  # Update the path after conversion

    if selected_format.lower() == "aac":
        if use_fast_converting:
            os.rename(full_file_path.replace(full_file_path.split('.')[-1], "m4a"), full_file_path.replace(full_file_path.split('.')[-1], audio_format))
            full_file_path = full_file_path.replace(full_file_path.split('.')[-1], audio_format)
        else:
            aac_file_path = full_file_path.replace(".m4a", ".aac")
            print(f"{aac_file_path=}")
            subprocess.run(["ffmpeg", "-i", full_file_path, "-c:a", "aac", "-b:a", "192k", aac_file_path], check=True)
            full_file_path = aac_file_path  # Update the path after conversion

    print(f"Audio saved at: {full_file_path}: {os.path.exists(full_file_path)}")

    downloads[card_id] = full_file_path
    save_downloads_list()
    if use_user_address:
        download_link = f"http://{ip_address}:{port}/downloads/{card_id}"
    else:
        download_link = f"http://{server_ip}/downloads/{card_id}"
    # print(download_link)
    return download_link, full_file_path




def sanitize_filename(title, max_length=100):
    """Removes invalid filename characters and trims length."""
    title = re.sub(r'[<>:"/\\|?*]', '', title)  # Remove illegal characters
    return title[:max_length].strip()  # Trim to avoid long filenames

def resolve_tiktok_short_url(short_url):
    """Expands shortened TikTok URLs (vm.tiktok.com/vt.tiktok.com) to full URLs."""
    response = requests.head(short_url, allow_redirects=True)
    return response.url


def convert_to_h264(input_file, output_file):
    """Converts a video to H.264 format using FFmpeg."""
    command = [
        "ffmpeg", "-y", "-i", input_file,
        "-c:v", "libx264", "-preset", "slow", "-crf", "23",  # Encode as H.264
        "-c:a", "aac", "-b:a", "128k",  # Keep audio quality
        output_file
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



def download_tiktok_video(url, card_id, server_ip, save_path="."):
    """Downloads a TikTok video in H.264 format, ensuring a valid filename."""

    if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
        url = resolve_tiktok_short_url(url)

    ydl_opts = {
        'format': 'bv*[vcodec^=avc1]+ba/b[ext=mp4]',  # Force H.264 (AVC)
        'merge_output_format': 'mp4',
        'postprocessors': [{'key': 'FFmpegVideoRemuxer', 'preferedformat': 'mp4'}],
        'outtmpl': f'{save_path}/temp_%(id)s_{card_id}.mp4',  # Safe naming
    }

    print(f"Downloading TikTok video: {url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = info_dict.get("title", "video")  # Extract title
        output_file = ydl.prepare_filename(info_dict)
        full_file_path = os.path.abspath(output_file)  # Get the full absolute path
        safe_title = sanitize_filename(title)  # Fix filename
        temp_file = os.path.join(save_path, f"temp_{safe_title}_{card_id}.mp4")
        final_file = os.path.join(save_path, f"final_{safe_title}_{card_id}.mp4")

    #   print(f"{full_file_path=}")
    #   print(f"{temp_file=}")
    #   print(f"{final_file=}")

    os.rename(full_file_path, temp_file)

    print(f"Converting to H.264: {temp_file} → {final_file}")
    convert_to_h264(temp_file, final_file)
    os.remove(temp_file)

    final_file = demojize_filename(final_file)

    downloads[card_id] = os.path.abspath(final_file)
    save_downloads_list()
    if use_user_address:
        download_link = f"http://{ip_address}:{port}/downloads/{card_id}"
    else:
        download_link = f"http://{server_ip}/downloads/{card_id}"
    # print(download_link)
    return download_link, os.path.abspath(final_file)


def download_tiktok_audio(url, card_id, server_ip, selected_format="mp3", save_path="."):
    """Downloads only the audio from a TikTok video in the specified format."""

    # Resolve TikTok short links
    if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
        url = resolve_tiktok_short_url(url)

    print(f"download_audio: {selected_format=}")
    if selected_format.lower() == "ogg":
        audio_format = "m4a"
    elif selected_format.lower() == "webm":
        audio_format = "m4a"
    elif selected_format.lower() == "aac":
        audio_format = "m4a"
    else:
        audio_format = selected_format.lower()

    ydl_opts = {
        'format': 'bestaudio/best',  # Ensure best available audio
        'extract_audio': True,  # Extract audio only
        'audio_format': audio_format,  # Convert to selected format
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,  # Convert to mp3, m4a, etc.
            'preferredquality': '192',  # Adjust bitrate (128, 192, 320)
        }],
        'outtmpl': f'{save_path}/temp_%(id)s_{card_id}.%(ext)s',  # Safe filename
        'noplaylist': True,  # Prevent playlist downloads
    }

    #   print(f"Downloading TikTok audio: {url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = info_dict.get("title", "video")  # Extract title
        output_file = ydl.prepare_filename(info_dict)  # Get temp filename
        full_file_path = os.path.abspath(output_file.replace(output_file.split('.')[-1], audio_format))  # Final filename
        safe_title = sanitize_filename(title)  # Fix filename
        temp_file = os.path.join(save_path, f"temp_{safe_title}_{card_id}.{selected_format}")
        final_file = os.path.join(save_path, f"final_{safe_title}_{card_id}.{selected_format}")

    #   print(f"{full_file_path=}")
    #   print(f"{temp_file=}")
    #   print(f"{final_file=}")




    if selected_format.lower() == "ogg":
        if use_fast_converting:
            os.rename(full_file_path.replace(full_file_path.split('.')[-1], "m4a"), full_file_path.replace(full_file_path.split('.')[-1], selected_format))
            full_file_path = full_file_path.replace(full_file_path.split('.')[-1], selected_format)
        else:
            ogg_file_path = full_file_path.replace(".m4a", ".ogg")
            subprocess.run(["ffmpeg", "-i", full_file_path, "-c:a", "libvorbis", "-q:a", "5", ogg_file_path], check=True)
            full_file_path = ogg_file_path  # Update the path after conversion

    if selected_format.lower() == "webm":
        if use_fast_converting:
            os.rename(full_file_path.replace(full_file_path.split('.')[-1], "m4a"), full_file_path.replace(full_file_path.split('.')[-1], selected_format))
            full_file_path = full_file_path.replace(full_file_path.split('.')[-1], selected_format)
        else:
            webm_file_path = full_file_path.replace(".m4a", ".webm")
            subprocess.run(["ffmpeg", "-i", full_file_path, "-c:a", "libopus", "-b:a", "128k", webm_file_path], check=True)
            full_file_path = webm_file_path  # Update the path after conversion

    if selected_format.lower() == "aac":
        if use_fast_converting:
            os.rename(full_file_path.replace(full_file_path.split('.')[-1], "m4a"), full_file_path.replace(full_file_path.split('.')[-1], audio_format))
            full_file_path = full_file_path.replace(full_file_path.split('.')[-1], audio_format)
        else:
            aac_file_path = full_file_path.replace(".m4a", ".aac")
            print(f"{aac_file_path=}")
            subprocess.run(["ffmpeg", "-i", full_file_path, "-c:a", "aac", "-b:a", "192k", aac_file_path], check=True)
            full_file_path = aac_file_path  # Update the path after conversion

    os.rename(full_file_path, final_file)

    full_file_path = final_file

    print(f"Audio saved at: {full_file_path}: {os.path.exists(full_file_path)}")

    final_file = demojize_filename(final_file)

    downloads[card_id] = os.path.abspath(final_file)
    save_downloads_list()
    if use_user_address:
        download_link = f"http://{ip_address}:{port}/downloads/{card_id}"
    else:
        download_link = f"http://{server_ip}/downloads/{card_id}"
    # print(download_link)
    return download_link, os.path.abspath(final_file)



def get_video_title(url):
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print(info["title"])
        return info["title"]


def get_video_channel_name(url):
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print(info.get('channel'))  # Prints the channel name
        return info.get('channel')


def get_video_channel_link(url):
    with yt_dlp.YoutubeDL({}) as ydl:
        info = ydl.extract_info(url, download=False)
        print(info.get('channel_url'))  # Prints the channel link
        return info.get('channel_url')


def get_video_thumbnail(url):
    # Create a yt-dlp object with a specific format for extracting metadata
    ydl_opts = {
        'quiet': True,  # Suppress output
        'extract_flat': True,  # Only get metadata (not download video)
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract info about the video
        info_dict = ydl.extract_info(url, download=False)

        # Get the thumbnail URL from the extracted information
        thumbnail_url = info_dict.get('thumbnail', None)
        return thumbnail_url



def is_livestream(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('is_live', False)



def get_best_available_resolution(url, max_resolution="1080p"):
    """Returns the highest available resolution up to the specified max resolution."""

    # Convert resolution string to an integer (e.g., "1080p" → 1080)
    def res_to_int(res):
        return int(res.replace("p", "")) if res else 0

    # Get available formats
    ydl_opts = {'quiet': True}  # Suppress unnecessary output
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    available_resolutions = set()

    for fmt in info.get('formats', []):
        if fmt.get('vcodec') != 'none':  # Ensure it's a video format
            height = fmt.get('height')
            if height:
                available_resolutions.add(f"{height}p")

    if not available_resolutions:
        return None  # No valid video resolutions found

    # Convert max_resolution to integer
    max_res_int = res_to_int(max_resolution)

    # Filter resolutions within the allowed limit and find the highest available
    filtered_resolutions = [res for res in available_resolutions if res_to_int(res) <= max_res_int]

    if not filtered_resolutions:
        return None  # No resolutions available within the limit

    # Return the highest available resolution within the limit
    return max(filtered_resolutions, key=res_to_int)


def check_if_video_exceeds_max_length(video_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False  # Ensure full metadata extraction
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            video_duration = info.get('duration', 0)  # Duration in seconds
            return video_duration > max_video_length_seconds
        except Exception as e:
            print(f"Error: {e}")
            return None  # Return None if there's an error


if __name__ == '__main__':
    if not use_automatic_removal_system:
        allow_sync_button = False
    try:
        downloads = load_downloads_list()
    except Exception as e:
        print(f"could not load downloads ERROR: {e}")
    if use_automatic_removal_system:
        remove_expired_records()
    if enable_automatic_browser_opening:
        webbrowser.open(f"http://{ip_address}:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
