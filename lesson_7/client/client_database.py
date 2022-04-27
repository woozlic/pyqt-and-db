from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class ClientStorage:
    """
    Class that contains ORM classes for DB tables
    """
    class Contact(Base):
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True, nullable=False)

        def __init__(self, username):
            self.username = username

        def __repr__(self):
            if self.username:
                return self.username
            else:
                return 'WTF?'

    class Message(Base):
        __tablename__ = 'messages'
        id = Column(Integer, primary_key=True)
        from_ = Column(Integer, ForeignKey('contacts.id'), nullable=True)
        to = Column(Integer, ForeignKey('contacts.id'), nullable=True)
        timestamp = Column(DateTime)
        text = Column(Text)

        def __init__(self, text: str, timestamp, from_=None, to=None):
            # to=None means to self, from_=None means from self
            self.text = text
            self.timestamp = timestamp
            self.from_ = from_
            self.to = to

        def __repr__(self):
            return self.text

    def __init__(self, username: str):
        self.username = username
        current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{username}_storage.db')
        self.engine = create_engine(f'sqlite:///{current_dir}', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        Base.metadata.create_all(self.engine)
        Session = sessionmaker()
        self.session = Session(bind=self.engine)

    def get_history(self, current_chat):
        """Returns messages history for user and current chat"""
        messages_from = self.session.query(self.Message).filter_by(from_=current_chat)
        messages_to = self.session.query(self.Message).filter_by(to=current_chat)
        messages_from = [(m.from_, m.to, m.timestamp, m.text) for m in messages_from]
        messages_to = [(m.from_, m.to, m.timestamp, m.text) for m in messages_to]
        print([i[2] for i in messages_to])
        history = sorted([*messages_from, *messages_to], key=lambda x: x[2])  # datetime.strptime(x[2],
        return history

    def get_contacts(self):
        """Returns user's contacts"""
        contacts = self.session.query(self.Contact).all()
        return [contact.username for contact in contacts]

    def is_contact_exists(self, username: str):
        """Checks if user is in the contacts list"""
        contact_exists = self.session.query(self.Contact).filter_by(username=username).first()
        return contact_exists

    def add_contact(self, username: str):
        """Add user to contacts list"""
        contact = self.Contact(username=username)
        self.session.add(contact)
        self.session.commit()

    def delete_contact(self, username: str):
        """Delete user from contacts list"""
        self.session.query(self.Contact).filter_by(username=username).delete()
        self.session.commit()

    def create_message(self, text: str, timestamp, from_=None, to=None):
        """Create JIM-message for sending"""
        if from_:
            if not self.is_contact_exists(from_) and from_ != to and self.username != from_:
                self.add_contact(from_)
        if to:
            if not self.is_contact_exists(to) and from_ != to and self.username != to:
                self.add_contact(to)
        message = self.Message(text, timestamp, from_, to)
        self.session.add(message)
        self.session.commit()

    def get_messages(self):
        """Returns all messages from DB"""
        return self.session.query(self.Message).all()

    def delete_all_contacts(self):
        """Deletes all user's contacts"""
        self.session.query(self.Contact).delete()
        self.session.commit()

    def delete_all_messages(self):
        """Deletes all messages"""
        self.session.query(self.Message).delete()
        self.session.commit()


if __name__ == '__main__':
    storage = ClientStorage('guest')
    storage.delete_all_contacts()
    storage.delete_all_messages()
    print('Empty', storage.get_contacts())
    storage.add_contact('test_1')
    print('Added 1', storage.get_contacts())
    storage.add_contact('test_1')
    print('Added the same', storage.get_contacts())
    storage.delete_contact('test_1')
    print('Deleted 1', storage.get_contacts())
    storage.create_message('Hello, test_1!', datetime.now(), 'test_2', 'test_1')
    print('test_2 -> test_1', storage.get_messages())
    storage.create_message('Hello, test_2!', datetime.now(), 'test_1', 'test_2')
    print('test_1 -> test_2', storage.get_messages())
