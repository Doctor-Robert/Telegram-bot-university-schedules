from all_function import parser_function, buttoms_functions, bd_functions
from datetime import datetime, date, timedelta
import telebot
import threading

from dotenv import load_dotenv
import os

load_dotenv()
TELEBOT_KEY = os.environ.get("TELEBOT_KEY")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

bd_functions.init_db()
bot = telebot.TeleBot(TELEBOT_KEY)


@bot.message_handler(commands=["start", "help"])
def start_handler(message):

    user_id, nickname = message.from_user.id, message.from_user.username
    # bd_functions.add_user(user_id, nickname)

    if message.text == "/start":

        bd_functions.add_today_weekday_counter(user_id, 0)
        group_name = bd_functions.get_group_name(user_id)

        if group_name and group_name != "":
            # Удаление сообщения
            delete_message_id = bd_functions.get_delete_message_id(user_id)
            if delete_message_id != None:
                bot.delete_messages(
                    message.chat.id, [delete_message_id, delete_message_id - 1]
                )

            # Отправка пользователю
            text = f"""
👋 <b>Привет!</b>

📊 Твоя группа: {group_name}

<i>Выбери действие ниже: 👇</i>
"""
            sent_message = bot.send_message(
                message.chat.id, text, reply_markup=buttoms_functions.main_menu_buttom(), parse_mode='HTML'
            )

            # обновление id удаленного сообщение
            bd_functions.add_delete_message_id(user_id, sent_message.message_id)
        else:
            text = "🎓 Добро пожаловать в бот расписания КазГАУ!\n\n📌 Для начала работы укажите вашу учебную группу\n\nПример: A123-45"
            bot.send_message(message.chat.id, text)

            bd_functions.add_user(user_id, nickname)
            bd_functions.add_data_of_reg(user_id, date.today())
            bd_functions.add_message_chat_id(user_id, message.chat.id)
            bd_functions.add_user_status(user_id, "waiting_for_group_input")

    elif message.text == "/help":
        text = '🆘 Центр поддержки\n\nПо вопросам модерации, сотрудничества или техническим проблемам обращайтесь к администратору: @admgrz\n\n⚠️ Если вы видите ошибку "Группа не найдена", но уверены что группа существует:\n\n1. Проверьте правильность написания группы\n2. Убедитесь что расписание опубликовано на текущую неделю\n3. Если расписания на текущую неделю нет - попробуйте добавить группу через неделю\n\nМы всегда рады помочь! 🤝'
        bot.send_message(message.chat.id, text)

@bot.message_handler(
    func=lambda message: bd_functions.get_user_status(message.from_user.id)
    in ["waiting_for_group_input", "waiting_password", "waiting_group_name"]
)
def find_user_group(message):
    user_id = message.from_user.id
    message_chat_id = message.chat.id

    # Добавление группы и ее проверка
    if bd_functions.get_user_status(user_id) == "waiting_for_group_input":
        group_name = message.text
        parser_function.check_and_add_user_group(user_id, group_name, message_chat_id)

    # Проверка пароля(админка)
    elif bd_functions.get_user_status(user_id) == "waiting_password":
        if message.text == ADMIN_PASSWORD:
            bd_functions.add_user_admin(user_id)

            bot.send_message(
                message.chat.id,
                text="✅ Доступ предоставлен\n\nТеперь вы администратор\n\n🛠 Доступные команды:\n/show_users - все пользователи\n/show_group_users - по группе",
            )
        else:
            bot.send_message(
                message.chat.id, text="❌ Доступ запрещен\n\nНеверный пароль"
            )

        bd_functions.add_user_status(user_id, "None")

    # Показать пользователей из одной группы
    elif bd_functions.get_user_status(user_id) == "waiting_group_name":
        group_name = message.text.upper()
        users = bd_functions.get_all_users_from_one_group(group_name)
        response = f"📊 Список пользователей из группы {group_name}:\n\n"
        for user in users:
            response += f"👤 @{user['nickname'] or 'нет'}, {user['group_name'] or 'не указана'}, {user['user_admin']}\n"

        try:
            bot.send_message(message.chat.id, response)
        except Exception as e:
            bot.send_message(message.chat.id, "Сообщение слишком большое")

        bd_functions.add_user_status(user_id, "None")

