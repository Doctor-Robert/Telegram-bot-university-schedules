import sqlite3

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

    cur.execute('''
        CREATE TABLE IF NOT EXISTS schedule(
            user_id INTEGER PRIMARY KEY,
            monday TEXT DEFAULT '',
            tuesday TEXT DEFAULT '',
            wednesday TEXT DEFAULT '',
            thursday TEXT DEFAULT '',
            friday TEXT DEFAULT '',
            saturday TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS info(
            user_id INTEGER PRIMARY KEY,
            user_status TEXT DEFAULT '',
            today_weekday_counter INTEGER DEFAULT 0,
            next_week TEXT DEFAULT 'False',
            today_weekday INTEGER DEFAULT 0, 
            delete_message_id INTEGER,
            message_chat_id INTEGER,
            flag_daily_notification TEXT DEFAULT 'Выключен ❌',
            flag_weekly_schedule TEXT DEFAULT 'Выключен ❌',
            FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('Kazgau.db')
    conn.row_factory = sqlite3.Row
    return conn


#user_id, nickname
def add_user(user_id, nickname):
    conn = get_db_connection()
    cur = conn.cursor()

    # Добавляем пользователя в таблицу users (только если нет)
    cur.execute(
        'INSERT OR IGNORE INTO users (user_id, nickname) VALUES (?, ?)',
        (user_id, nickname)
    )

    # ПРОВЕРЯЕМ, существует ли уже запись в info перед добавлением
    cur.execute('SELECT 1 FROM info WHERE user_id = ?', (user_id,))
    info_exists = cur.fetchone()
    
    if not info_exists:
        cur.execute(
            'INSERT INTO info (user_id) VALUES (?)',
            (user_id,)
        )
        print(f"Создана новая запись в info для пользователя {user_id}")
    else:
        print(f"Запись в info уже существует для пользователя {user_id}")
    
    # ПРОВЕРЯЕМ, существует ли уже запись в schedule перед добавлением
    cur.execute('SELECT 1 FROM schedule WHERE user_id = ?', (user_id,))
    schedule_exists = cur.fetchone()
    
    if not schedule_exists:
        cur.execute(
            'INSERT INTO schedule (user_id) VALUES (?)',
            (user_id,)
        )
        print(f"Создана новая запись в schedule для пользователя {user_id}")
    else:
        print(f"Запись в schedule уже существует для пользователя {user_id}")
    
    conn.commit()
    conn.close()

#flag_daily_notification
def add_flag_daily_notification(user_id, flag_daily_notification):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'UPDATE info SET flag_daily_notification = ? WHERE user_id = ?',
        (flag_daily_notification, user_id)
    )
    conn.commit()
    conn.close()

def get_flag_daily_notification(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT flag_daily_notification FROM info WHERE user_id = ?',
        (user_id,)
    )
    result = cur.fetchone()
    conn.close()
    if result:
        return result['flag_daily_notification']
    return ''

#flag_weekly_schedule
def add_flag_weekly_schedule(user_id, flag_weekly_schedule):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'UPDATE info SET flag_weekly_schedule = ? WHERE user_id = ?',
        (flag_weekly_schedule, user_id)
    )
    conn.commit()
    conn.close()

def get_flag_weekly_schedule(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT flag_weekly_schedule FROM info WHERE user_id = ?',
        (user_id,)
    )
    result = cur.fetchone()
    conn.close()
    if result:
        return result['flag_weekly_schedule']
    return ''


#group_name
def add_group_name(user_id, group_name):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'UPDATE users SET group_name = ? WHERE user_id = ?',
        (group_name, user_id)
    )
    conn.commit()
    conn.close()

def get_group_name(user_id):
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

#today_weekday_counter
def add_today_weekday_counter(user_id, today_weekday_counter):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'UPDATE info SET today_weekday_counter = ? WHERE user_id = ?',
        (today_weekday_counter, user_id)
    )
    conn.commit()
    conn.close()

def get_today_weekday_counter(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT today_weekday_counter FROM info WHERE user_id = ?',
        (user_id,)
    )
    result = cur.fetchone()
    conn.close()
    if result:
        return result['today_weekday_counter']
    return ''

#delete_message_id
def add_delete_message_id(user_id, delete_message_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'UPDATE info SET delete_message_id = ? WHERE user_id = ?',  # ИЗМЕНИТЕ НА UPDATE
        (delete_message_id, user_id)
    )
    conn.commit()
    conn.close()

def get_delete_message_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT delete_message_id FROM info WHERE user_id = ?',
        (user_id,)
    )
    result = cur.fetchone()
    conn.close()
    if result and result['delete_message_id']:
        return int(result['delete_message_id'])
    return None

#message_chat_id
def add_message_chat_id(user_id, message_chat_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'UPDATE info SET message_chat_id = ? WHERE user_id = ?',
        (message_chat_id, user_id)
    )
    conn.commit()
    conn.close()

def get_message_chat_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT message_chat_id FROM info WHERE user_id = ?',
        (user_id,)
    )
    result = cur.fetchone()
    conn.close()
    if result:
        return result['message_chat_id']
    return ''

#user_status
def add_user_status(user_id, user_status):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'UPDATE info SET user_status = ? WHERE user_id = ?',
        (user_status, user_id)
    )
    conn.commit()
    conn.close()

def get_user_status(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT user_status FROM info WHERE user_id = ?',
        (user_id,)
    )
    result = cur.fetchone()
    conn.close()
    if result:
        return result['user_status']
    return ''

#user_admin
def add_user_admin(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'UPDATE users SET user_admin = ? WHERE user_id = ?',
        ('yes', user_id)
    )
    conn.commit()
    conn.close()

def get_user_admin(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT user_admin FROM users WHERE user_id = ?',
        (user_id,)
    )
    result = cur.fetchone()
    conn.close()
    if result:
        return result['user_admin']
    return ''

#all_user_from_one_group
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

def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT * FROM users',
    )
    result = cur.fetchall()
    conn.close()

    return result

def get_all_info():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT * FROM info',
    )
    result = cur.fetchall()
    conn.close()

    return result

#Обновить расписание
def add_all_schedule(user_id, weekdays):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
            UPDATE schedule 
            SET monday = ?, tuesday = ?, wednesday = ?, thursday = ?, friday = ?, saturday = ?
            WHERE user_id = ?
        ''', (
            weekdays["0"][0] if weekdays["0"] else "Нет пар", 
            weekdays["1"][0] if weekdays["1"] else "Нет пар", 
            weekdays["2"][0] if weekdays["2"] else "Нет пар", 
            weekdays["3"][0] if weekdays["3"] else "Нет пар", 
            weekdays["4"][0] if weekdays["4"] else "Нет пар", 
            weekdays["5"][0] if weekdays["5"] else "Нет пар", 
            user_id
        ))

    conn.commit()
    conn.close()

