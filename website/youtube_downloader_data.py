from sqlalchemy.orm import declarative_base
from sqlalchemy import Column
from sqlalchemy import String, Integer, Boolean

Base = declarative_base()


class Youtubedownloader(Base):
    __tablename__ = "youtube downloader"
    id = Column(Integer, primary_key=True)
    card_id = Column(String)
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
        return f"Youtube downloader: {self.id}, {self.card_id}, {self.filepath}, {self.time_created}, {self.should_keep}, {self.time_taken}, {self.video_tittle}, {self.video_url}, {self.video_channel_name}, {self.video_channel_link}, {self.video_thumbnail_link}, {self.selected_type}, {self.best_available_resolution}, {self.video_platform}, {self.selected_format}"


    def convert_to_tuple(self):  # Convert Container to tuple
        return (self.id, self.card_id, self.filepath, self.time_created, self.should_keep, self.time_taken,
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
            id=tuple_[0], card_id=tuple_[1], filepath=tuple_[2], time_created=tuple_[3],
            should_keep=tuple_[4], time_taken=tuple_[5], video_tittle=tuple_[6], video_url=tuple_[7],
            video_channel_name=tuple_[8], video_channel_link=tuple_[9], video_thumbnail_link=tuple_[10],
            selected_type=tuple_[11], best_available_resolution=tuple_[12], video_platform=tuple_[13],
            selected_format=tuple_[14]
        )
        return youtube_downloader
