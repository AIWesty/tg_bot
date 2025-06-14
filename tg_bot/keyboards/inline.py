from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yaml
from utils.i18n import translator
from aiogram.utils.keyboard import InlineKeyboardBuilder


def weather_keyboard() -> InlineKeyboardMarkup:
    with open('config/config.yaml', 'r', encoding='utf-8') as f: 
        config_data = yaml.safe_load(f) # открыли ямл файл с конфигом, прочитали информацию (защищённо)
        cities = config_data['weather']['cities']
        
    buttons = [] #список кнопок
    for city in cities: 
        button_row = [InlineKeyboardButton(text=city, callback_data=f"city_{city}")]
        buttons.append(button_row) #добавляем кнопки по списку городов
    
    return InlineKeyboardMarkup(inline_keyboard=buttons) #возвращаем класс клавиатуры с параметром нашего списка


def language_keyboard():
    builder = InlineKeyboardBuilder()
    for lang_code, lang_data in translator.locales.items():
        builder.button(
            text=lang_data.get("language_name", lang_code),
            callback_data=f"set_lang_{lang_code}"
        )
    return builder.as_markup()