@bot.callback_query_handler(func=lambda callback: callback.data in ['change_the_group', 'settings', 'daily_notification', 'weekly_schedule', 'profile'])
def change_group(callback):
    user_id = callback.from_user.id

    try:
        bot.answer_callback_query(callback.id)
    except Exception as e:
        print(f"Ошибка ответа на callback: {e}")
    
    if callback.data == 'profile':
        group_name = bd_functions.get_group_name(user_id)
        notification_status = bd_functions.get_flag_daily_notification(user_id)
        registration_date = bd_functions.get_data_of_reg(user_id)
        if notification_status == 'Включен ✅':
            notification_status = "✅ ВКЛЮЧЕНЫ"
            notification_icon = "🔔"
        else:
            notification_status = "❌ ВЫКЛЮЧЕНЫ" 
            notification_icon = "🔕"
        text = f"""
👤 <b>ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ</b>
━━━━━━━━━━━━━━━━━━━━

<b>📋 ОСНОВНАЯ ИНФОРМАЦИЯ</b>
├ <b>📌Группа:</b> <code>{group_name or 'Не установлена'}</code>
├ {notification_icon} <b>Уведомления:</b> {notification_status}
└ 📅 <b>Регистрация:</b> <code>{registration_date or 'Неизвестно'}</code>

<b>🚀 ДОПОЛНИТЕЛЬНО</b>
╰ 🌟 Функции в разработке

━━━━━━━━━━━━━━━━━━━━
💡 Есть идеи по улучшению? 
📧 @admgrz
    """
        kb = buttoms_functions.profile_buttom()
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=text, reply_markup=kb, parse_mode='HTML')



    # Изменение группы
    if callback.data == 'change_the_group':
        bd_functions.add_user_status(user_id, 'waiting_for_group_input')
        bd_functions.add_group_name(user_id, '')

        text = '🔄 Смена группы\n\nВведите новое название группы:\n\nПример: А123-45'
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=text)

    # Настройки
    elif callback.data in ['settings', 'daily_notification', 'weekly_schedule']:
        if callback.data == 'daily_notification':
            if bd_functions.get_flag_daily_notification(user_id) == 'Выключен ❌':
                bd_functions.add_flag_daily_notification(user_id, 'Включен ✅')
            else:
                bd_functions.add_flag_daily_notification(user_id, 'Выключен ❌')

        if callback.data == 'weekly_schedule':
                if bd_functions.get_flag_weekly_schedule(user_id) == 'Выключен ❌':
                    bd_functions.add_flag_weekly_schedule(user_id, 'Включен ✅')
                else:
                    bd_functions.add_flag_weekly_schedule(user_id, 'Выключен ❌')

        flag_daily_notification = bd_functions.get_flag_daily_notification(user_id)
        flag_weekly_schedule = bd_functions.get_flag_weekly_schedule(user_id)

        kb = buttoms_functions.settings_buttom()
        if "Включен" in flag_daily_notification:
            daily_icon = "✅ Включены"
        else:
            daily_icon = "❌ Выключены"
        if "Включен" in flag_weekly_schedule:
            weekly_icon = "✅ Включено"
        else:
            weekly_icon = "❌ Выключено"

        text = f"""
<b>⚙️ НАСТРОЙКИ БОТА</b>
━━━━━━━━━━━━━━━━━━━━

<b>🔔 Ежедневные уведомления</b>
{daily_icon}

<b>📅 Недельное расписание</b>
{weekly_icon}

━━━━━━━━━━━━━━━━━━━━
<b>🆘 ПОМОЩЬ И ПОДДЕРЖКА</b>
По любым вопросам обращайтесь: 
👉 @admgrz
"""
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=text, reply_markup=kb, parse_mode='HTML')