def get_all_schedule(user_id):
    """Получает все расписание пользователя в формате словаря"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT monday, tuesday, wednesday, thursday, friday, saturday 
        FROM schedule WHERE user_id = ?
    ''', (user_id,))
    
    result = cur.fetchone()
    conn.close()
    
    if not result:
        return None
    
    # Преобразуем результат в словарь с номерами дней как ключи
    schedule_dict = {
        "0": result['monday'] if result['monday'] else "",
        "1": result['tuesday'] if result['tuesday'] else "",
        "2": result['wednesday'] if result['wednesday'] else "",
        "3": result['thursday'] if result['thursday'] else "",
        "4": result['friday'] if result['friday'] else "",
        "5": result['saturday'] if result['saturday'] else ""
    }
    
    return schedule_dict

def ensure_schedule_record_exists(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM schedule WHERE user_id = ?', (user_id,))
    result = cur.fetchone()
    
    if not result:
        cur.execute('INSERT INTO schedule (user_id) VALUES (?)', (user_id,))
        conn.commit()
    
    conn.close()

#next_week
def add_next_week(user_id, next_week):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'UPDATE info SET next_week = ? WHERE user_id = ?',
        (next_week, user_id)
    )
    conn.commit()
    conn.close()

def get_next_week(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT next_week FROM info WHERE user_id = ?',
        (user_id,)
    )
    result = cur.fetchone()
    conn.close()
    if result:
        return result['next_week']
    return False

#today_weekday
def add_today_weekday(user_id, today_weekday):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'UPDATE info SET today_weekday = ? WHERE user_id = ?',
        (today_weekday, user_id)
    )
    conn.commit()
    conn.close()

def get_today_weekday(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT today_weekday FROM info WHERE user_id = ?',
        (user_id,)
    )
    result = cur.fetchone()
    conn.close()
    if result:
        return result['today_weekday']
    return ''

#Получить день недели
def get_true_day(weekday, user_id):
    """Получает расписание для конкретного дня недели пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Сопоставляем номер дня с названием столбца
    day_columns = {
        0: 'monday',
        1: 'tuesday', 
        2: 'wednesday',
        3: 'thursday',
        4: 'friday',
        5: 'saturday'
    }
    
    column_name = day_columns.get(weekday)
    if not column_name:
        conn.close()
        return "❌ Неверный день недели"
    
    # Выполняем запрос
    cur.execute(f'SELECT {column_name} FROM schedule WHERE user_id = ?', (user_id,))
    result = cur.fetchone()
    conn.close()
    
    if result and result[column_name] and result[column_name] != "Нет пар":
        schedule_text = result[column_name]
        # Если текст все еще содержит квадратные скобки (на всякий случай)
        if schedule_text.startswith('[') and schedule_text.endswith(']'):
            schedule_text = schedule_text[1:-1]  # Убираем квадратные скобки
        if schedule_text.startswith("'") and schedule_text.endswith("'"):
            schedule_text = schedule_text[1:-1]  # Убираем кавычки
        return schedule_text
    else:
        return "📭 Пар на этот день нет\n\nМожно отдыхать! 🎉"