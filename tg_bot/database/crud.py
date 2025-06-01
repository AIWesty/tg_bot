import csv
from pathlib import Path
from datetime import datetime


def save_user(user_id: int, username: str, first_name: str) -> None: 
    file_path = Path('data/users.csv') #путь до файла
    file_path.parent.mkdir(exist_ok=True) #проверяем есть ли родительская директория и если нет то создаем
    
    if not file_path.exists():  #проверяем есть ли файл 
        with open(file_path, 'w', newline='', encoding='utf-8') as f: # если нет создаем
            writer = csv.writer(f)
            writer.writerow(["user_id", "username", "first_name", "join_date"])#записываем в нужном формтае
            
    with open(file_path, 'r', encoding='utf-8') as f: # далее читаем существующий файл 
        reader = csv.reader(f)
        existing_users = [row[0] for row in reader] # список существующих пользователей по айди
        
    if str(user_id) not in existing_users:  # проверяем есть ли юзер в сущ пользователях
        with open(file_path, 'a', newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([user_id,username, first_name, datetime.now().strftime("%Y-%m-%d")]) 
