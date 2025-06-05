import csv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from utils.logger import log_errors, log_message
from utils.report import generate_daily_report
from typing import List

async def send_morning_greeting(bot: Bot):
    
    with open('data/greeting.txt', 'r', encoding='utf-8') as f: # читаем файл с сообщением
        greeting_data = f.read()
        
    with open('data/users.csv', 'r', encoding='utf-8') as f: #читаем файл с юзерами
        reader = csv.reader(f)
        user_ids = [row[0] for row in reader] #выбрали айдишники
    
    for user_id in user_ids: 
        try: 
            await bot.send_message(user_id, greeting_data)
        except:
            pass

async def setup_scheduler(bot: Bot, admin_ids: List[int]) -> AsyncIOScheduler:
    """Настраивает и запускает планировщик задач для бота."""
    
    try:
        #Инициализация планировщика
        scheduler = AsyncIOScheduler()
        
        # наастройка часовых поясов (важно для cron-задач)
        moscow_tz = 'Europe/Moscow' 
        
        #утреннее приветствие в 8:00 по Москве
        scheduler.add_job(
            send_morning_greeting,
            "cron",
            hour=8,
            timezone=moscow_tz,  # Явное указание часового пояса
            args=(bot,),
            id="morning_greeting",  # Уникальный айдидля возможного обновления
            misfire_grace_time=60,  # Допустимое время задержки выполнения (сек)
            replace_existing=True  # Заменяет задачу, если уже существует
        )
        
        #Ежедневный отчет в 23:55 по Москве
        scheduler.add_job(
            generate_daily_report,
            "cron",
            hour=23,
            minute=55,
            timezone=moscow_tz,
            args=(bot, admin_ids),  # Передаем и бота и admin_ids
            id="daily_report",
            misfire_grace_time=300,  # Больше времени для отчетов
            replace_existing=True
        )
        
        # Запуск планировщика
        scheduler.start()
        
        #Возвращаем scheduler для возможного управления
        return scheduler
        
    except Exception as e:
        log_errors(f"Ошибка при настройке планировщика: {e}")
        raise