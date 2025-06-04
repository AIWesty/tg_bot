import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # Хранилище состояний (FSM)
from utils.config import load_config  # Загрузка конфигов
from routers import commands, messages, weather # подключение роутеров
# from utils.scheduler import setup_scheduler  # Планировщик задач



#основная функция нашего бота
async def main() -> None: 
    
    config = load_config() #инициализация конфига

    bot = Bot(token=config.bot.token) #инициализация бота
    dp = Dispatcher(storage=MemoryStorage()) # инициализация деспетчера с хранилищем fsm
    
    dp.include_router(commands.router) # подлючаем роутер с обработкой команд
    dp.include_router(messages.router) 
    # dp.include_router(weather.router)

    
    await dp.start_polling(bot)#асинхронный опрос бота(событийный цикл)
    
    
if __name__ == '__main__': 
    asyncio.run(main()) #запускаем основную функцию и событийный цикл в ней 