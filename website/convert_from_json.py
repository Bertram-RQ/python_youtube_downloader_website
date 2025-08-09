# import_from_json.py

import json
from youtube_downloader_sql import create_record
from youtube_downloader_data import Youtubedownloader, UserDownloadedVideos

def import_database_from_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Restore Youtubedownloader
    for row in data.get("youtubedownloader", []):
        create_record(Youtubedownloader, (
            row.get("id"),
            row.get("card_id"),
            row.get("user_id"),
            row.get("filepath"),
            row.get("time_created"),
            row.get("should_keep"),
            row.get("time_taken"),
            row.get("video_tittle"),
            row.get("video_url"),
            row.get("video_channel_name"),
            row.get("video_channel_link"),
            row.get("video_thumbnail_link"),
            row.get("selected_type"),
            row.get("best_available_resolution"),
            row.get("video_platform"),
            row.get("selected_format")
        ))

    # Restore UserDownloadedVideos
    for row in data.get("user_downloaded_videos", []):
        create_record(UserDownloadedVideos, (
            row.get("id"),
            row.get("user_id"),
            row.get("video_url"),
            row.get("video_title"),
            row.get("username"),
        ))

    # Restore UserDownloadedVideos
    for row in data.get("user_settings", []):
        create_record(UserDownloadedVideos, (
            row.get("id"),
            row.get("user_id"),
            row.get("username"),
            row.get("password"),
        ))

    print(f"Database restored from {filename}")


if __name__ == "__main__":
    import_database_from_json("youtube_downloader_backup.json")
