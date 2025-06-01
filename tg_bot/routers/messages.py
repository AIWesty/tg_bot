#В данной версии бота используется библиотека request - синхронная библиотека для http запросов
#Однако в проекте мы таже используем асинхронный фреймворк aiogram
#Совмещать синхронный и асинхронный код является плохой практикой, но это сделано в учебных целях
#В продакшене рекомендуется придерживаться выбранного способо обработки(здесь можно использовать aiohttp)

from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, Location, Voice
from keyboards.reply import main_keyboard
from utils.logger import log_errors, log_message
from utils.speech import speech_to_text  #модуль распознования голоса
import requests
import os


router = Router()

@router.message(F.text.lower() == 'кота!')
async def send_cat(message: Message) -> None: #функция обработчик сообщения кота!(разного регистра)
    
    cat_api_url = 'https://api.thecatapi.com/v1/images/search' #url запроса к апи сайта с картинками
    response = requests.get(cat_api_url).json() # гет запрос по url, парсит Json ответ в словарь
    cat_url = response[0]['url'] #сайт изначально выдает не сразу картинку а json ответ со словарем, мы обращаемся к нему по ключу url, вытаскивая картинку
    
    if message.from_user is None: # проверяем наличие from_user
            await message.answer(cat_url, caption="Вот тебе котик! 🐱") 
            return
    user = message.from_user
        
    log_message(user.id, f'Вызвал команду (кота!))') #логирование команды
    
    await message.answer_photo(cat_url, caption="Вот тебе котик! 🐱") 
    
    

@router.message(F.text.lower() == 'получить погоду')
async def send_weather_menu(message: Message) -> None:  #обработчик функции получить погоду
    from keyboards.inline import weather_keyboard  #импортируем клавиатуру
    if message.from_user is None:
        await message.answer('Выберите город:', reply_markup=weather_keyboard())
        return
    user = message.from_user
    
    log_message(user.id, f'Вызвал команду (получить погоду)')
    
    #отвечаем и возвращаем клавиатуру с погодой
    await message.answer('Выберите город:', reply_markup=weather_keyboard())


@router.message(F.voice)
async def handle_voice(message: Message) -> None:
    """Обработка голосового сообщения с проверкой всех возможных None."""
    
    # Создаем папку темп если её нет
    os.makedirs("temp", exist_ok=True)
    
    # Проверяем, что message.voice существует
    if not message.voice:
        await message.answer("Не удалось получить голосовое сообщение")
        return
    
    if message.from_user is None:
        return

    if message.bot is None:
        return
    
    user = message.from_user
    
    # Получаем file_id (с проверкой)
    voice: Voice = message.voice
    file_id: str = voice.file_id
    
    try:
        # Получаем метаданные файла
        voice_file = await message.bot.get_file(file_id)
        
        # Проверяем file_path
        if not voice_file.file_path:
            await message.answer("Не удалось получить путь к файлу")
            return
            
        # Формируем путь для сохранения
        voice_path: str = f"temp/voice_{message.from_user.id}.ogg"
        
        # Скачиваем файл (теперь file_path точно str)
        await message.bot.download_file(
            file_path=voice_file.file_path,
            destination=voice_path
        )
        
        # Преобразуем в текст
        text: str = speech_to_text(voice_path)
        await message.answer(f"Вы сказали: {text}")
        
    except Exception as e:
        await message.answer("Произошла ошибка при обработке голосового")
        log_errors(e)
        
    finally:
        # Удаляем временный файл, если он существует
        if Path(voice_path).exists():
            Path(voice_path).unlink()
        
    log_message(user.id, f'Вызвал команду (обработка голосового сообщения)')