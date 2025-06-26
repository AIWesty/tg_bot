🤖 Telegram Bot: Multi-Functional Assistant

📌 Основная информация
- **Название бота**: Vaxei_Bot
- **Тема**: Многофункциональный бот-ассистент с поддержкой погоды, голосовых команд, геолокации и некоторыми другими фишками
- **Автор**: Виктор/lilchacha | [GitHub профиль](https://github.com/tsukishido)
- **Username бота**: `@Vaxei_bot` | [Ссылка на бота] (https://t.me/Vaxei_bot)

🔧 Как устроен бот
### Основные технологии
- **Python 3.10+** - современная версия языка
- **Aiogram** - библиотека для создания Telegram ботов
- **Asyncio** - для плавной работы с несколькими пользователями сразу

🌟 Функционал
- **Получение погоды** по выбранному городу (OpenWeatherMap API)
- **Случайные котики** (TheCatAPI)
- **Обработка голосовых сообщений** (Vosk)
- **Определение адреса** по геолокации (Nominatim)
- **Мультиязычная поддержка** (русский/английский)
- **Статистика пользователей**
- **Интерактивные клавиатуры**

📋 Список команд
| Команда       | Описание                          | Пример           |
|---------------|-----------------------------------|------------------|
| `/start`      | Запуск бота                       | `/start`         |
| `/help`       | Справка по командам               | `/help`          |
| `/language`   | Смена языка (ru/en)               | `/language`      |
| `/me`         | Ваша статистика                   | `/me`            |
| `/roll`       | Случайное число                   | `/roll 1-100`    |

**Быстрые действия через кнопки**:
- "🌤️ Получить погоду" 
- "🐱 Кота!"
- "📍 Отправить локацию"

🗃️ Структура базы данных реализована записью в файл csv в виде:
user_id,username,first_name,join_date,language,city


## 📦 Зависимости
Основные сторонние библиотеки:
aiogram==3.0.0b7
python-dotenv==1.0.0
requests==2.31.0
vosk==0.3.45
APScheduler==3.10.0
pydantic==1.10.7
python-decouple==3.8
fpdf2==2.7.4
APScheduler


🌐 Используемые API
Сервис	        Описание	            Ключ в config.yaml	    Документация
OpenWeatherMap	Данные о погоде	        weather.api_key	        API Docs
TheCatAPI	    Случайные изображения   котиков	Не требуется	API Docs
Nominatim	    Геокодирование локаций	Не требуется	        API Docs

📚 Использованные материалы
Ресурс	                Описание	                Ссылка
Aiogram Documentation   Основная документация	    aiogram.dev
Vosk API	            Распознавание речи	        alphacephei.com
Python Decouple	        Управление конфигурацией    pypi.org
Requests Library	    HTTP-запросы	            docs.python-requests.org


🚀 Установка и запуск
1.Клонировать репозиторий:

git clone https://github.com/yourusername/yourbot.git
cd yourbot

2.Установить зависимости:

pip install -r requirements.txt


3.создать файлы конфигурации:

cp config.example.yaml config.yaml
cp .env.example .env


4.Заполнить конфиги:

yaml
# config.yaml
bot:
  token: "YOUR_BOT_TOKEN"
  admins: [123456789]
weather:
  api_key: "OPENWEATHER_API_KEY"


5.Запустить бота:

python run.py


📊 Статистика и логи
Бот автоматически сохраняет:

Логи сообщений в data/logs/

Статистику команд в SQLite

PDF-отчеты в data/reports/
