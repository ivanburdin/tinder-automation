from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, BOOLEAN, Boolean, MetaData, ForeignKey, Sequence, or_, DATE
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Match(Base):
    __tablename__ = 'Matches'
    match_id = Column(String(50), primary_key=True)
    user_id = Column(String(25))
    name = Column(String(50))
    birth_date = Column(String(50))
    age = Column(Integer)
    bio = Column(String(1000))
    photos = Column(String(5000))
    photos_orig = Column(String(5000))
    photos_count = Column(Integer)
    pretty_conversation = Column(String(5000))
    instagram = Column(String(5000))
    telegram = Column(String(5000))
    whatsapp = Column(String(5000))
    notification_status = Column(String(50))

    def __repr__(self):
        return f"<User(match_id={self.match_id}" \
               f",tinder_id={self.user_id}" \
               f",name={self.name}" \
               f",birth_date={self.birth_date}" \
               f",age={self.age}" \
               f",bio={self.bio}" \
               f",photos={self.photos}" \
               f",photos_orig={self.photos_orig}" \
               f",photos_count={self.photos_count}" \
               f",pretty_conversation={self.pretty_conversation}" \
               f",instagram={self.instagram}" \
               f",telegram={self.telegram}" \
               f",whatsapp={self.whatsapp}" \
               f",notification_status={self.notification_status}" \
               f")>"


class TinderDb:

    @staticmethod
    def _session_maker():
        engine = create_engine('sqlite:///storage/tinderdb.sqlite?check_same_thread=False')
        Session = sessionmaker()
        Session.configure(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        return session

    @staticmethod
    def add_match(**kwargs):
        match = Match(**kwargs)
        session = TinderDb._session_maker()
        try:
            session.add(match)
            session.commit()
        except:
            pass
        finally:
            session.close()

    @staticmethod
    def delete_match(match_id):
        session = TinderDb._session_maker()
        try:
            session.query(Match).filter_by(match_id=match_id).delete()
            session.commit()
        except:
            pass
        finally:
            session.close()

    @staticmethod
    def delete_all_matches():
        session = TinderDb._session_maker()
        try:
            session.query(Match).all().delete()
            session.commit()
        except:
            pass
        finally:
            session.close()

    @staticmethod
    def get_match(match_id):
        session = TinderDb._session_maker()
        match_in_db = None
        try:
            match_in_db = session.query(Match).filter_by(match_id=match_id).first()
        except:
            pass
        finally:
            session.close()
        return match_in_db

    @staticmethod
    def search_match(string):
        string = f'%%%{string}%%%'
        session = TinderDb._session_maker()
        try:
            match_in_db = session.query(Match).filter(
                or_(
                    Match.whatsapp.ilike(string),
                    Match.telegram.ilike(string),
                    Match.instagram.ilike(string),
                    Match.bio.ilike(string),
                    Match.pretty_conversation.ilike(string)
                )
            ).first()
        except:
            pass
        finally:
            session.close()
        return match_in_db

    @staticmethod
    def match_exists(match_id):
        match_in_db = None
        session = TinderDb._session_maker()
        try:
            match_in_db = session.query(Match).filter_by(match_id=match_id).first()
        except:
            pass
        finally:
            session.close()
        return False if match_in_db is None else True

    @staticmethod
    def get_match_igs(match_id):
        match_in_db = None
        session = TinderDb._session_maker()
        try:
            match_in_db = session.query(Match).filter_by(match_id=match_id).first()
        except:
            pass
        finally:
            session.close()
        return match_in_db.instagram

    @staticmethod
    def get_match_tgs(match_id):
        match_in_db = None
        session = TinderDb._session_maker()
        try:
            match_in_db = session.query(Match).filter_by(match_id=match_id).first()
        except:
            pass
        finally:
            session.close()
        return match_in_db.telegram

    @staticmethod
    def get_match_was(match_id):
        match_in_db = None
        session = TinderDb._session_maker()
        try:
            match_in_db = session.query(Match).filter_by(match_id=match_id).first()
        except:
            pass
        finally:
            session.close()
        return match_in_db.whatsapp

    @staticmethod
    def add_to_notification_queue(**kwargs):
        match = Match(**kwargs)
        session = TinderDb._session_maker()
        try:
            session.add(match)
            session.commit()
        except:
            pass
        finally:
            session.close()

    @staticmethod
    def get_new_from_notification_queue():
        session = TinderDb._session_maker()
        try:
            result = session.query(Match).filter_by(notification_status='new')
            matches = [m for m in result]
        except:
            pass
        finally:
            session.close()
        return matches

    @staticmethod
    def push_notification_status(match):
        session = TinderDb._session_maker()
        try:
            session.query(Match).filter_by(match_id=match.match_id).update({'notification_status': 'sent'})
            session.commit()
        except:
            pass
        finally:
            session.close()