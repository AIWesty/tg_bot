from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram import F
from utils.logger import log_errors, log_message
from utils.config import load_config
import requests

router = Router() 

@router.callback_query(F.data.startswith('city_')) #делаем из функции обработчик callback  запроса от тг
async def send_weather(callback: CallbackQuery) -> None:
    if not callback.data or not callback.message: 
        return
    
    try:
    
        city = callback.data.split('_')[1] #из пришедших данных выбираем город(пример: city_Moscow)
        
        config = load_config() # загружаем конфиг
        
        api_key = config.weather.api_key # берем апи ключ с конфига
        
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'
        print(f"Request URL: {url}")
        
        response = requests.get(url, timeout=5).json() #запрос к апи погоды с таймаутом
            
        
        if response.get('cod') != 200:  # проверяем код запроса
            error_msg = response.get('message', 'Unknown error')
            print(f"API error: {error_msg}")
            await callback.message.answer(f"Не удалось получить погоду 😕\nОшибка: {error_msg}")
            return

        #формируем ответ
        weather_data = (
                f"🌤 Погода в {city}:\n"
                f"🌡 Температура: {response['main']['temp']}°C\n"
                f"💨 Ветер: {response['wind']['speed']} м/с\n"
                f"☁️ Облачность: {response['clouds']['all']}%"
            )  
            
        await callback.message.answer(weather_data) #отвечаем
        await callback.answer() #закрываем полоску загрузки
        
        log_message(callback.from_user.id, f'Запрошена погода для города {city}')
    
    except IndexError:
        await callback.message.answer("Некорректный формат запроса")
    except requests.exceptions.RequestException as e:
        await callback.message.answer("Ошибка подключения к сервису погоды")
        log_errors(f'Ошибка запроса погоды: {str(e)}')
    except Exception as e:
        await callback.message.answer("Произошла непредвиденная ошибка")
        log_errors(f'Ошибка в обработчике погоды: {str(e)}')