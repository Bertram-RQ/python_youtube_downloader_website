from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, update, delete
from youtube_downloader_data import Youtubedownloader, Base

import time



from sqlalchemy.engine import Engine
from sqlalchemy import event



Database = "sqlite:///youtube_downloader_database.db"


def create_record(record):
    with Session(engine) as session:
        record.id = None
        session.add(record)
        session.commit()

def select_all(classparam):
    with Session(engine) as session:
        records = session.scalars(select(classparam))
        result = []
        for record in records:
            #   print(record)
            result.append(record)
        return result

def get_record(classparam, record_id):
    with Session(engine) as session:
        record = session.scalars(select(classparam).where(classparam.id == record_id)).first()
    return record

def delete_expired(classparam, record_card_id):
    with Session(engine) as session:
        #   record = session.scalars(select(classparam).where(classparam.id == record_id)).first()
        session.execute(delete(classparam).where(classparam.card_id == record_card_id))
        session.commit()

def deleteall():
    with Session(engine) as session:
        session.execute(delete(Youtubedownloader))
        session.commit()












if __name__ == "__main__":
    engine = create_engine(Database, echo=False, future=True)
    Base.metadata.create_all(engine)
    #deleteall()
    #   print(select_all(Youtubedownloader))
    all_record = select_all(Youtubedownloader)
    for record in all_record:
        print(time.time() - record.time_created)
        if time.time() - record.time_created > 60:
            print(f"deleting: {record}")
            delete_expired(Youtubedownloader, record.card_id)
    # print("hi :D")
else:
    engine = create_engine(Database, echo=False, future=True)
    Base.metadata.create_all(engine)
    # print("you're not from here")
    print("database connected")


