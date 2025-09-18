from datetime import datetime, date
from datetime import timedelta
from datetime import datetime
from bs4 import BeautifulSoup
from telebot import types
import requests
import telebot
import sqlite3
import re
from dotenv import load_dotenv
import os

load_dotenv()
TELEBOT_KEY = os.environ.get("TELEBOT_KEY")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

bot = telebot.TeleBot(TELEBOT_KEY)

# Парсер (Парсит сайт и находит расписание)
def the_site_parser(link):
    try:
        response = requests.get(link, timeout=10)
        response.encoding = 'utf-8'
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети: {e}")
        return False
    
    soup = BeautifulSoup(response.text, 'lxml')
    answer = soup.find('div', id= 'schedule')

    if not answer:
        return False

    weekdays = {
        '0': [],        #понедельник
        '1': [],        #вторник
        '2': [],        #среда
        '3': [],        #четверг
        '4': [],        #пятница
        '5': []         #субота
    }

    value_user = answer.find_all('div')

    for i in range(4, len(value_user)):
        text = value_user[i].text.strip()

        if 'Понедельник' in value_user[i].text:
            ready_text = separation_weekday_parser(text)
            weekdays['0'].append(ready_text)
        elif 'Вторник' in value_user[i].text:
            ready_text = separation_weekday_parser(text)
            weekdays['1'].append(ready_text)
        elif 'Среда' in value_user[i].text:
            ready_text = separation_weekday_parser(text)
            weekdays['2'].append(ready_text)
        elif 'Четверг' in value_user[i].text:
            ready_text = separation_weekday_parser(text)
            weekdays['3'].append(ready_text)
        elif 'Пятница' in value_user[i].text:
            ready_text = separation_weekday_parser(text)
            weekdays['4'].append(ready_text)
        elif 'Суббота' in value_user[i].text:
            ready_text = separation_weekday_parser(text)
            weekdays['5'].append(ready_text)
    
    return weekdays

def separation_weekday_parser(weekday):
    weekday_value = ''.join(weekday).split('\n')

    old_time = None
    number = 0
    result = ''

    for lesson in weekday_value:
        time_math = re.search(r'\d{2}:\d{2}-\d{2}:\d{2}', lesson)

        if number != 0:
            result += (f"【{number} пара】 | {old_time}\n")

        if time_math:
            time = time_math.group()
            separated_lines = re.split(r'(?=Преподаватель:|Аудитория:|\d{2}:\d{2}-\d{2}:\d{2})', lesson)
            if separated_lines:
                if lesson == weekday_value[0]:
                    result += (f"⭐️ {separated_lines[0]}\n\n")
                else:
                    # Проверяем длину списка перед обращением к элементам
                    if len(separated_lines) >= 3:
                        result += (f"• {separated_lines[0]}\n• {separated_lines[1]}\n• {separated_lines[2]}\n")
                        result += f"\n"
                    elif len(separated_lines) >= 2:
                        result += (f"• {separated_lines[0]}\n• {separated_lines[1]}\n")
                        result += f"\n"
                    else:
                        result += (f"• {separated_lines[0]}\n")
                        result += f"\n"
        else:
            separated_lines = re.split(r'(?=Преподаватель:|Аудитория:)', lesson)
            if separated_lines:
                # Безопасное обращение к элементам списка
                if len(separated_lines) >= 3:
                    result += (f"• {separated_lines[0]}\n• {separated_lines[1]}\n• {separated_lines[2]}\n")
                elif len(separated_lines) >= 2:
                    result += (f"• {separated_lines[0]}\n• {separated_lines[1]}\n")
                else:
                    result += (f"• {separated_lines[0]}\n")
        
        old_time = time
        number += 1

    return result

