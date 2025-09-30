from all_function import bd_functions, buttoms_functions
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
import requests
import telebot
import re

from dotenv import load_dotenv
import os

load_dotenv()
TELEBOT_KEY = os.environ.get("TELEBOT_KEY")
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

def check_and_add_user_group(user_id, group_name, message_chat_id):
    
    today_weekday = datetime.today().weekday()

    # Проверка, что сегодня не воскресенье и понедельник
    if today_weekday in [5, 6]:
        today_day = date.today()
        count_for_next_week = 7 - today_weekday
        day = today_day + timedelta(days=count_for_next_week)

        link = f'https://kazgau.ru/obrazovanie/raspisanie-zanyatij/?filter=group&item={group_name}&date={day}'
    else:
        today_day = date.today()
        link = f'https://kazgau.ru/obrazovanie/raspisanie-zanyatij/?filter=group&item={group_name}&date={today_day}'
    
    response = requests.get(link)

    # Поиск сегоднешнего дня недели

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        schedule = (soup.find('div', id= 'schedule')).text
        
        if not 'Нет расписания на выбранную неделю' in schedule:
            bd_functions.add_group_name(user_id, group_name.upper())
            group_name = bd_functions.get_group_name(user_id)
            bd_functions.add_user_status(user_id, 'None')

            text = f"✅ Отлично! Группа сохранена!\n\n• Группа: {group_name.upper()}\n• Статус: 🎉 Добавлена\n\nТеперь вы можете просматривать расписание!"
            sent_message = bot.send_message(message_chat_id, text, reply_markup=buttoms_functions.main_menu_buttom(), parse_mode='Markdown')

            bd_functions.add_delete_message_id(user_id, sent_message.message_id)
        else:
            text = f'❌ Группа {group_name} не найдена.\n\nПроверьте:\n• Правильность написания\n• Формат (например: А123-45)\n• Актуальность группы\n\nПопробуйте еще раз или воспользуйтесь командой /help:'
            bot.send_message(message_chat_id, text)
    else:
        text = "🌐 Ошибка соединения\n\nСайт временно недоступен\nПовторите попытку позже"
        bot.send_message(message_chat_id, text)

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

def check_sunday():
    if datetime.today().weekday() == 6:
        today_day = date.today() + timedelta(1)
        today_weekday = 0
    else:
        today_day = date.today()
        today_weekday = datetime.today().weekday()
    return today_day, today_weekday