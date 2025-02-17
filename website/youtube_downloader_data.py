from sqlalchemy.orm import declarative_base
from sqlalchemy import Column
from sqlalchemy import String, Integer

Base = declarative_base()


class Youtubedownloader(Base):
    __tablename__ = "youtube downloader"
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer)
    filepath = Column(String)
    time_created = Column(Integer)

    def __repr__(self):
        return f"Youtube downloader: {self.id}, {self.card_id}, {self.filepath}, {self.time_created},"

    def convert_to_tuple(self):  # Convert Container to tuple
        return self.id, self.card_id, self.filepath, self.time_created

    def valid(self):
        try:
            value = int(self.id)
        except ValueError:
            return False
        return value >= 0

    @staticmethod
    def convert_from_tuple(tuple_):
        youtube_downloader = Youtubedownloader(id=tuple_[0], card_id=tuple_[1], filepath=tuple_[2], time_created=tuple_[3])
        return youtube_downloader
