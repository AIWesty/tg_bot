from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yaml

def weather_keyboard() -> InlineKeyboardMarkup:
    with open('config/config.yaml', 'r', encoding='utf-8') as f: 
        config_data = yaml.safe_load(f) # открыли ямл файл с конфигом, прочитали информацию (защищённо)
        cities = config_data['weather']['cities']
        
    buttons = [] #список кнопок
    for city in cities: 
        button_row = [InlineKeyboardButton(text=city, callback_data=f"city_{city}")]
        buttons.append(button_row) #добавляем кнопки по списку городов
    
    return InlineKeyboardMarkup(inline_keyboard=buttons) #возвращаем класс клавиатуры с параметром нашего списка


        