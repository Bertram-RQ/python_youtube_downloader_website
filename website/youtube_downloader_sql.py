from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, update, delete
from youtube_downloader_data import Youtubedownloader, UserDownloadedVideos, Base

import time



from sqlalchemy.engine import Engine
from sqlalchemy import event



Database = "sqlite:///youtube_downloader_database.db"


def create_record(classparam, data_tuple):
    """
    Create a record using a tuple and a class with `convert_from_tuple()` method.

    Example:
        create_record(UserData, (None, "123", "[]"))
    """
    with Session(engine) as session:
        record = classparam.convert_from_tuple(data_tuple)
        record.id = None  # optionally reset ID
        session.add(record)
        session.commit()
        return record


def select_all(classparam):
    with Session(engine) as session:
        records = session.scalars(select(classparam))
        result = []
        for record in records:
            #   print(record)
            result.append(record)
        return result


def user_select_all(classparam, user_id):
    #   with Session(engine) as session:
    #       records = session.scalars(select(classparam))
    #       #   print(records)
    #       result = []
    #       for record in records:
    #           #   print(record)
    #           if record.user_id == user_id:
    #               print(f"added: {record}")
    #               result.append(record)
    #           else:
    #               print(f"did not add: {record}")
    #       return result
    with Session(engine) as session:
        records = session.scalars(select(classparam).where(classparam.user_id == user_id))
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


def delete_all(classparam):
    with Session(engine) as session:
        session.execute(delete(classparam))
        session.commit()


def user_delete_all(classparam, user_id):
    with Session(engine) as session:
        records = user_select_all(classparam, user_id)
        results = []
        for record in records:
            results.append(record.filepath)

        session.execute(delete(classparam).where(classparam.user_id == user_id))
        session.commit()

        return results






if __name__ == "__main__":
    engine = create_engine(Database, echo=False, future=True)
    Base.metadata.create_all(engine)
    #deleteall()
    #   print(select_all(Youtubedownloader))
    all_record = select_all(Youtubedownloader)
    print(all_record)
    for record in all_record:
        print(time.time() - record.time_created)
        #   print(record)
        if time.time() - record.time_created > 600:
            print(f"deleting: {record}")
            delete_expired(Youtubedownloader, record.card_id)

    for record in all_record:
        print(record)

    all_record = select_all(UserDownloadedVideos)
    print(all_record)

    for record in all_record:
        print(record)

    # print("hi :D")
else:
    engine = create_engine(Database, echo=False, future=True)
    Base.metadata.create_all(engine)
    # print("you're not from here")
    print("database connected")


