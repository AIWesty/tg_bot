from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram import F
from database.crud import get_user_language
from utils.logger import logger
from utils.config import load_config
from utils.fallbacks import fallback
import requests
from utils.i18n import translator  # LOCALIZATION: добавлен импорт транслятора

router = Router() 

@router.callback_query(F.data.startswith('city_')) #делаем из функции обработчик callback запроса от тг
async def send_weather(callback: CallbackQuery) -> None:
    if not callback.data or not callback.message: 
        return
    
    try:
        lang = get_user_language(callback.from_user.id) if callback.from_user else 'ru'  # LOCALIZATION: получаем язык пользователя
        
        city = callback.data.split('_')[1] #из пришедших данных выбираем город(пример: city_Moscow)
        
        config = load_config() # загружаем конфиг
        
        api_key = config.weather.api_key # берем апи ключ с конфига
        
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang={lang}'  # LOCALIZATION: язык запроса к API
        print(f"Request URL: {url}")
        
        response = requests.get(url, timeout=5).json() #запрос к апи погоды с таймаутом
            
        if response.get('cod') != 200:  # проверяем код запроса
            error_msg = response.get('message', translator.get('unknown_error', lang=lang))
            print(f"API error: {error_msg}")
            await callback.message.answer(
                translator.get(
                    'weather_fetch_error',
                    lang=lang,
                    error=error_msg,
                    default=f"Не удалось получить погоду 😕\nОшибка: {error_msg}"
                )
            )
            return

        # Формируем данные о погоде
        weather_data = {
            'temp': response['main']['temp'],
            'wind': response['wind']['speed'],
            'clouds': response['clouds']['all'],
            'description': response['weather'][0]['description'] if response.get('weather') else ''
        }
        
        # Обновляем кэш при успешном запросе
        fallback.update_weather_cache(
            city=city,
            temperature=f"{weather_data['temp']}°C",
            wind=f"{weather_data['wind']} {translator.get('wind_unit', lang=lang, default='м/с')}",
            clouds=f"{weather_data['clouds']}%"
        )
        # Формируем ответ (LOCALIZATION: используем переводы для структуры сообщения)
        response_text = translator.get(
            'weather_response',
            lang=lang,
            city=city,
            temp=weather_data['temp'],
            wind=weather_data['wind'],
            clouds=weather_data['clouds'],
            description=weather_data['description'],
            default=(
                f"🌤 Погода в {city}:\n"
                f"🌡 Температура: {weather_data['temp']}°C\n"
                f"💨 Ветер: {weather_data['wind']} м/с\n"
                f"☁️ Облачность: {weather_data['clouds']}%\n"
                f"📝 {weather_data['description']}"
            )
        )
        
        await callback.message.answer(response_text)
        await callback.answer()
        logger.log_message(callback.from_user.id, f'Запрошена погода для города {city}')  # LOCALIZATION: лог-сообщение оставляем
    
    except IndexError:
        await callback.message.answer(
            translator.get(
                'invalid_request_format',
                lang=lang,
                default="Некорректный формат запроса"
            )
        )
        logger.log_error("Некорректный формат callback данных", user_id=callback.from_user.id)  # LOCALIZATION: лог-ошибка оставляем
    
    except requests.exceptions.RequestException as e:
        # Пробуем получить данные из кэша
        cached_response = fallback.get_weather_fallback(city)
        if cached_response:
            await callback.message.answer(
                translator.get(
                    'cached_weather_response',
                    lang=lang,
                    response=cached_response,
                    default=f"{cached_response}\n(данные могут быть неактуальными)"
                )
            )
            logger.log_message(callback.from_user.id, f'Использованы кэшированные данные для {city}')  # LOCALIZATION: лог-сообщение оставляем
        else:
            await callback.message.answer(
                translator.get(
                    'weather_service_unavailable',
                    lang=lang,
                    default="Сервис погоды временно недоступен. Попробуйте позже."
                )
            )
            logger.log_error(f'Ошибка запроса погоды: {str(e)}', user_id=callback.from_user.id)  # LOCALIZATION: лог-ошибка оставляем
    
    except Exception as e:
        await callback.message.answer(
            translator.get(
                'unexpected_error',
                lang=lang,
                default="Произошла непредвиденная ошибка"
            )
        )
        logger.log_error(f'Ошибка в обработчике погоды: {str(e)}', user_id=callback.from_user.id)  # LOCALIZATION: лог-ошибка оставляем