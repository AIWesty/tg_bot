from pathlib import Path
from datetime import datetime 

ERR_DIR = Path('data/reports')
ERR_DIR.mkdir(parents=True, exist_ok=True) # путь до reports с созданием родителя если нет 
LOG_DIR = Path('data/logs')
LOG_DIR.mkdir(parents=True, exist_ok=True) # путь до logs с созданием родителя если нет

def log_message(user_id: int, text: str) -> None: 
    '''Логирует действие пользователя'''
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #текущая дата + время в формате год месяц день / часы минуты сек
    log_entry = f'[{timestamp}] user_id={user_id} | text={text}\n' # строка лога 
    
    with open(LOG_DIR / 'all_messages.log', 'a', encoding='utf-8') as f:  # запись в общий файл логов
        f.write(log_entry) 
        
    
    user_log_file = LOG_DIR / f'user_{user_id}.log' # Запись в отдельный файл под пользователя
    with open(user_log_file, 'a', encoding='utf-8') as f: 
        f.write(log_entry)    
    
    
def log_errors(error) -> None:  
    '''Логируем ошибки'''
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #логирование ошибок в reports
    with open(ERR_DIR, 'a', encoding='utf-8') as f: 
        f.write(f'[{timestamp}] Error: {error}')