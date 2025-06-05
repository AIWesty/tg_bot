#В данной версии бота используется библиотека request - синхронная библиотека для http запросов
#Однако в проекте мы таже используем асинхронный фреймворк aiogram
#Совмещать синхронный и асинхронный код является плохой практикой, но это сделано в учебных целях
#В продакшене рекомендуется придерживаться выбранного способо обработки(здесь можно использовать aiohttp)

from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message
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
    os.makedirs("temp", exist_ok=True)
    
    if not message.voice or not message.from_user or not message.bot: #проверяем существуют ли voice, user и bot 
        await message.answer("Ошибка: неверные параметры сообщения")
        return
    
    user = message.from_user
    
    
    try:
        voice_file = await message.bot.get_file(message.voice.file_id)
        if not voice_file.file_path: 
            await message.answer("Не удалось получить путь к файлу")
            return
            
        voice_path = f"temp/voice_{message.from_user.id}.ogg" #формируем путь к фременному файлу
        await message.bot.download_file(voice_file.file_path, voice_path) #загружаем файл с гс(откуда, куда)
        
        # Добавляем лог
        print(f"Файл сохранён: {voice_path}, размер: {os.path.getsize(voice_path)} байт")
        
        text = speech_to_text(voice_path)
        print(f"Распознанный текст: '{text}'")
        
        if text:
            await message.answer(f"Вы сказали: {text}")
        else:
            await message.answer("Не удалось распознать речь")
            
    except Exception as e:
        print(f"Ошибка обработки: {e}")
        await message.answer("Произошла ошибка при обработке голосового")
    finally:
        if os.path.exists(voice_path):
            os.remove(voice_path)
    
    log_message(user.id, f'Вызвал команду (обработка голосового сообщения)')
    
    
@router.message(F.location)
async def handle_location(message: Message) -> None:
    if not message.from_user or not message.location:
        return
    
    user = message.from_user
    
    
    try:
        lat = message.location.latitude
        lon = message.location.longitude
        
        #конфигурация для запроса к апи гео
        headers = {
            'User-Agent': 'YourBotName/1.0 (your@email.com)',
            'Accept-Language': 'ru-RU,ru;q=0.9'
        }
        
        #формируем ссылку для запроса
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        
        # формируем запрос с таймаутом
        try:
            api_response = requests.get(url, headers=headers, timeout=5)
            api_response.raise_for_status()  # ловим исключения 4хх/5хх
            
            response_data = api_response.json() # распаковываем в json полученные данные
            address = response_data.get("display_name", "Адрес не найден") #ищем локацию под display name
            
        except requests.exceptions.RequestException as e:
            log_errors(f"API request failed: {e}")
            address = "Не удалось получить данные о местоположении"
        except ValueError as e:  # Вложенные Json ошибки
            log_errors(f"Invalid API response: {e}")
            address = "Ошибка обработки данных местоположения"
            
        await message.answer(f"📍 Адрес: {address}") # отправка результата
        
    except Exception as e:
        log_errors("Unexpected error in location handler")
        await message.answer("⚠️ Произошла ошибка при обработке местоположения")
        
    log_message(user.id, f'Вызвал команду Location')