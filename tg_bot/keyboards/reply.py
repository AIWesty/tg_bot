from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard():  #интерактивная клавиатура
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Получить погоду')],  #кнопки
            [KeyboardButton(text='Кота!')],
            
        ],
        resize_keyboard=True, #подстраиваться под размер окна
        input_field_placeholder="Выберите действие...", #плейсхолдер с подсказкой 
        
    )