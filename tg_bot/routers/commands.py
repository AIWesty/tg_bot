from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from keyboards.reply import get_action_keyboard, get_main_keyboard
from keyboards.inline import language_keyboard
from utils.user_stats import format_stats_message, get_user_stats
from utils.logger import logger, user_stats_logger
from utils.i18n import translator
from database.crud import get_user_language, save_user
import random
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database.crud import set_user_language
from aiogram.types import CallbackQuery

router = Router() # определяем роутер(обьект класса роутер)

@router.message(Command('start'))  # обработчик команды старт, по сути "возвращает" интерфейсную клавиатуру для взаимодействия и приветствие
async def cmd_start(message: Message) -> None:
    """
    Обработчик команды /start
    - Регистрирует пользователя
    - Логирует запуск бота
    - Отправляет приветственное сообщение
    - Показывает основную клавиатуру
    """
    
    if message.from_user is None:  # проверка наличия пользователя (защита от некорректных сообщений)
        await message.answer('Не удалось определить пользователя')
        return
    
    user = message.from_user  # сохраняем объект пользователя в переменную
    lang = get_user_language(user.id)  # получаем язык пользователя из БД
    
    # Сохраняем пользователя в "базу" (если еще не сохранен)
    save_user(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name or "Unknown",
        language=lang  # сохраняем текущий язык
    )
    
    logger.log_message(user.id, translator.get('start_command_log', lang=lang))  # логируем обращение пользователя
    user_stats_logger.log_command(user.id, '/start')
    # Формируем приветственное сообщение с учетом локализации
    welcome_text = translator.get(
        'start_message',
        lang=lang,
        name=user.first_name or translator.get('unknown_user', lang=lang)
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(lang)  # подключаем интерактивную клавиатуру (кнопки)
    )
    

