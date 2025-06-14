#В данной версии бота используется библиотека request - синхронная библиотека для http запросов
#Однако в проекте мы таже используем асинхронный фреймворк aiogram
#Совмещать синхронный и асинхронный код является плохой практикой, но это сделано в учебных целях
#В продакшене рекомендуется придерживаться асинхронной обработки(здесь можно использовать aiohttp)

from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply import main_keyboard
from database.crud import get_user_language
from utils.logger import logger
from utils.i18n import translator
from utils.speech import speech_to_text  #модуль распознования голоса
from utils.fallbacks import fallback
import requests
import os


router = Router()

@router.message(F.text.lower() == 'кота!')
async def send_cat(message: Message) -> None: #функция обработчик сообщения кота!(разного регистра)
    
    if not message.from_user: #проверяем наличие пользователя 
        return
    
    user = message.from_user
    lang = get_user_language(user.id)  # Получаем язык пользователя
    logger.log_message(user.id, translator.get('cat_command_log', lang)) #логируем вызов
    
    try: 
        cat_api_url = 'https://api.thecatapi.com/v1/images/search' #url запроса к апи сайта с картинками
        response = requests.get(cat_api_url, timeout=5).json() # гет запрос по url, парсит Json ответ в словарь
        cat_url = response[0]['url'] #сайт изначально выдает не сразу картинку а json ответ со словарем, мы обращаемся к нему по ключу url, вытаскивая картинку

        fallback.update_cat_cache(cat_url)  # Обновляем кэш
        
        await message.answer_photo(
            cat_url, 
            caption=translator.get('cat_response', lang)  # Локализованная подпись
        ) 
    
    except Exception as e: 
        logger.log_error(f'Ошибка API котов: {str(e)}', user_id=user.id)
        # Используем кэшированную картинку
        cached_cat = fallback.get_cat_fallback()
        await message.answer_photo(
            cached_cat,
            caption=translator.get('cat_fallback', lang)  # Локализованный фолбек
        )
    

@router.message(F.text.lower() == 'получить погоду')
async def send_weather_menu(message: Message) -> None:  #обработчик функции получить погоду
    if not message.from_user: # проверяем юзера
        return 
    
    user = message.from_user
    lang = get_user_language(user.id)
    logger.log_message(user.id, translator.get('weather_command_log', lang))
    
    from keyboards.inline import weather_keyboard
    await message.answer(
        translator.get('weather_menu', lang),  # Локализованный текст
        reply_markup=weather_keyboard()
    )


@router.message(F.voice)
async def handle_voice(message: Message) -> None:
    
    if not message.voice or not message.from_user or not message.bot: #проверяем существуют ли voice, user и bot 
        return
    
    user = message.from_user
    lang = get_user_language(user.id)
    logger.log_message(user.id, translator.get('voice_command_log', lang))

    os.makedirs("temp", exist_ok=True) #делаем если нет директорию temp
    voice_path = f"temp/voice_{user.id}.ogg" # делаем путь к кешу гс 
    
    try:
        voice_file = await message.bot.get_file(message.voice.file_id) # получаем файл из тг
        if voice_file.file_path is None:
            await message.reply(translator.get('voice_file_error', lang))
            return

        await message.bot.download_file(voice_file.file_path, voice_path) # загружаем файл (откуда/куда)
        text = speech_to_text(voice_path)
        if text:
            await message.answer(
                translator.get('voice_response', lang, text=text)  # Локализованный ответ
            )
        else:
            await message.answer(
                translator.get('voice_fallback', lang)  # Локализованный фолбек
            )
            
    except Exception as e:
        logger.log_error(f'Ошибка распознавания голоса: {str(e)}', user_id=user.id)
        await message.answer(translator.get('voice_fallback', lang))
    finally:
        if os.path.exists(voice_path):
            os.remove(voice_path) #в конце удаляем временные файлы
            
    
@router.message(F.location)
async def handle_location(message: Message) -> None:
    if not message.from_user or not message.location:
        return
    
    user = message.from_user
    lang = get_user_language(user.id)
    logger.log_message(user.id, translator.get('location_command_log', lang))
    
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
            address = response_data.get(
                "display_name", 
                translator.get('address_not_found', lang)  # Локализованный фолбек
            )
            
        except requests.exceptions.RequestException as e: #обработка ошибок в запросах 
            logger.log_error(f"Ошибка API геолокации: {str(e)}", user_id=user.id)
            address = translator.get('api_error', lang)  # Локализованный фолбек
        except ValueError as e:
            logger.log_error(f"Ошибка обработки геоданных: {str(e)}", user_id=user.id)
            address = translator.get('data_processing_error', lang)  # Локализованный фолбек
            
        await message.answer(
            translator.get('location_response', lang, address=address)  # Локализованный ответ
        )
        
    except Exception as e:
        logger.log_error(f"Неожиданная ошибка геолокации: {str(e)}", user_id=user.id)
        await message.answer(
            translator.get('location_error', lang)  # Локализованный фолбек
        )
        