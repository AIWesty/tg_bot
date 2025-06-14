from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram import F
from utils.logger import logger
from utils.config import load_config
from utils.fallbacks import fallback
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

        # Формируем данные о погоде
        weather_data = {
            'temp': response['main']['temp'],
            'wind': response['wind']['speed'],
            'clouds': response['clouds']['all']
        }
        
        # Обновляем кэш при успешном запросе
        fallback.update_weather_cache(
            city=city,
            temperature=f"{weather_data['temp']}°C",
            wind=f"{weather_data['wind']} м/с",
            clouds=f"{weather_data['clouds']}%"
        )
        
        # Формируем ответ
        response_text = (
            f"🌤 Погода в {city}:\n"
            f"🌡 Температура: {weather_data['temp']}°C\n"
            f"💨 Ветер: {weather_data['wind']} м/с\n"
            f"☁️ Облачность: {weather_data['clouds']}%"
        )
        
        await callback.message.answer(response_text)
        await callback.answer()
        logger.log_message(callback.from_user.id, f'Запрошена погода для города {city}')
    
    except IndexError:
        await callback.message.answer("Некорректный формат запроса")
        logger.log_error("Некорректный формат callback данных", user_id=callback.from_user.id)
    
    except requests.exceptions.RequestException as e:
        # Пробуем получить данные из кэша
        cached_response = fallback.get_weather_fallback(city)
        if cached_response:
            await callback.message.answer(cached_response + "\n(данные могут быть неактуальными)")
            logger.log_message(callback.from_user.id, f'Использованы кэшированные данные для {city}')
        else:
            await callback.message.answer("Сервис погоды временно недоступен. Попробуйте позже.")
            logger.log_error(f'Ошибка запроса погоды: {str(e)}', user_id=callback.from_user.id)
    
    except Exception as e:
        await callback.message.answer("Произошла непредвиденная ошибка")
        logger.log_error(f'Ошибка в обработчике погоды: {str(e)}', user_id=callback.from_user.id)