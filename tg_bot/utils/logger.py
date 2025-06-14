from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import csv

class ActivityLogger:
    def __init__(self):
        # Директории для хранения данных
        self.BASE_DIR = Path('data')
        self.LOGS_DIR = self.BASE_DIR / 'logs'
        self.STATS_DIR = self.BASE_DIR / 'stats'
        self.ERRORS_DIR = self.BASE_DIR / 'errors'
        
        # Создаем директории при инициализации
        for directory in [self.LOGS_DIR, self.STATS_DIR, self.ERRORS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Файлы для статистики
        self.COMMAND_STATS_FILE = self.STATS_DIR / 'command_stats.csv'
        self.USER_ACTIVITY_FILE = self.STATS_DIR / 'user_activity.csv'
        
        # Инициализируем файлы статистики
        self._init_stats_files()

    def _init_stats_files(self):
        """Инициализирует файлы статистики с заголовками"""
        if not self.COMMAND_STATS_FILE.exists():
            with open(self.COMMAND_STATS_FILE, 'w', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['command', 'usage_count', 'last_used'])
        
        if not self.USER_ACTIVITY_FILE.exists():
            with open(self.USER_ACTIVITY_FILE, 'w', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['user_id', 'date', 'message_count', 'last_activity'])

    def log_message(self, user_id: int, text: str, is_command: bool = False) -> None:
        """Логирует сообщение/команду пользователя и обновляет статистику"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f'[{timestamp}] user_id={user_id} | text={text}\n'
        
        # Логирование в общий файл
        with open(self.LOGS_DIR / 'all_messages.log', 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Логирование в пользовательский файл
        user_log_file = self.LOGS_DIR / f'user_{user_id}.log'
        with open(user_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Обновление статистики активности
        self._update_user_activity(user_id)
        
        # Если это команда - обновляем статистику команд
        if is_command:
            self._update_command_stats(text.split()[0])  # Берем первое слово (/start)

    def log_error(self, error: str, user_id: Optional[int] = None) -> None:
        """Логирует ошибку с привязкой к пользователю (если указан)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_info = f"user_id={user_id} | " if user_id else ""
        error_entry = f'[{timestamp}] {user_info}Error: {error}\n'
        
        with open(self.ERRORS_DIR / 'errors.log', 'a', encoding='utf-8') as f:
            f.write(error_entry)

    def _update_user_activity(self, user_id: int) -> None:
        """Обновляет статистику активности пользователя"""
        today = datetime.now().strftime('%Y-%m-%d')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Читаем текущую статистику
        activities = {}
        if self.USER_ACTIVITY_FILE.exists():
            with open(self.USER_ACTIVITY_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = (row['user_id'], row['date'])
                    activities[key] = {
                        'count': int(row['message_count']),
                        'last': row['last_activity']
                    }
        
        # Обновляем данные
        key = (str(user_id), today)
        if key in activities:
            activities[key]['count'] += 1
            activities[key]['last'] = timestamp
        else:
            activities[key] = {'count': 1, 'last': timestamp}
        
        # Записываем обновленные данные
        with open(self.USER_ACTIVITY_FILE, 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'date', 'message_count', 'last_activity'])
            for (uid, date), data in activities.items():
                writer.writerow([uid, date, data['count'], data['last']])

    def _update_command_stats(self, command: str) -> None:
        """Обновляет статистику использования команд"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Читаем текущую статистику
        commands = {}
        if self.COMMAND_STATS_FILE.exists():
            with open(self.COMMAND_STATS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    commands[row['command']] = {
                        'count': int(row['usage_count']),
                        'last': row['last_used']
                    }
        
        # Обновляем данные
        if command in commands:
            commands[command]['count'] += 1
            commands[command]['last'] = timestamp
        else:
            commands[command] = {'count': 1, 'last': timestamp}
        
        # Записываем обновленные данные
        with open(self.COMMAND_STATS_FILE, 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['command', 'usage_count', 'last_used'])
            for cmd, data in commands.items():
                writer.writerow([cmd, data['count'], data['last']])

    def get_command_stats(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Возвращает топ-N самых используемых команд"""
        if not self.COMMAND_STATS_FILE.exists():
            return []
        
        with open(self.COMMAND_STATS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            stats = [(row['command'], int(row['usage_count'])) for row in reader]
        
        return sorted(stats, key=lambda x: x[1], reverse=True)[:limit]

    def get_user_activity(self, user_id: int) -> Dict[str, int]:
        """Возвращает статистику активности пользователя"""
        if not self.USER_ACTIVITY_FILE.exists():
            return {}
        
        user_stats = {}
        with open(self.USER_ACTIVITY_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user_id'] == str(user_id):
                    user_stats[row['date']] = int(row['message_count'])
        
        return user_stats

# Создаем экземпляр логгера для импорта
logger = ActivityLogger()