# Создание базы данных
def init_db():
    conn = sqlite3.connect("Kazgau.db")
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            nickname TEXT,
            group_name TEXT DEFAULT '',
            user_admin TEXT DEFAULT 'no'
            )
    ''')
    conn.commit()
    conn.close()
init_db()

# Статус пользователя
user_status = {}
# Счетчики
today_weekday_counter = 0   # Счетчик перехода на предыдущий или следующий день недели
next_week = False           # Флаг, чтобы знать какая сегодня неделя
weekdays = []               # Список со всеми днями недели
today_weekday = 0           # Сегодняшний день недели
delete_message_id = None    # id сообщения которое надо удалить




# Телеграмм бот
@bot.message_handler(commands=['start','help'])
def start_handler(message):
    global today_weekday_counter
    global delete_message_id

    user_id = message.from_user.id
    nickname = message.from_user.username
    group_name = get_group(user_id)
    
    if message.text == '/start':
        today_weekday_counter = 0
        if group_name and group_name != '':
            kb = main_menu_buttom()
            text = f"👋 Привет!\n\n📊 Твоя группа: {group_name}\n\nВыбери действие ниже: 👇"

            # Удаление сообщения
            if delete_message_id != None:
                bot.delete_messages(message.chat.id, [delete_message_id, delete_message_id - 1])
            
            sent_message = bot.send_message(message.chat.id, text, reply_markup=kb)
            delete_message_id = sent_message.message_id
        else:
            text = '🎓 Добро пожаловать в бот расписания КазГАУ!\n\n📌 Для начала работы укажите вашу учебную группу\n\nПример: A123-45' 
            bot.send_message(message.chat.id, text)

            user_status[user_id] = 'waiting_for_group_input'
            add_user(user_id, nickname)
    elif message.text == '/help':
        text = '🆘 Центр поддержки\n\nПо вопросам модерации, сотрудничества или техническим проблемам обращайтесь к администратору: @admgrz\n\n⚠️ Если вы видите ошибку "Группа не найдена", но уверены что группа существует:\n\n1. Проверьте правильность написания группы\n2. Убедитесь что расписание опубликовано на текущую неделю\n3. Если расписания на текущую неделю нет - попробуйте добавить группу через неделю\n\nМы всегда рады помочь! 🤝'
        bot.send_message(message.chat.id, text)

# Ожидание статуса
@bot.message_handler(func=lambda message: user_status.get(message.from_user.id) in ['waiting_for_group_input', 'waiting_password', 'waiting_group_name'])
def find_user_group(message):
    user_id = message.from_user.id
    message_chat_id = message.chat.id

    # Добавление группы и ее проверка
    if user_status.get(user_id) == 'waiting_for_group_input':
        group_name = message.text
        check_and_add_user_group(user_id, group_name, message_chat_id)

    # Проверка пароля(админка)
    elif user_status.get(user_id) == 'waiting_password':
        if message.text == ADMIN_PASSWORD:
            update_user_admin(user_id)

            text = "✅ Доступ предоставлен\n\nТеперь вы администратор\n\n🛠 Доступные команды:\n/show_users - все пользователи\n/show_group_users - по группе"
            bot.send_message(message.chat.id, text)
        else:
            text = "❌ Доступ запрещен\n\nНеверный пароль"
            bot.send_message(message.chat.id, text)

        user_status[user_id] = None

    # Показать пользователей из одной группы
    elif user_status.get(user_id) == 'waiting_group_name':
        group_name = message.text.upper()
        users = get_all_users_from_one_group(group_name)
        response = f"📊 Список пользователей из группы {group_name}:\n\n"
        for user in users:
            response += f"👤 @{user['nickname'] or 'нет'}, {user['group_name'] or 'не указана'}, {user['user_admin']}\n" 
        
        try:
            bot.send_message(message.chat.id, response)
        except Exception as e:
            bot.send_message(message.chat.id, "Сообщение слишком большое")

        user_status[user_id] = None

# Изменение группы и помощь
@bot.callback_query_handler(func=lambda callback: callback.data in ['change_the_group', 'help'])
def change_group(callback):
    user_id = callback.from_user.id

    try:
        bot.answer_callback_query(callback.id)
    except Exception as e:
        print(f"Ошибка ответа на callback: {e}")
    
    # Изменение группы
    if callback.data == 'change_the_group':
        user_status[user_id] = 'waiting_for_group_input'
        add_group(user_id, '')

        text = '🔄 Смена группы\n\nВведите новое название группы:\n\nПример: А123-45'
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=text)

    # Помощь
    elif callback.data == 'help':
        kb = back_to_main_menu()
        text = '🆘 Центр поддержки\n\nПо вопросам модерации, сотрудничества или техническим проблемам обращайтесь к администратору: @admgrz\n\nМы всегда рады помочь! 🤝'
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=text, reply_markup=kb)

# Посмотреть расписание
@bot.callback_query_handler(func=lambda callback: callback.data in ['schedule', 'forward', 'back', 'main_menu','next_week','last_week'])
def check_schedule(callback):
    global today_weekday_counter
    global next_week
    global weekdays
    global today_weekday

    try:
        bot.answer_callback_query(callback.id)
    except Exception as e:
        print(f"Ошибка ответа на callback: {e}")

    user_id = callback.from_user.id
    group_name = get_group(user_id)

    # Кнопка расписание
    if callback.data == 'schedule':
        # Проверка на воскресенье
        today_day, today_weekday = check_sunday()

        # Парсер
        link = f"https://kazgau.ru/obrazovanie/raspisanie-zanyatij/?filter=group&item={group_name}&date={today_day}"
        if find_no_schedule_for_week(link):

            weekdays = the_site_parser(link)

            if not weekdays:
                bot.send_message(callback.chat.id, "❌ Не удалось загрузить сайт\n\nПопробуйте позже")
                return
        else:
            kb = back_to_main_menu()
            text = "📅 Нет расписания на эту неделю"
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=text, reply_markup=kb)
            return

    # Главное меню
    if callback.data == 'main_menu':
        text = f"👋 Привет!\n\n📊 Твоя группа: {group_name}\n\nВыбери действие ниже: 👇"
        kb = main_menu_buttom()
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=text, reply_markup=kb)
        today_weekday_counter = 0
        next_week = False
        return

    # Кнопки вперед/назад
    if callback.data == 'forward':
        today_weekday_counter += 1
    elif callback.data == 'back':
        today_weekday_counter -= 1

    # Кнопки Прошлая/Слудующая неделя
    if callback.data == 'next_week':

        # Нахождение следующий недели
        today_day, today_weekday = check_sunday()
        counter = 7 - today_weekday
        today_day = today_day + timedelta(counter)
        link = f"https://kazgau.ru/obrazovanie/raspisanie-zanyatij/?filter=group&item={group_name}&date={today_day}"

        if find_no_schedule_for_week(link):
            weekdays = the_site_parser(link)

            next_week = True
            today_weekday = 0
            today_weekday_counter = 0
        else:
            kb = last_week_and_main_menu_buttom()
            text = "📅 Нет расписания на эту неделю"
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=text, reply_markup=kb)
            return

    elif callback.data == 'last_week':
        today_weekday = datetime.today().weekday()
        
        # Проверка на воскресенье
        if today_weekday == 6:
            today_day = date.today() + timedelta(1)
        else:
            today_day = date.today()

        link = f"https://kazgau.ru/obrazovanie/raspisanie-zanyatij/?filter=group&item={group_name}&date={today_day}"
        weekdays = the_site_parser(link)

        next_week = False
        today_weekday = 0
        today_weekday_counter = 5

    show_weekday = today_weekday + today_weekday_counter


    # Проверка какую клавиатуру показывать в расписании
    kb = check_keyboard(show_weekday)

    if not weekdays[str(show_weekday)]:
        text = "📭 Пар на этот день нет\n\nМожно отдыхать! 🎉"
    else:
        text = weekdays[str(show_weekday)]
        
    try:
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=text, reply_markup=kb)
    except Exception as e:
        # Если сообщение не изменилось, игнорируем ошибку
        if "message is not modified" not in str(e):
            print(f"Ошибка при редактировании сообщения: {e}")

# Админка
@bot.message_handler(commands=['admin', 'show_users', 'show_group_users'])
def admin_handler(message):
    user_id = message.from_user.id
    status_admin = get_user_admin(user_id)

    # Команда /admin
    if message.text == '/admin':
        if status_admin == 'no':
            user_status[user_id] = 'waiting_password'
            bot.send_message(message.chat.id, '🔐 Административная панель\n\nДля доступа введите пароль:')
        elif status_admin == 'yes':
            text = "🛠 Панель администратора\n\nДоступные команды:\n• /show_users - все пользователи\n• /show_group_users - поиск по группе"
            bot.send_message(message.chat.id, text)
    
    # Команда /show_users
    elif message.text == '/show_users' and status_admin == 'yes':
        users = get_all_users()
        response = f"📊 Список пользователей (всего: {len(users)}):\n\n"

        for user in users:
            response += f"👤@{user['nickname'] or 'нет'}, {user['group_name'] or 'не указана'}, {user['user_admin']}\n"
        
        try:
            bot.send_message(message.chat.id, response)
        except Exception as e:
            bot.send_message(message.chat.id, f"Сообщение слишком большое, число пользователей = {len(users)}")

    # Команда /show_group_users
    elif message.text == '/show_group_users' and status_admin == 'yes':
        user_status[user_id] = 'waiting_group_name'
        text = "👥 Поиск по группе\n\nВведите название группы для просмотра пользователей:\n\nПример: A123-45"
        bot.send_message(message.chat.id, text)




# Функции вызова кнопок
# Функция вызова кнопок главного меню
def main_menu_buttom():
    kb = types.InlineKeyboardMarkup()
    btm1 = types.InlineKeyboardButton(text="🎓 РАСПИСАНИЕ", callback_data= "schedule")
    btm2 = types.InlineKeyboardButton(text="🔄 СМЕНИТЬ ГРУППУ", callback_data= "change_the_group")
    btm3 = types.InlineKeyboardButton(text="❓ ПОМОЩЬ", callback_data= "help")
    kb.add(btm1)
    kb.add(btm2, btm3)
    return kb

# Функция вызова кнопок вперед назад в расписании
def forward_backward_buttom():
    kb = types.InlineKeyboardMarkup(row_width=3)
    btm1 = types.InlineKeyboardButton(text="▶️ ВПЕРЕД", callback_data= "forward")
    btm2 = types.InlineKeyboardButton(text="◀️ НАЗАД", callback_data= "back")
    btm3 = types.InlineKeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ", callback_data= "main_menu")
    kb.add(btm2, btm1)
    kb.add(btm3)
    return kb

def backward_buttom():
    kb = types.InlineKeyboardMarkup()
    btm2 = types.InlineKeyboardButton(text="◀️ НАЗАД", callback_data= "back")
    btm3 = types.InlineKeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ", callback_data= "main_menu")
    kb.add(btm2)
    kb.add(btm3)
    return kb

def forward_buttom():
    kb = types.InlineKeyboardMarkup()
    btm2 = types.InlineKeyboardButton(text="▶️ ВПЕРЕД", callback_data= "forward")
    btm3 = types.InlineKeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ", callback_data= "main_menu")
    kb.add(btm2)
    kb.add(btm3)
    return kb

def backward_and_next_week_buttom():
    kb = types.InlineKeyboardMarkup()
    btm2 = types.InlineKeyboardButton(text="◀️ НАЗАД", callback_data= "back")
    btm1 = types.InlineKeyboardButton(text="📅 СЛЕД. НЕДЕЛЯ", callback_data= "next_week")
    btm3 = types.InlineKeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ", callback_data= "main_menu")
    kb.add(btm2,btm1)
    kb.add(btm3)
    return kb

def forward_and_last_week_buttom():
    kb = types.InlineKeyboardMarkup()
    btm2 = types.InlineKeyboardButton(text="▶️ ВПЕРЕД", callback_data= "forward")
    btm1 = types.InlineKeyboardButton(text="📅 ПРЕД. НЕДЕЛЯ", callback_data= "last_week")
    btm3 = types.InlineKeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ", callback_data= "main_menu")
    kb.add(btm1,btm2)
    kb.add(btm3)
    return kb

def last_week_and_main_menu_buttom():
    kb = types.InlineKeyboardMarkup()
    btm1 = types.InlineKeyboardButton(text="📅 ПРЕД. НЕДЕЛЯ", callback_data= "last_week")
    btm3 = types.InlineKeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ", callback_data= "main_menu")
    kb.add(btm1)
    kb.add(btm3)
    return kb

# Функция вызова кнопки вернуться в меню
def back_to_main_menu():
    kb = types.InlineKeyboardMarkup()
    btm1 = types.InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data= "main_menu")
    kb.add(btm1)
    return kb



# Функции базы данных
def get_db_connection():
    conn = sqlite3.connect('Kazgau.db')
    conn.row_factory = sqlite3.Row
    return conn

# Добавление в Базу Данных
def add_user(user_id, nickname):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'INSERT OR IGNORE INTO users (user_id, nickname) VALUES (?, ?)',
        (user_id, nickname)
    )
    conn.commit()
    conn.close()

def add_group(user_id, group_name):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'UPDATE users SET group_name = ? WHERE user_id = ?',
        (group_name, user_id)
    )
    conn.commit()
    conn.close()

def update_user_admin(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'UPDATE users SET user_admin = ? WHERE user_id = ?',
        ('yes', user_id)
    )
    conn.commit()
    conn.close()

# Извлечение из Базы Данных
def get_group(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT group_name FROM users WHERE user_id = ?',
        (user_id,)
    )
    result = cur.fetchone()
    conn.close()
    if result:
        return result['group_name']
    return ''

def get_user_admin(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT user_admin FROM users WHERE user_id = ?',
        (user_id,)
    )
    result = cur.fetchone()
    conn.close()

    return result['user_admin']

def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT * FROM users',
    )
    result = cur.fetchall()
    conn.close()

    return result

def get_all_users_from_one_group(group_name):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT * FROM users WHERE group_name = ?',
        (group_name,)
    )
    result = cur.fetchall()
    conn.close()

    return result




# Функция поиска группы и ее добавление в БД
def check_and_add_user_group(user_id, group_name, message_chat_id):
    global delete_message_id

    today_weekday = datetime.today().weekday()

    # Проверка, что сегодня не воскресенье и понедельник
    if today_weekday in [5, 6]:
        today_day = date.today()
        count_for_next_week = 7 - today_weekday
        day = today_day + timedelta(days=count_for_next_week)

        link = f'https://kazgau.ru/obrazovanie/raspisanie-zanyatij/?filter=group&item={group_name}&date={day}'
    else:
        link = f'https://kazgau.ru/obrazovanie/raspisanie-zanyatij/?filter=group&item={group_name}'
    
    response = requests.get(link)

    # Поиск сегоднешнего дня недели

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        schedule = (soup.find('div', id= 'schedule')).text
        
        if not 'Нет расписания на выбранную неделю' in schedule:
            add_group(user_id, group_name.upper())
            user_status[user_id] = None

            kb = main_menu_buttom()

            text = f"✅ Отлично! Группа сохранена!\n\n• Группа: {group_name.upper()}\n• Статус: 🎉 Добавлена\n\nТеперь вы можете просматривать расписание!"
            sent_message = bot.send_message(message_chat_id, text, reply_markup=kb, parse_mode='Markdown')
            delete_message_id = sent_message.message_id
        else:
            text = f'❌ Группа {group_name} не найдена.\n\nПроверьте:\n• Правильность написания\n• Формат (например: А123-45)\n• Актуальность группы\n\nПопробуйте еще раз или воспользуйтесь командой /help:'
            bot.send_message(message_chat_id, text)
    else:
        text = "🌐 Ошибка соединения\n\nСайт временно недоступен\nПовторите попытку позже"
        bot.send_message(message_chat_id, text)

# Проверка какую клавиатуру показывать в расписании
def check_keyboard(today_weekday):
    if next_week:
        if today_weekday == 0:
                kb = forward_and_last_week_buttom()
        elif today_weekday == 5:
            kb = backward_buttom()
        else:
            kb = forward_backward_buttom()
    else:
        if today_weekday == 0:
            kb = forward_buttom()
        elif today_weekday == 5:
            kb = backward_and_next_week_buttom()
        else:
            kb = forward_backward_buttom()
    return kb  

# Проверка на воскресенье
def check_sunday():
    if datetime.today().weekday() == 6:
        today_day = date.today() + timedelta(1)
        today_weekday = 0
    else:
        today_day = date.today()
        today_weekday = datetime.today().weekday()
    return today_day, today_weekday

# Проверка на пустую неделю
def find_no_schedule_for_week(link):
    response = requests.get(link)
    flag = True

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        schedule = (soup.find('div', id= 'schedule')).text
        
        if 'Нет расписания на выбранную неделю' in schedule:
            flag = False

    else:
        flag = False
    return flag

bot.polling()
