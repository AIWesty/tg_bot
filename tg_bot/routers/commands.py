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
        await message.answer(translator.get('unknown_user_error', default='Не удалось определить пользователя'))
        return
    
    user = message.from_user  # сохраняем объект пользователя в переменную
    lang = get_user_language(user.id)  # получаем язык пользователя из БД
    
    # Сохраняем пользователя в "базу" (если еще не сохранен)
    save_user(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name or translator.get('unknown_user', lang=lang),
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
        # Проверка пользователя
        if message.from_user is None:
            logger.log_error("Empty from_user in help command")
            return

        user_id = message.from_user.id
        lang = get_user_language(user_id) or 'en'
        
        # Логирование
        logger.log_message(user_id, f"Called /help command (lang: {lang})")
        user_stats_logger.log_command(user_id, '/help')

        # Функция для удобного получения перевода
        def get_translation(key: str) -> str:
            """Безопасное получение перевода с fallback'ами"""
            result = translator.get(key, lang=lang)
            return str(result) if result is not None else f"[{key}]"

        # Получение данных
        header = get_translation("help_header")
        commands_title = get_translation("help_commands_title")
        examples_title = get_translation("help_examples_title")
        footer = get_translation("help_footer")

        # Обработка команд
        raw_commands = translator.get("help_commands", lang=lang)
        if isinstance(raw_commands, dict):
            commands = "\n".join(
                f"• /{cmd} - {desc}"
                for cmd, desc in sorted(raw_commands.items())
            )
        else:
            commands = str(raw_commands) if raw_commands is not None else ""

        # Обработка примеров
        raw_examples = translator.get("help_examples", lang=lang)
        if isinstance(raw_examples, dict):
            examples = "\n".join(
                f"🔹 {example}"
                for example in raw_examples.values()
            )
        elif isinstance(raw_examples, list):
            examples = "\n".join(f"🔹 {ex}" for ex in raw_examples)
        else:
            examples = str(raw_examples) if raw_examples is not None else ""

        # Формирование сообщения
        message_parts = [
            f"📝 {header}",
            "",
            f"<b>{commands_title}</b>",
            commands,
            "",
            f"<b>{examples_title}</b>",
            examples,
            "",
            footer
        ]

        # Отправка сообщения
        await message.answer(
            "\n".join(message_parts),
            parse_mode="HTML",
            reply_markup=get_action_keyboard(lang)
        )

    except Exception as e:
        logger.log_error(f"Help command error: {str(e)}")
        error_msg = translator.get(
            "error_help",
            lang=get_user_language(message.from_user.id) if message.from_user else 'en',
            default="⚠️ Help unavailable now"
        )
        await message.answer(str(error_msg), parse_mode="HTML")

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
            input_field_placeholder=translator.get(
                "choose_command_placeholder", 
                lang=lang,
                default="Выберите команду..."
            )
        )
    )
    

@router.message(Command('about'))
async def cmd_about(message: Message) -> None:  # обработчик команды about
    import json
    from pathlib import Path
    
    try:
        with open('config/about.json', 'r', encoding='utf-8') as f: #данные берем из config/about
            about_data = json.load(f) #подргужаем данные 
            
            lang = get_user_language(message.from_user.id) if message.from_user else 'en'
            
            about_txt = (
                f"🤖 {about_data['name']}\n"
                f"📝 {translator.get('about_description', lang=lang, default=about_data.get('description', ''))}\n"
                f"🛠️ {translator.get('version', lang=lang)}: {about_data['version']}\n"
                f"👨‍💻 {translator.get('author', lang=lang)}: {about_data['author']}"
            )
            
            if message.from_user is None: # проверяем наличие from_user
                await message.answer(about_txt)
                return
            
            user = message.from_user
            
            logger.log_message(user.id, f'Вызвал команду (/about)')  
            user_stats_logger.log_command(user.id, '/about')
            
            await message.answer(about_txt)
            
    except FileNotFoundError:
        await message.answer(translator.get(
            'about_file_not_found', 
            lang=get_user_language(message.from_user.id) if message.from_user else 'en',
            default="Файл с информацией о боте не найден"
        ))
    except json.JSONDecodeError as e:
        error_msg = f"Ошибка в формате файла about.json: {str(e)}" 
        logger.log_error(error_msg)
        await message.answer(translator.get(
            'about_load_error',
            lang=get_user_language(message.from_user.id) if message.from_user else 'en',
            default="Ошибка загрузки информации о боте"
        ))
    except KeyError as e:
        error_msg = f"Отсутствует обязательное поле в about.json: {str(e)}"  
        logger.log_error(error_msg)
        await message.answer(translator.get(
            'about_incomplete_info',
            lang=get_user_language(message.from_user.id) if message.from_user else 'en',
            default="Неполная информация о боте"
        ))
    except Exception as e:
        error_msg = f"Неожиданная ошибка: {str(e)}"  
        logger.log_error(error_msg)
        await message.answer(translator.get(
            'about_unknown_error',
            lang=get_user_language(message.from_user.id) if message.from_user else 'en',
            default="Произошла ошибка при получении информации"
        ))
    
    
