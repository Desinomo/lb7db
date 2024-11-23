from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, Session, relationship
from datetime import datetime

# Підключення до бази даних
engine = create_engine('sqlite:///E:/python/messengers.db', echo=False)
Base = declarative_base()

# Оголошення класів моделей
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)

class Chats(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True)
    name = Column(String)  # Назва чату
    is_group_chat = Column(Integer, default=0)  # 0 - особистий чат, 1 - груповий чат
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatParticipants(Base):
    __tablename__ = 'chat_participants'

    chat_id = Column(Integer, ForeignKey('chats.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    chat = relationship("Chats")
    user = relationship("Users")

class Messages(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chats")
    sender = relationship("Users")

# Створення таблиць
Base.metadata.create_all(engine)

# Створення сесії
def create_session():
    return Session(engine)

# CRUD функції
def create_user(session, username, email):
    session.add(Users(username=username, email=email))
    session.commit()

def create_chat(session, name, is_group_chat):
    session.add(Chats(name=name, is_group_chat=is_group_chat))
    session.commit()

def add_participant(session, chat_id, user_id):
    session.add(ChatParticipants(chat_id=chat_id, user_id=user_id))
    session.commit()

def send_message(session, chat_id, sender_id, content):
    session.add(Messages(chat_id=chat_id, sender_id=sender_id, content=content))
    session.commit()

def get_chat_messages(session, chat_id):
    return session.query(Messages).filter(Messages.chat_id == chat_id).all()

def get_user_chats(session, user_id):
    return session.query(Chats).join(ChatParticipants).filter(ChatParticipants.user_id == user_id).all()

# Оновлення користувача (зміна ніка)
def update_user(session, user_id, new_username=None, new_email=None):
    user = session.query(Users).filter(Users.id == user_id).first()
    if user:
        if new_username:
            user.username = new_username
        if new_email:
            user.email = new_email
        session.commit()
    return user

# Оновлення повідомлення
def update_message(session, message_id, new_content):
    message = session.query(Messages).filter(Messages.id == message_id).first()
    if message:
        message.content = new_content
        session.commit()
    return message

# Видалення користувача
def delete_user(session, user_id):
    user = session.query(Users).filter(Users.id == user_id).first()
    if user:
        # Видалення повідомлень, де користувач є відправником
        session.query(Messages).filter(Messages.sender_id == user_id).delete()
        session.commit()

        # Видалення користувача
        session.delete(user)
        session.commit()
    return user

# Видалення повідомлення
def delete_message(session, message_id):
    message = session.query(Messages).filter(Messages.id == message_id).first()
    if message:
        session.delete(message)
        session.commit()
    return message

# Виконання коду
session = create_session()

# Додавання користувачів
users_data = [
    ("ІванКоваль", "ivan.koval@mail.com"),
    ("ОленаШевченко", "olena.shevchenko@mail.com"),
    ("МаксимМельник", "maksym.melnyk@mail.com"),
    ("КатеринаПетренко", "kateryna.petrenko@mail.com"),
    ("ВіталійЛисенко", "vitalii.lysenko@mail.com"),
    ("НаталіяСидоренко", "natalia.sydorenko@mail.com"),
    ("АндрійСавченко", "andrii.savchenko@mail.com"),
    ("МаріяДорошенко", "maria.doroshenko@mail.com"),
    ("ЮрійКовальчук", "yurii.kovalchuk@mail.com"),
    ("ДмитроГречко", "dmytro.hrechko@mail.com")
]

for username, email in users_data:
    create_user(session, username, email)

# Створення чатів
create_chat(session, "Іван & Олена", is_group_chat=0)  # Особистий чат між Іваном та Оленою
create_chat(session, "Максим & Катерина", is_group_chat=0)  # Особистий чат між Максимом та Катериною
create_chat(session, "Груповий чат", is_group_chat=1)  # Груповий чат для 6 осіб

# Додавання учасників до чатів
add_participant(session, 1, 1)  # Іван
add_participant(session, 1, 2)  # Олена
add_participant(session, 2, 3)  # Максим
add_participant(session, 2, 4)  # Катерина
add_participant(session, 3, 1)  # Іван
add_participant(session, 3, 2)  # Олена
add_participant(session, 3, 3)  # Максим
add_participant(session, 3, 4)  # Катерина
add_participant(session, 3, 5)  # Віталій
add_participant(session, 3, 6)  # Наталія
add_participant(session, 3, 7)  # Андрій

# Надсилання повідомлень
messages_data = [
    (1, 1, "Привіт, Олено, як ти?"),
    (1, 2, "Все добре, дякую! А ти?"),
    (2, 3, "Привіт, Катерино! Як справи?"),
    (2, 4, "Вітаю! Все в порядку!"),
    (3, 5, "Привіт усім! Як поживаєте?"),
    (3, 6, "Все супер, дякую за запитання!"),
    (3, 1, "Хлопці, давайте обговоримо наші плани!"),
    (3, 2, "Згоден, вже час щось вирішити!"),
    (3, 3, "Я готовий до змін!"),
    (3, 4, "Я також!"),
    (3, 5, "Давайте зробимо це!"),
    (3, 6, "Збираємося вже завтра?"),
    (3, 7, "Так, давайте!"),
    (2, 1, "Я на зв'язку, чекаю на вашу відповідь!"),
    (2, 4, "Все, що потрібно, вже готово!")
]

for chat_id, sender_id, content in messages_data:
    send_message(session, chat_id, sender_id, content)

# Оновлення користувача (зміна ніка)
updated_user = update_user(session, 1, new_username="ІванКовальUpdated")
print(f"Оновлений користувач: {updated_user.username}, {updated_user.email}")

# Оновлення повідомлення
updated_message = update_message(session, 1, "Привіт, Олено, як все?")
print(f"Оновлене повідомлення: {updated_message.content}")

# Видалення користувача
deleted_user = delete_user(session, 6)  # Видаляємо користувача Наталію
print(f"Видалений користувач: {deleted_user.username}")

# Видалення повідомлення
deleted_message = delete_message(session, 3)  # Видаляємо третє повідомлення
print(f"Видалене повідомлення: {deleted_message.content}")

# Виведення повідомлень з групового чату
group_chat_messages = get_chat_messages(session, 3)  # Вивести повідомлення з групового чату (чату з 6 користувачами)
print("Повідомлення в груповому чаті:")
for message in group_chat_messages:
    if message.sender:  # Перевірка на наявність користувача
        print(f"{message.sender.username}: {message.content}")
    else:
        print(f"Повідомлення без відправника: {message.content}")

# Виведення чатів для користувача
user_chats = get_user_chats(session, 1)  # Вивести чати для користувача з id 1
print(f"Чати для користувача з id 1:")
for chat in user_chats:
    print(chat.name)
