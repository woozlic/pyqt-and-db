from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import hashlib

Base = declarative_base()


class ServerStorage:
    class Client(Base):
        __tablename__ = 'clients'
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True)
        password = Column(String)
        last_login = Column(DateTime, default=datetime.now)

        def __init__(self, username, password, last_login=None):
            self.username = username
            self.password = password
            self.last_login = last_login

        def __repr__(self):
            return self.username

    class ActiveClient(Base):
        __tablename__ = 'active_clients'
        id = Column(Integer, primary_key=True)
        client = Column(Integer, ForeignKey('clients.id'), unique=True)
        ip_address = Column(String)
        port = Column(Integer)
        login_time = Column(DateTime)

        def __init__(self, client, ip_address, port, login_time):
            self.client = client
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time

        def __repr__(self):
            return self.ip_address + ":" + self.port

    class LoginHistory(Base):
        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        client = Column(Integer, ForeignKey('clients.id'))
        ip_address = Column(String)
        port = Column(Integer)
        date_time = Column(DateTime)

        def __init__(self, client, ip_address, port, date_time):
            self.client = client
            self.ip_address = ip_address
            self.port = port
            self.date_time = date_time

        def __repr__(self):
            return self.ip_address + ":" + self.port

    def __init__(self, path):
        self.engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        Base.metadata.create_all(self.engine)

        Session = sessionmaker()
        self.session = Session(bind=self.engine)
        self.session.query(self.ActiveClient).delete()
        self.session.commit()

    def get_clients(self, user):
        print(user)
        return [c.username for c in self.session.query(self.Client).filter(self.Client.username != user).all()]

    def is_user_exist(self, username):
        return self.session.query(self.Client).filter_by(username=username).first()

    def check_user_online(self, user):
        if self.session.query(self.ActiveClient).filter_by(client=user.id).first():
            raise ValueError('User already logged in.')

    def register_user(self, username, password):
        res = self.session.query(self.Client).filter_by(username=username)
        if res.count():
            raise ValueError('User already exists')
        else:
            hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), username.lower().encode('utf-8'),
                                                  100000)
            user = self.Client(username=username, password=hashed_password)
            self.session.add(user)
            self.session.commit()

    def user_login(self, username, password, address, port):
        res = self.session.query(self.Client).filter_by(username=username)
        if res.count():
            user = res.first()
            if password == str(user.password):
                user.last_login = datetime.now()
            else:
                raise ValueError('Wrong password!')
        else:
            raise ValueError('User is not registered!')

        new_login_row = self.LoginHistory(client=user.id, ip_address=address, port=port, date_time=datetime.now())
        self.session.add(new_login_row)
        self.session.commit()

        self.check_user_online(user)

        new_active_row = self.ActiveClient(client=user.id, ip_address=address, port=port, login_time=datetime.now())
        self.session.add(new_active_row)
        self.session.commit()
        print(f'User {username} from {address}:{port} logged in')

    def user_logout(self, username):
        print(f'User {username} logged out')
        res = self.session.query(self.Client).filter_by(username=username)
        if res.count():
            client = res.first()
            self.session.query(self.ActiveClient).filter_by(client=client.id).delete()
            self.session.commit()
        else:
            print(f'User {username} does not exists')

    def get_active_users_list(self):
        query = self.session.query(
            self.Client.username,
            self.ActiveClient.ip_address,
            self.ActiveClient.port,
            self.ActiveClient.login_time
        ).join(self.Client)
        return query.all()

    def get_login_history(self, username=None):
        query = self.session.query(self.Client.username,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip_address,
                                   self.LoginHistory.port).join(self.Client)
        return query.all()


if __name__ == '__main__':
    test_db = ServerStorage()
    # Выполняем "подключение" пользователя
    test_db.user_login('client_1', '192.168.1.4', 8080)
    test_db.user_login('client_2', '192.168.1.5', 7777)

    # Выводим список кортежей - активных пользователей
    print(' ---- test_db.active_users_list() ----')
    print(test_db.get_active_users_list())

    # Выполняем "отключение" пользователя
    test_db.user_logout('client_1')
    # И выводим список активных пользователей
    print(' ---- test_db.active_users_list() after logout client_1 ----')
    print(test_db.get_active_users_list())

    # Запрашиваем историю входов по пользователю
    print(' ---- test_db.login_history(client_1) ----')
    print(test_db.get_login_history('client_1'))

    # и выводим список известных пользователей
    print(' ---- test_db.users_list() ----')
    print(test_db.get_active_users_list())
