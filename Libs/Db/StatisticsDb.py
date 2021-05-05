from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, BOOLEAN, Boolean, MetaData, ForeignKey, Sequence, or_, DATE
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Statistics(Base):
    __tablename__ = 'Statistics'
    date = Column(DATE, primary_key=True)
    likes_count = Column(Integer, nullable=False, default=0)
    new_matches = Column(Integer, nullable=False, default=0)
    contacts_recieved = Column(Integer, nullable=False, default=0)
    matches_deleted = Column(Integer, nullable=False, default=0)
    social_contacts = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<User(date={self.date}" \
               f",likes_count={self.likes_count}" \
               f",new_matches={self.new_matches}" \
               f",contacts_recieved={self.contacts_recieved}" \
               f",matches_deleted={self.matches_deleted}" \
               f",social_contacts={self.social_contacts}" \
               f")>"


class StatisticsDb:
    @staticmethod
    def _session_maker():
        engine = create_engine('sqlite:///storage/tinderdb.sqlite?check_same_thread=False')
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        return session

    @staticmethod
    def _check_current_date_exists_in_db():
        session = StatisticsDb._session_maker()
        try:
            todays_row = session.query(Statistics).filter_by(date=datetime.date(datetime.now())).first()
            if todays_row is None:
                session.add(Statistics(date=datetime.date(datetime.now())))
                session.commit()
        except:
            pass
        finally:
            session.close()


    @staticmethod
    def increase_likes(count):
        StatisticsDb._check_current_date_exists_in_db()

        session = StatisticsDb._session_maker()
        try:
            todays_row = session.query(Statistics).filter_by(date=datetime.date(datetime.now())).first()
            todays_row.likes_count += count
            session.add(todays_row)
            session.commit()
        except:
            pass
        finally:
            session.close()

    @staticmethod
    def increase_new_matches(count=1):
        StatisticsDb._check_current_date_exists_in_db()

        session = StatisticsDb._session_maker()
        try:
            todays_row = session.query(Statistics).filter_by(date=datetime.date(datetime.now())).first()
            todays_row.new_matches += count
            session.add(todays_row)
            session.commit()
        except:
            pass
        finally:
            session.close()


    @staticmethod
    def increase_contacts_recieved():
        StatisticsDb._check_current_date_exists_in_db()

        session = StatisticsDb._session_maker()
        try:
            todays_row = session.query(Statistics).filter_by(date=datetime.date(datetime.now())).first()
            todays_row.contacts_recieved += 1
            session.add(todays_row)
            session.commit()
        except:
            pass
        finally:
            session.close()

    @staticmethod
    def derease_contacts_recieved():
        StatisticsDb._check_current_date_exists_in_db()

        session = StatisticsDb._session_maker()
        try:
            todays_row = session.query(Statistics).filter_by(date=datetime.date(datetime.now())).first()

            if todays_row.contacts_recieved >= 1: # only for today
                todays_row.contacts_recieved -= 1

            session.add(todays_row)
            session.commit()
        except:
            pass
        finally:
            session.close()

    @staticmethod
    def increase_matches_deleted():
        StatisticsDb._check_current_date_exists_in_db()

        session = StatisticsDb._session_maker()
        try:
            todays_row = session.query(Statistics).filter_by(date=datetime.date(datetime.now())).first()
            todays_row.matches_deleted += 1
            session.add(todays_row)
            session.commit()
        except:
            pass
        finally:
            session.close()

    @staticmethod
    def increase_social_contacts():
        StatisticsDb._check_current_date_exists_in_db()

        session = StatisticsDb._session_maker()
        try:
            todays_row = session.query(Statistics).filter_by(date=datetime.date(datetime.now())).first()
            todays_row.social_contacts += 1
            session.add(todays_row)
            session.commit()
        except:
            pass
        finally:
            session.close()

    @staticmethod
    def get_statistics_for_today():
        StatisticsDb._check_current_date_exists_in_db()

        session = StatisticsDb._session_maker()
        try:
            todays_row = session.query(Statistics).filter_by(date=datetime.date(datetime.now())).first()
        except:
            todays_row = Statistics()
        finally:
            session.close()


        return todays_row

    @staticmethod
    def clear_today():
        StatisticsDb._check_current_date_exists_in_db()

        session = StatisticsDb._session_maker()
        try:
            todays_row = session.query(Statistics).filter_by(date=datetime.date(datetime.now())).first()
            todays_row.social_contacts = 0
            todays_row.contacts_recieved = 0
            todays_row.matches_deleted = 0
            todays_row.new_matches = 0
            todays_row.likes_count = 0
            session.add(todays_row)
            session.commit()
        except:
            pass
        finally:
            session.close()