@bot.callback_query_handler(func=lambda callback: callback.data in ['schedule', 'forward', 'back', 'main_menu','next_week','last_week'])
def check_schedule(callback):
    weekdays = None

    try:
        bot.answer_callback_query(callback.id)
    except Exception as e:
        print(f"Ошибка ответа на callback: {e}")

    user_id = callback.from_user.id
    group_name = bd_functions.get_group_name(user_id)

    # Кнопка расписание
    if callback.data == 'schedule':
        # Проверка на воскресенье
        today_day, today_weekday = parser_function.check_sunday()
        bd_functions.add_today_weekday(user_id, today_weekday)

        # Парсер
        link = f"https://kazgau.ru/obrazovanie/raspisanie-zanyatij/?filter=group&item={group_name}&date={today_day}"
        
        if parser_function.find_no_schedule_for_week(link):

            weekdays = parser_function.the_site_parser(link)
            bd_functions.ensure_schedule_record_exists(user_id)
            bd_functions.add_all_schedule(user_id, weekdays)

            if not weekdays:
                bot.send_message(callback.chat.id, "❌ Не удалось загрузить сайт\n\nПопробуйте позже")
                return
        else:
            kb = buttoms_functions.back_to_main_menu()
            text = "📅 Нет расписания на эту неделю"
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=text, reply_markup=kb)
            return

    # Главное меню
    if callback.data == 'main_menu':
        text = f"""
👋 <b>Привет!</b>

📊 Твоя группа: {group_name}

<i>Выбери действие ниже: 👇</i>
"""
        kb = buttoms_functions.main_menu_buttom()
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=text, reply_markup=kb, parse_mode='HTML')
        bd_functions.add_today_weekday_counter(user_id, 0)
        bd_functions.add_next_week(user_id, 'False')
        return

    # Кнопки вперед/назад
    if callback.data == 'forward':
        counter = bd_functions.get_today_weekday_counter(user_id) + 1
        bd_functions.add_today_weekday_counter(user_id, counter)
    elif callback.data == 'back':
        counter = bd_functions.get_today_weekday_counter(user_id) - 1
        bd_functions.add_today_weekday_counter(user_id, counter)

    # Кнопки Прошлая/Слудующая неделя
    if callback.data == 'next_week':

        # Нахождение следующий недели
        today_day, today_weekday = parser_function.check_sunday()
        counter = 7 - today_weekday
        today_day = today_day + timedelta(counter)
        link = f"https://kazgau.ru/obrazovanie/raspisanie-zanyatij/?filter=group&item={group_name}&date={today_day}"

        if parser_function.find_no_schedule_for_week(link):
            weekdays = parser_function.the_site_parser(link)
            bd_functions.add_all_schedule(user_id, weekdays)

            bd_functions.add_next_week(user_id, 'True')
            bd_functions.add_today_weekday(user_id, 0)
            bd_functions.add_today_weekday_counter(user_id, 0)
        else:
            kb = buttoms_functions.last_week_and_main_menu_buttom()
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
        weekdays = parser_function.the_site_parser(link)
        bd_functions.add_all_schedule(user_id, weekdays)

        bd_functions.add_next_week(user_id, "False")
        bd_functions.add_today_weekday(user_id, 0)
        bd_functions.add_today_weekday_counter(user_id, 5)

    if weekdays is None:
        weekdays = bd_functions.get_all_schedule(user_id)

    #Расписание по дням
    if bd_functions.get_flag_weekly_schedule(user_id) == 'Выключен ❌':
        show_weekday = bd_functions.get_today_weekday(user_id) + bd_functions.get_today_weekday_counter(user_id)


        # Проверка какую клавиатуру показывать в расписании
        kb = buttoms_functions.check_keyboard(show_weekday)

        # ПРОВЕРЯЕМ, что weekdays не None и содержит нужный ключ
        if weekdays is None or str(show_weekday) not in weekdays or not weekdays[str(show_weekday)]:
            bd_functions.ensure_schedule_record_exists(user_id)
            text = "📭 Пар на этот день нет\n\nМожно отдыхать! 🎉"
        else:
            bd_functions.ensure_schedule_record_exists(user_id)
            text = bd_functions.get_true_day(show_weekday, user_id)
    #Расписание на неделю
    else:
        text = "🎯 **РАСПИСАНИЕ НА НЕДЕЛЮ**\n\n"
        
        day_names = {
            '0': '📋 ПОНЕДЕЛЬНИК', 
            '1': '📋 ВТОРНИК', 
            '2': '📋 СРЕДА', 
            '3': '📋 ЧЕТВЕРГ', 
            '4': '📋 ПЯТНИЦА', 
            '5': '📋 СУББОТА'
        }
        
        for i, (day_num, day_name) in enumerate(day_names.items()):
            # Добавляем разделитель между днями
            if i > 0:
                text += "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
            
            text += f"**{day_name}**\n"
            
            if day_num in weekdays and weekdays[day_num]:
                day_text = str(weekdays[day_num][0]).strip("[]'")
                # Убираем дублирующее название дня и дату из текста
                lines = day_text.split('\n')
                # Пропускаем первую строку (название дня и дата)
                if lines and '⭐️' in lines[0]:
                    lines = lines[1:]
                day_text_clean = '\n'.join(lines)
                text += f"{day_text_clean}\n"
            else:
                text += "    🎉 Выходной - пар нет!\n"

        if bd_functions.get_next_week(user_id) == 'False':
            kb = buttoms_functions.next_week_and_main_menu()
        else:
            kb = buttoms_functions.last_week_and_main_menu_buttom()

    try:
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=text, reply_markup=kb, parse_mode='Markdown')
    except Exception as e:
        # Если сообщение не изменилось, игнорируем ошибку
        if "message is not modified" not in str(e):
            print(f"Ошибка при редактировании сообщения: {e}")