@router.message(Command("roll"))
async def cmd_roll(message: Message):
    # Обработка отсутствия текста
    if message.text is None:
        error_msg = translator.get(
            'roll_processing_error',
            lang=get_user_language(message.from_user.id) if message.from_user else 'en'
        ) or "❌ Failed to process command."
        await message.answer(error_msg)
        return

    # Проверка пользователя
    if message.from_user is None:
        return
    
    # Получаем язык с дефолтным значением 'en'
    user = message.from_user
    lang = get_user_language(user.id) or 'en'  # Явное указание дефолтного языка
    
    # Debug: проверяем какой язык определился

    args = message.text.split()

    try:
        # Обработка диапазона
        if len(args) > 1:
            start, end = map(int, args[1].split("-"))
            num = random.randint(start, end)
            response = translator.get('roll_result_with_args', lang=lang) or f"🎲 Rolled: {num}"
        # Стандартный случай
        else:
            num = random.randint(1, 6)
            response = translator.get('roll_default', lang=lang) or f"🎲 Rolled: {num}"

        # Форматирование ответа (если содержит {num})
        if '{num}' in response:
            response = response.format(num=num)
            
        await message.answer(response)

        # Логирование
        logger.log_message(user.id, f'Used /roll command')
        user_stats_logger.log_command(user.id, '/roll')

    except (ValueError, IndexError):
        error_msg = translator.get('roll_usage_error', lang=lang) or "❌ Usage: /roll start-end (e.g. /roll 1-100)"
        await message.answer(error_msg)
    
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
        confirmation = translator.get(
            "language_changed", 
            lang=lang, 
            language=translator.locales[lang].get("language_name", lang)
        )
        
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
            await callback.answer(translator.get(
                "message_update_error",
                lang=lang,
                default="Не удалось обновить сообщение"
            ))
            
    except IndexError:
        await callback.answer(translator.get(
            "request_format_error",
            lang=get_user_language(callback.from_user.id) if callback.from_user else 'en',
            default="⚠️ Ошибка формата запроса"
        ))
    except ValueError:
        supported_langs = ", ".join(translator.locales.keys())
        await callback.answer(translator.get(
            "unsupported_language_error",
            lang=get_user_language(callback.from_user.id) if callback.from_user else 'en',
            supported_langs=supported_langs,
            default=f"⚠️ Поддерживаемые языки: {supported_langs}"
        ))
    except Exception as e:
        await callback.answer(translator.get(
            "language_change_error",
            lang=get_user_language(callback.from_user.id) if callback.from_user else 'en',
            default="⚠️ Ошибка смены языка"
        ))
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
        logger.log_error(f"/me error: {e}", user.id)  # лог-сообщение, оставляем как есть
        error_msg = translator.get(
            "error_stats", 
            lang=lang, 
            default="⚠️ Не удалось получить статистику"
        )
        await message.answer(error_msg)