from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from keyboards.reply import main_keyboard
from utils.logger import log_message
from database.crud import save_user
import random

router = Router() # определяем роутер(обьект класса роутер)

@router.message(Command('start')) # обработчик комманды старт, по сути "возвращает" интер клавиатуру для взаимодействия и приветствие
async def cmd_start(message: Message) -> None: # принимает сообщение пользователя
    
    if message.from_user is None:  #проверка наличия пользователя
        await message.answer('Не удалось определить пользователя')
        return
    
    user = message.from_user  # сохраняем объект пользователя в user
    
    # сохраняем в "базу" пользователя 
    save_user(user.id, user.username or "", user.first_name or "Unknown")
    
    log_message(user.id, f'Запустил бота (/start)')  # логируем обращение пользователя
    
    await message.answer(
        f'Привет, {user.first_name}! Я бот. Чем могу тебе помочь?',
        reply_markup = main_keyboard(),
    ) # формируем ответ пользователю и подключаем интерактивную клавиатуру (кнопки)
    
    

@router.message(Command('help'))
async def cmd_help(message: Message) -> None:  # обработчик команды help
    help_text = """
    📌 Доступные команды:
    /start - Начать работу
    /help - Помощь
    /about - О боте
    /roll - Случайное число
    """
    
    if message.from_user is None:  # проверяем есть ли from_user
        await message.answer(help_text, reply_markup=ReplyKeyboardRemove())
        return
    
    user = message.from_user
    log_message(user.id, 'Вызвал команду (/help)')  
    
    await message.answer(help_text, reply_markup=ReplyKeyboardRemove()) #отправка ответа и закрытие окна интерактивной клавиатуры
    

@router.message(Command('about'))
async def cmd_about(message: Message) -> None:  # обработчик команды about
    import json
    
    with open('config/about.json', 'r', encoding='utf-8') as f: #данные берем из config/about
        about_data = json.load(f) #подргужаем данные 
        
        
        about_txt = (
            f"🤖 <b>{about_data['name']}</b>\n"
            f"📝 {about_data['description']}\n"
            f"🛠️ Версия: {about_data['version']}\n"
            f"👨‍💻 Автор: {about_data['author']}"
        )
        
        if message.from_user is None: # проверяем наличие from_user
            await message.answer(about_txt)
            return
        
        user = message.from_user
        
        log_message(user.id, f'Вызвал команду (/about)')
        
        await message.answer(about_txt)
    
    
@router.message(Command("roll"))
async def cmd_roll(message: Message): # обработка команды ролл
    if message.text is None:  # проверяем  есть ли текст в сообщении
        await message.answer("❌ Не удалось обработать команду.")
        return

    args = message.text.split()  # разбиваем текст на части
    
    if len(args) > 1:  # если есть аргумент(указано ли что то помимо ролл) (например /roll 1-100)
        try:
            start, end = map(int, args[1].split("-"))  # разделяем диапазон
            num = random.randint(start, end)
            await message.answer(f"🎲 Выпало: {num}")
        except (ValueError, IndexError):  # ловим конкретные исключения
            await message.answer("❌ Используйте: /roll 1-100 (числа могут быть произвольными)")
    else:
        await message.answer(f"🎲 Выпало: {random.randint(1, 6)}")