@bot.message_handler(commands=['admin', 'show_users', 'show_group_users'])
def admin_handler(message):
    user_id = message.from_user.id
    status_admin = bd_functions.get_user_admin(user_id)

    # Команда /admin
    if message.text == '/admin':
        if status_admin == 'no':
            bd_functions.add_user_status(user_id, 'waiting_password')
            bot.send_message(message.chat.id, '🔐 Административная панель\n\nДля доступа введите пароль:')
        elif status_admin == 'yes':
            text = "🛠 Панель администратора\n\nДоступные команды:\n• /show_users - все пользователи\n• /show_group_users - поиск по группе"
            bot.send_message(message.chat.id, text)
    
    # Команда /show_users
    elif message.text == '/show_users' and status_admin == 'yes':
        users = bd_functions.get_all_users()
        response = f"📊 Список пользователей (всего: {len(users)}):\n\n"

        for user in users:
            response += f"👤@{user['nickname'] or 'нет'}, {user['group_name'] or 'не указана'}, {user['user_admin']}\n"
        
        try:
            bot.send_message(message.chat.id, response)
        except Exception as e:
            bot.send_message(message.chat.id, f"Сообщение слишком большое, число пользователей = {len(users)}")

    # Команда /show_group_users
    elif message.text == '/show_group_users' and status_admin == 'yes':
        bd_functions.add_user_status(user_id, 'waiting_group_name')
        text = "👥 Поиск по группе\n\nВведите название группы для просмотра пользователей:\n\nПример: A123-45"
        bot.send_message(message.chat.id, text)

greeting_thread = threading.Thread(target=parser_function.daily_greating)
greeting_thread.daemon = True
greeting_thread.start()

bot.polling()
