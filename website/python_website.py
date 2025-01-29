import time
import yt_dlp
import os

from flask import Flask, render_template, request, jsonify, send_file, Response
import webbrowser

ip_address = "127.0.0.1"
port = 5500

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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    start_time = time.time()
    selected_type = request.form.get('input-menu-type')
    print(f"{selected_type=}")
    selected_format = request.form.get('format')
    print(f"{selected_format=}")
    input_value = request.form.get('input-bar')  # Get the input value from the form
    selected_option_resolution = request.form.get('input-menu-resolution')  # Get the selected resolution from the form
    card_id = request.form.get('card-id')  # Get the unique card ID

    if not selected_format or selected_format.lower() == "none":
        print(f"selected_format is not selected stopping")
        return jsonify({'card_id': card_id, 'should_keep': False})

    video_title = get_video_title(input_value)
    print(f"{video_title=}")

    video_channel_name = get_video_channel_name(input_value)
    print(f"{video_channel_name=}")

    video_channel_link = get_video_channel_link(input_value)
    print(f"{video_channel_link=}")

    video_thumbnail_link = get_video_thumbnail(input_value)
    print(f"{video_thumbnail_link=}")

    try:
        if selected_type == "audio":
            download_link = download_audio(input_value, card_id, selected_format, "audios")
        else:
            download_link = download_video(input_value, card_id, "videos", selected_option_resolution)
    except Exception as e:
        print(f"failed to download removing card\nError: {e}")
        return jsonify({'card_id': card_id, 'should_keep': False})
    print(f"{download_link=}")

    # For now, we will mock the download link
    #   download_link = "https://www.example.com"  # Replace this with real download logic
    print(f"{card_id=}")
    end_time = time.time()

    # Return the link and the card ID as JSON
    return jsonify({'card_id': card_id,
                    'download_link': download_link,
                    'should_keep': True,
                    "time_taken": round(end_time - start_time, 0),
                    "video_title": video_title,
                    "video_url": input_value,
                    "video_channel_name": video_channel_name,
                    "video_channel_link": video_channel_link,
                    "video_thumbnail_link": video_thumbnail_link
                    })


@app.route('/files', methods=['POST'])
def handle_files_command():
    print("in here")
    # Clear downloadable files list
    downloads.clear()

    # List all files in the folder
    folders = os.listdir()
    print(folders)
    for folder in folders:
        print(f"{folder=}")
        if folder == "audios" or folder == "videos":
            continue
        else:
            folders.remove(folder)

    print(folders)

    # Iterate over each file and remove it
    for folder_name in folders:
        for file in os.listdir(folder_name):
            file_path = os.path.join(folder_name, file)
            if os.path.isfile(file_path):  # Check if it's a file
                os.remove(file_path)
                print(f"Removed: {file_path}")
    return Response(status=204)  # No Content


def download_video(url, card_id, save_path=".", max_resolution="1080p"):
    # Define resolution mapping (in case user enters just numbers)
    resolution_map = {
        "2160": "2160p", "1440": "1440p",
        "1080": "1080p", "720": "720p",
        "480": "480p", "360": "360p"
    }

    # Normalize resolution input
    max_resolution = resolution_map.get(max_resolution, max_resolution)
    print(f"{max_resolution=}")

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
    print(f'{save_path}/%(title)s_{card_id}.%(ext)s')

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

    downloads[card_id] = full_file_path
    download_link = f"http://{ip_address}:{port}/downloads/{card_id}"
    # print(download_link)
    return download_link


def download_audio(url, card_id, selected_format="mp3", save_path="."):
    print(f"download_audio: {selected_format=}")
    if selected_format.lower() == "ogg":
        audio_format = "m4a"
    elif selected_format.lower() == "webm":
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

    if selected_format.lower() == "ogg":
        os.rename(full_file_path.replace(full_file_path.split('.')[-1], "m4a"), full_file_path.replace(full_file_path.split('.')[-1], selected_format))
        full_file_path = full_file_path.replace(full_file_path.split('.')[-1], selected_format)

    if selected_format.lower() == "webm":
        os.rename(full_file_path.replace(full_file_path.split('.')[-1], "m4a"), full_file_path.replace(full_file_path.split('.')[-1], selected_format))
        full_file_path = full_file_path.replace(full_file_path.split('.')[-1], selected_format)

    if audio_format == "aac":
        os.rename(full_file_path.replace(full_file_path.split('.')[-1], "m4a"), full_file_path.replace(full_file_path.split('.')[-1], audio_format))

    print(f"Audio saved at: {full_file_path}: {os.path.exists(full_file_path)}")

    downloads[card_id] = full_file_path
    download_link = f"http://{ip_address}:{port}/downloads/{card_id}"
    return download_link


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


if __name__ == '__main__':
    webbrowser.open(f"http://{ip_address}:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
