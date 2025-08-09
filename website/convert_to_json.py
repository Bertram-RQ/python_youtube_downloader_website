# export_to_json.py

import json
from sqlalchemy import create_engine, MetaData, Table, select

DATABASE_URL = "sqlite:///youtube_downloader_database.db"
engine = create_engine(DATABASE_URL)

def export_table_safe(table_name):
    try:
        meta = MetaData()
        meta.reflect(bind=engine, only=[table_name])
        table = meta.tables[table_name]

        with engine.connect() as conn:
            result = conn.execute(select(table))
            rows = []
            for row in result.mappings():  # returns dict-like rows
                rows.append(dict(row))
        return rows
    except Exception as e:
        print("unable to get table: ", table_name, " \nerror: ", e)
        return []

def export_database_to_json(filename):
    data = {}
    data["youtubedownloader"] = export_table_safe("youtube downloader")
    data["user_downloaded_videos"] = export_table_safe("user_downloaded_videos")
    data["user_settings"] = export_table_safe("user_settings")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"Database exported to {filename}")

if __name__ == "__main__":
    export_database_to_json("youtube_downloader_backup.json")
