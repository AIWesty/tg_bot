import csv
from pathlib import Path
from datetime import datetime


def save_user(
    user_id: int, 
    username: str, 
    first_name: str,
    language: str = 'ru'  # Добавляем параметр language со значением по умолчанию
) -> None: 
    file_path = Path('data/users.csv') # путь до файла
    file_path.parent.mkdir(exist_ok=True) # проверяем есть ли родительская директория и если нет то создаем
    
    if not file_path.exists():  # проверяем есть ли файл 
        with open(file_path, 'w', newline='', encoding='utf-8') as f: # если нет создаем
            writer = csv.writer(f)
            # записываем в нужном формате
            writer.writerow(["user_id", "username", "first_name", "join_date", "language", "city"])
            
    with open(file_path, 'r', encoding='utf-8') as f: # далее читаем существующий файл 
        reader = csv.reader(f)
        existing_users = [row[0] for row in reader] # список существующих пользователей по айди
        
    if str(user_id) not in existing_users:  # проверяем есть ли юзер в сущ пользователях
        with open(file_path, 'a', newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # используем переданный язык или значение по умолчанию
            writer.writerow([
                user_id, 
                username, 
                first_name, 
                datetime.now().strftime("%Y-%m-%d"), 
                language,  # Используем параметр вместо жестко заданного 'ru'
                ''
            ])

    
    
def get_user_language(user_id: int) -> str:
    """Возвращает язык пользователя ('ru' или 'en'), по умолчанию 'ru'"""
    # Для CSV-версии
    if not Path("data/users.csv").exists():
        return 'ru'
    
    with open("data/users.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # безопасная проверка наличия user_id и language
            if row.get('user_id') == str(user_id):
                return row.get('language', 'ru')  # Возвращаем язык или 'ru' по умолчанию
    return 'ru'

def set_user_language(user_id: int, language: str):
    """Устанавливает язык пользователя ('ru' или 'en')"""
    if language not in ('ru', 'en'):
        raise ValueError("Поддерживаются только 'ru' и 'en'")
    
    # Обновляем CSV (аналогично set_user_city)
    users = []
    file_exists = Path("data/users.csv").exists()
    
    if file_exists:
        with open("data/users.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            users = list(reader)
    
    # Обновляем запись
    updated = False
    for user in users:
        # безопасный доступ к user_id
        if user.get('user_id') == str(user_id):
            user['language'] = language
            updated = True
            break
    
    # Если пользователь не найден, добавляем новую запись с минимальными данными
    if not updated:
        users.append({
            'user_id': str(user_id),
            'language': language,
            'username': '',
            'first_name': '',
            'join_date': datetime.now().strftime("%Y-%m-%d"),
            'city': ''
        })
    
    # Перезаписываем файл
    with open("data/users.csv", 'w', encoding='utf-8', newline='') as f:
        # используем все необходимые колонки
        writer = csv.DictWriter(f, fieldnames=['user_id', 'username', 'first_name', 'join_date', 'language', 'city'])
        writer.writeheader()
        writer.writerows(users)