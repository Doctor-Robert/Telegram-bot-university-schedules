from telebot import types
from all_function import bd_functions
# Функция вызова кнопок главного меню
def main_menu_buttom():
    kb = types.InlineKeyboardMarkup()
    btm1 = types.InlineKeyboardButton(text="🎓 РАСПИСАНИЕ", callback_data= "schedule")
    btm2 = types.InlineKeyboardButton(text="👤 МОЙ ПРОФИЛЬ", callback_data= "profile")
    btm3 = types.InlineKeyboardButton(text="⚙️ НАСТРОЙКИ", callback_data= "settings")
    kb.add(btm1)
    kb.add(btm2, btm3)
    return kb

def profile_buttom():
    kb = types.InlineKeyboardMarkup(row_width=3)
    btm1 = types.InlineKeyboardButton(text="🔄 СМЕНИТЬ ГРУППУ", callback_data= "change_the_group")
    btm2 = types.InlineKeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ", callback_data= "main_menu")
    kb.add(btm1)
    kb.add(btm2)
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

def next_week_and_main_menu():
    kb = types.InlineKeyboardMarkup()
    btm1 = types.InlineKeyboardButton(text="📅 СЛЕД. НЕДЕЛЯ", callback_data= "next_week")
    btm3 = types.InlineKeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ", callback_data= "main_menu")
    kb.add(btm1)
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
    btm1 = types.InlineKeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ", callback_data= "main_menu")
    kb.add(btm1)
    return kb

def settings_buttom():
    kb = types.InlineKeyboardMarkup()
    btm1 = types.InlineKeyboardButton(text="🔔 ЕЖЕДНЕВНОЕ УВЕДОМЛЕНИЕ", callback_data= "daily_notification")
    btm2 = types.InlineKeyboardButton(text="📅 НЕДЕЛЬНОЕ РАСПИСАНИЕ", callback_data= "weekly_schedule")
    btm3 = types.InlineKeyboardButton(text="🏠 ГЛАВНОЕ МЕНЮ", callback_data= "main_menu")
    kb.add(btm1)
    kb.add(btm2)
    kb.add(btm3)
    return kb

def check_keyboard(today_weekday):
    if bd_functions.get_next_week == 'True':
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