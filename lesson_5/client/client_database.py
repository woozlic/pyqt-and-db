from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()


class ClientStorage:
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
        timestamp = DateTime()
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
        self.engine = create_engine(f'sqlite:///{username}_storage.db', echo=False, pool_recycle=7200)
        Base.metadata.create_all(self.engine)

        Session = sessionmaker()
        self.session = Session(bind=self.engine)

    def get_contacts(self):
        contacts = self.session.query(self.Contact).all()
        return [contact.username for contact in contacts]

    def is_contact_exists(self, username):
        contact_exists = self.session.query(self.Contact).filter_by(username=username).first()
        return contact_exists

    def add_contact(self, username: str):
        contact = self.Contact(username=username)
        self.session.add(contact)
        self.session.commit()

    def delete_contact(self, username: str):
        self.session.query(self.Contact).filter_by(username=username).delete()
        self.session.commit()

    def create_message(self, text: str, timestamp, from_=None, to=None):
        if from_:
            from_ = self.session.query(self.Contact).filter_by(username=from_).first()
            if not from_:
                self.add_contact(from_)
        if to:
            to = self.session.query(self.Contact).filter_by(username=to).first()
            if not to:
                self.add_contact(to)
        message = self.Message(text, timestamp, from_, to)
        self.session.add(message)
        self.session.commit()

    def get_messages(self):
        return self.session.query(self.Message).all()

    def delete_all_contacts(self):
        self.session.query(self.Contact).delete()

    def delete_all_messages(self):
        self.session.query(self.Message).delete()


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