@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Универсальный обработчик команды /help для всех языков"""
    try:
        if not message.from_user:
            logger.log_error("Empty from_user in help command")
            return

        user_id = message.from_user.id
        lang = get_user_language(user_id)
        logger.log_message(user_id, f"Called /help command (lang: {lang})")
        user_stats_logger.log_command(user_id, '/help')
        # Получаем локализованные данные
        help_data = {
            'title': translator.get("help_title", lang=lang),
            'commands': translator.get("help_commands", lang=lang),
            'footer': translator.get("help_footer", lang=lang),
            'examples': translator.get("help_examples", lang=lang)
        }

        # Формируем список команд
        commands_list = ""
        if isinstance(help_data['commands'], dict):
            commands_list = "\n".join(
                f"• /{cmd} - {desc}" 
                for cmd, desc in sorted(help_data['commands'].items())
            )
        else:
            commands_list = str(help_data['commands'])

        # Формируем примеры использования
        examples_text = ""
        if isinstance(help_data['examples'], dict):
            examples_text = "\n".join(
                f"🔹 {example}" 
                for example in help_data['examples'].values()
            )

        # Собираем итоговое сообщение
        help_message = (
            f"<b>{help_data['title']}</b>\n\n"
            f"<u>{translator.get('available_commands', lang=lang)}</u>:\n"
            f"{commands_list}\n\n"
            f"<u>{translator.get('usage_examples', lang=lang)}</u>:\n"
            f"{examples_text}\n\n"
            f"{help_data['footer']}"
        )

        await message.answer(
            help_message,
            parse_mode="HTML",
            reply_markup=get_action_keyboard(lang)  # Добавляем клавиатуру действий
        )

    except Exception as e:
        logger.log_error(f"Help command error: {e}")
        error_msg = translator.get("error_help", lang=lang, default="⚠️ Help unavailable now")
        await message.answer(error_msg, parse_mode="HTML")

@router.message(F.text == '/')
async def show_commands_hint(message: Message):
    """Показывает подсказку по командам при вводе /"""
    if message.from_user is None:
        return
    lang = get_user_language(message.from_user.id)
    
    # Получаем только названия команд без описаний
    commands_dict = translator.get("help_commands", lang=lang)

    # Проверяем тип и получаем ключи
    if isinstance(commands_dict, dict):
        commands = list(commands_dict.keys())
    else:
        commands = ["start", "help"]  # Значение по умолчанию
    
    # Создаем клавиатуру с командами
    builder = ReplyKeyboardBuilder()
    for cmd in commands:
        builder.button(text=f"/{cmd}")
    builder.adjust(3)  # 3 кнопки в ряду
    
    await message.answer(
        translator.get("type_slash", lang=lang),
        reply_markup=builder.as_markup(
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="Выберите команду..."
        )
    )
    

@router.message(Command('about'))
async def cmd_about(message: Message) -> None:  # обработчик команды about
    import json
    from pathlib import Path
    
    try:
        with open('config/about.json', 'r', encoding='utf-8') as f: #данные берем из config/about
            about_data = json.load(f) #подргужаем данные 
            
            about_txt = (
                f"🤖 {about_data['name']}\n"
                f"📝 {about_data['description']}\n"
                f"🛠️ Версия: {about_data['version']}\n"
                f"👨‍💻 Автор: {about_data['author']}"
            )
            
            if message.from_user is None: # проверяем наличие from_user
                await message.answer(about_txt)
                return
            
            user = message.from_user
            
            logger.log_message(user.id, f'Вызвал команду (/about)')
            user_stats_logger.log_command(user.id, '/about')
            
            await message.answer(about_txt)
            
    except FileNotFoundError:
        await message.answer("Файл с информацией о боте не найден")
    except json.JSONDecodeError as e:
        error_msg = f"Ошибка в формате файла about.json: {str(e)}"
        logger.log_error(error_msg)
        await message.answer("Ошибка загрузки информации о боте")
    except KeyError as e:
        error_msg = f"Отсутствует обязательное поле в about.json: {str(e)}"
        logger.log_error(error_msg)
        await message.answer("Неполная информация о боте")
    except Exception as e:
        error_msg = f"Неожиданная ошибка: {str(e)}"
        logger.log_error(error_msg)
        await message.answer("Произошла ошибка при получении информации")
    
    
@router.message(Command("roll"))
async def cmd_roll(message: Message): # обработка команды ролл
    if message.text is None:  # проверяем  есть ли текст в сообщении
        await message.answer("❌ Не удалось обработать команду.")
        return

    if message.from_user is None: 
        return
    
    user = message.from_user

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
    
    logger.log_message(user.id, f'Вызвал команду (/about)')
    user_stats_logger.log_command(user.id, '/roll')
    
    
@router.message(Command("language"))
async def cmd_language(message: Message):
    """Обработчик команды /language - показывает клавиатуру выбора языка"""
    if message.from_user is None: 
        return
    user = message.from_user
    lang = get_user_language(message.from_user.id)
    await message.answer(
        translator.get("choose_language", lang=lang),
        reply_markup=language_keyboard()
    )
    logger.log_message(user.id, 'Вызвал команду /language')

@router.callback_query(F.data.startswith("set_lang_"))
async def set_language_callback(callback: CallbackQuery):
    """Обработчик выбора языка из inline-клавиатуры"""
    if not callback.data or not callback.message or not callback.bot:
        return
    
    
    try:
        # Парсим выбранный язык из callback (формат: set_lang_ru)
        lang = callback.data.split('_')[2]
        user_id = callback.from_user.id
        # Проверяем поддержку языка
        if lang not in translator.locales:
            raise ValueError("Unsupported language")
        
        # Устанавливаем язык и получаем локализованное подтверждение
        set_user_language(user_id, lang)
        confirmation = translator.get("language_changed", lang=lang, language=translator.locales[lang].get("language_name", lang))
        
        # Отвечаем пользователю
        await callback.answer(confirmation)
        
        # Обновляем сообщение с кнопками
        try:
            if isinstance(callback.message, Message):
            # Редактируем обычное сообщение
                await callback.message.edit_text(
                translator.get("choose_language", lang=lang),
                reply_markup=language_keyboard()
            )
            else:
                # Для инлайн-сообщений используем другой подход
                logger.log_message(user_id, 'Вызывал команду /set_language_callback')
                await callback.bot.edit_message_text(
                    chat_id=callback.from_user.id,
                    message_id=callback.message.message_id if callback.message else None,
                    inline_message_id=callback.inline_message_id,
                    text=translator.get("choose_language", lang=lang),
                    reply_markup=language_keyboard()
                )
        except TelegramAPIError as e:
            await callback.answer("Не удалось обновить сообщение")
            
    except IndexError:
        await callback.answer("⚠️ Ошибка формата запроса")
    except ValueError:
        supported_langs = ", ".join(translator.locales.keys())
        await callback.answer(f"⚠️ Поддерживаемые языки: {supported_langs}")
    except Exception as e:
        await callback.answer("⚠️ Ошибка смены языка")
        logger.log_error(f"Language change error: {str(e)}", user_id=callback.from_user.id)
        

@router.message(Command("me"))
async def cmd_me(message: Message) -> None:
    """Обработчик команды /me - показывает статистику пользователя"""
    try:
        if not message.from_user:
            logger.log_error("message.from_user пустой")
            return

        user = message.from_user
        lang = get_user_language(user.id)
        logger.log_message(user.id, "вызвана команда /me")
        
        # Логируем команду и обновляем статистику
        user_data = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        user_stats_logger.log_command(user.id, "/me", user_data)
        
        # Получаем статистику
        stats = user_stats_logger.get_user_stats(user.id)
        
        # Форматируем сообщение
        response = format_stats_message(stats, lang)
        
        await message.answer(response, parse_mode="HTML")

    except Exception as e:
        logger.log_error(f"/me error: {e}", user.id)
        error_msg = translator.get("error_stats", lang=lang, default="⚠️ Не удалось получить статистику")
        await message.answer(error_msg)

