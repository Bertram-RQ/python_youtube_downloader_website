from sqlalchemy.orm import declarative_base
from sqlalchemy import Column
from sqlalchemy import String, Integer, Boolean
import json
import time

Base = declarative_base()


class Youtubedownloader(Base):
    __tablename__ = "youtube downloader"
    id = Column(Integer, primary_key=True)
    card_id = Column(String)
    user_id = Column(String)
    filepath = Column(String)
    time_created = Column(Integer)
    should_keep = Column(Boolean, default=True)
    time_taken = Column(Integer)
    video_tittle = Column(String)
    video_url = Column(String)
    video_channel_name = Column(String)
    video_channel_link = Column(String)
    video_thumbnail_link = Column(String)
    selected_type = Column(String)
    best_available_resolution = Column(String)
    video_platform = Column(String)
    selected_format = Column(String)

    def __repr__(self):
        return f"Youtube downloader: {self.id}, {self.card_id}, {self.user_id}, {self.filepath}, {self.time_created}, {self.should_keep}, {self.time_taken}, {self.video_tittle}, {self.video_url}, {self.video_channel_name}, {self.video_channel_link}, {self.video_thumbnail_link}, {self.selected_type}, {self.best_available_resolution}, {self.video_platform}, {self.selected_format}"


    def convert_to_tuple(self):  # Convert Container to tuple
        return (self.id, self.card_id, self.user_id, self.filepath, self.time_created, self.should_keep, self.time_taken,
                self.video_tittle, self.video_url, self.video_channel_name, self.video_channel_link,
                self.video_thumbnail_link, self.selected_type, self.best_available_resolution, self.video_platform, self.selected_format)

    def valid(self):
        try:
            value = int(self.id)
        except ValueError:
            return False
        return value >= 0

    @staticmethod
    def convert_from_tuple(tuple_):
        youtube_downloader = Youtubedownloader(
            id=tuple_[0], card_id=tuple_[1], user_id=tuple_[2], filepath=tuple_[3], time_created=tuple_[4],
            should_keep=tuple_[5], time_taken=tuple_[6], video_tittle=tuple_[7], video_url=tuple_[8],
            video_channel_name=tuple_[9], video_channel_link=tuple_[10], video_thumbnail_link=tuple_[11],
            selected_type=tuple_[12], best_available_resolution=tuple_[13], video_platform=tuple_[14],
            selected_format=tuple_[15]
        )
        return youtube_downloader


class UserDownloadedVideos(Base):
    __tablename__ = "user_downloaded_videos"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    video_url = Column(String)
    video_title = Column(String)

    def __repr__(self):
        return f"user_downloaded_videos: {self.id}, {self.user_id}, {self.video_url}, {self.video_title}"

    def convert_to_tuple(self):
        return (self.id, self.user_id, self.video_url, self.video_title)

    def valid(self):
        try:
            value = int(self.id)
        except ValueError:
            return False
        return value >= 0

    @staticmethod
    def convert_from_tuple(tuple_):
        user_downloaded_videos = UserDownloadedVideos(
            id=tuple_[0], user_id=tuple_[1], video_url=tuple_[2], video_title=tuple_[3],
        )
        return user_downloaded_videos