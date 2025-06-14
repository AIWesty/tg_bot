from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def main_keyboard(lang: str = 'ru') -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    # Добавляем кнопки в зависимости от языка
    if lang == 'ru':
        builder.button(text="/help")
    else:
        builder.button(text="/help")
    return builder.as_markup(resize_keyboard=True)


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