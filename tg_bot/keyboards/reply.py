from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """
    Универсальная клавиатура с командами и кнопками действий
    :param lang: язык пользователя ('ru' или 'en')
    :return: ReplyKeyboardMarkup
    """
    builder = ReplyKeyboardBuilder()
    
    # Общие команды для всех языков
    builder.button(text="/help")
    builder.button(text="/about")
    
    # Языкозависимые кнопки действий
    if lang == 'ru':
        builder.button(text="Получить погоду")
        builder.button(text="Кота!")
    else:
        builder.button(text="Get the weather")
        builder.button(text="Cat!")
    
    # Дополнительные кнопки в новом ряду
    builder.adjust(2, 2)  # 2 кнопки в первом ряду, 2 во втором
    
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..." if lang == 'ru' else "Select action..."
    )

def get_action_keyboard(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """
    Клавиатура только с основными действиями (погода и кот)
    :param lang: язык пользователя
    :return: ReplyKeyboardMarkup
    """
    builder = ReplyKeyboardBuilder()
    
    if lang == 'ru':
        builder.button(text="/start")
        builder.button(text="/help")
        builder.button(text="/language")
        builder.button(text="/roll")
        builder.button(text="/me")
    else:
        builder.button(text="/start")
        builder.button(text="/help")
        builder.button(text="/language")
        builder.button(text="/roll")
        builder.button(text="/me")
    
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..." if lang == 'ru' else "Select action..."
    )


def commands_keyboard(lang: str = 'ru'):
    """Клавиатура с основными командами"""
    builder = ReplyKeyboardBuilder()
    commands = ["help", "weather", "cat", "roll", "language"]
    for cmd in commands:
        builder.button(text=f"/{cmd}")
    builder.adjust(2)
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )