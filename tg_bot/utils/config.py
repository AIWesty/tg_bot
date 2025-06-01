import yaml
from pydantic import BaseModel #базовый класс для валидации, при возвращении обьекта автоматически отвалидирует данные 

class BotConfig(BaseModel):
    token: str
    admins: int  
    log_path: str
    users_db: str

class WeatherConfig(BaseModel):
    cities: list[str]
    api_key: str

class Config(BaseModel):
    bot: BotConfig
    weather: WeatherConfig



def load_config() -> Config: 
    from dotenv import load_dotenv # импортируем функцию обращения к .env
    import os 
    load_dotenv()#Загружаем токены из .env
    
    with open('config/config.yaml', 'r', encoding='utf-8') as f: 
        config_data = yaml.safe_load(f) # открыли ямл файл с конфигом, прочитали информацию (защищённо)
    
    config_data["bot"]["admins"] = os.getenv("ADMIN_IDS")
    config_data["bot"]["token"] = os.getenv("BOT_TOKEN")
    config_data["weather"]["api_key"] = os.getenv("WEATHER_API_KEY") #подставили в конфиг дату значения токенов 
    
    return Config(**config_data)#вернули обьект класса с распакованным словарем в аргументы класса

