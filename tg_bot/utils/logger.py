from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import csv
from collections import defaultdict

class BaseLogger:
    """Базовый логгер для записи сообщений и ошибок"""
    def __init__(self):
        self.BASE_DIR = Path('data')
        self.LOGS_DIR = self.BASE_DIR / 'logs'
        self.ERRORS_DIR = self.BASE_DIR / 'errors'
        
        for directory in [self.LOGS_DIR, self.ERRORS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    def log_message(self, user_id: int, text: str) -> None:
        """Логирует сообщение пользователя"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f'[{timestamp}] user_id={user_id} | text={text}\n'
        
        # Логирование в общий файл
        with open(self.LOGS_DIR / 'all_messages.log', 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Логирование в пользовательский файл
        user_log_file = self.LOGS_DIR / f'user_{user_id}.log'
        with open(user_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def log_error(self, error: str, user_id: Optional[int] = None) -> None:
        """Логирует ошибку с привязкой к пользователю (если указан)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_info = f"user_id={user_id} | " if user_id else ""
        error_entry = f'[{timestamp}] {user_info}Error: {error}\n'
        
        with open(self.ERRORS_DIR / 'errors.log', 'a', encoding='utf-8') as f:
            f.write(error_entry)

class UserStatsLogger:
    """Логгер статистики пользователей"""
    def __init__(self):
        self.BASE_DIR = Path('data')
        self.STATS_DIR = self.BASE_DIR / 'user_stats'
        self.STATS_DIR.mkdir(parents=True, exist_ok=True)
        
        self.USER_STATS_FILE = self.STATS_DIR / 'user_stats.csv'
        self.COMMAND_STATS_FILE = self.STATS_DIR / 'command_stats.csv'
        self.DAILY_ACTIVITY_FILE = self.STATS_DIR / 'daily_activity.csv'
        
        self._init_stats_files()

    def _init_stats_files(self):
        """Инициализирует файлы статистики"""
        files = {
            self.USER_STATS_FILE: [
                'user_id', 'username', 'first_name', 'last_name',
                'total_commands', 'last_active', 'favorite_command',
                'first_seen', 'days_active'
            ],
            self.COMMAND_STATS_FILE: [
                'user_id', 'command', 'usage_count', 'last_used'
            ],
            self.DAILY_ACTIVITY_FILE: [
                'user_id', 'date', 'message_count', 'command_count'
            ]
        }
        
        for file, headers in files.items():
            if not file.exists():
                with open(file, 'w', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)

    def log_command(self, user_id: int, command: str, user_data: Optional[Dict[str, Any]] = None) -> None:
        """Логирует использование команды"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._update_user_stats(user_id, command, timestamp, user_data)
        self._update_command_stats(user_id, command, timestamp)
        self._update_daily_activity(user_id, is_command=True)

    def log_message(self, user_id: int, user_data: Optional[Dict[str, Any]] = None) -> None:
        """Логирует сообщение пользователя"""
        self._update_daily_activity(user_id)
        if user_data:
            self._ensure_user_record_exists(user_id, user_data)

    def _ensure_user_record_exists(self, user_id: int, user_data: Dict[str, Any]) -> None:
        """Создает запись о пользователе, если ее нет"""
        if not self._user_exists(user_id):
            self._add_new_user(user_id, user_data)

    def _user_exists(self, user_id: int) -> bool:
        """Проверяет существование пользователя в статистике"""
        if not self.USER_STATS_FILE.exists():
            return False
            
        with open(self.USER_STATS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return any(int(row['user_id']) == user_id for row in reader)

    def _add_new_user(self, user_id: int, user_data: Dict[str, Any]) -> None:
        """Добавляет нового пользователя в статистику"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_user = {
            'user_id': user_id,
            'username': user_data.get('username', ''),
            'first_name': user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'total_commands': 0,
            'last_active': timestamp,
            'favorite_command': '',
            'first_seen': timestamp,
            'days_active': 0
        }
        
        self._append_to_csv(self.USER_STATS_FILE, new_user)
        self._update_daily_activity(user_id)

    def _update_user_stats(self, user_id: int, command: str, timestamp: str, user_data: Optional[Dict[str, Any]]) -> None:
        """Обновляет основную статистику пользователя"""
        updated_rows = []
        updated = False
        
        with open(self.USER_STATS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['user_id']) == user_id:
                    # Обновляем данные
                    row['total_commands'] = str(int(row['total_commands']) + 1)
                    row['last_active'] = timestamp
                    
                    # Обновляем любимую команду
                    command_counts = self._get_user_command_counts(user_id)
                    if command_counts:
                        row['favorite_command'] = max(command_counts.items(), key=lambda x: x[1])[0]
                    
                    # Обновляем профиль пользователя
                    if user_data:
                        row.update({
                            'username': user_data.get('username', row['username']),
                            'first_name': user_data.get('first_name', row['first_name']),
                            'last_name': user_data.get('last_name', row['last_name'])
                        })
                    
                    updated = True
                updated_rows.append(row)
        
        if not updated:
            self._add_new_user(user_id, user_data or {})
            return
        
        self._write_csv(self.USER_STATS_FILE, updated_rows[0].keys(), updated_rows)

    def _update_command_stats(self, user_id: int, command: str, timestamp: str) -> None:
        """Обновляет статистику команд пользователя"""
        updated = False
        updated_rows = []
        
        with open(self.COMMAND_STATS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['user_id']) == user_id and row['command'] == command:
                    row['usage_count'] = str(int(row['usage_count']) + 1)
                    row['last_used'] = timestamp
                    updated = True
                updated_rows.append(row)
        
        if not updated:
            updated_rows.append({
                'user_id': user_id,
                'command': command,
                'usage_count': 1,
                'last_used': timestamp
            })
        
        self._write_csv(self.COMMAND_STATS_FILE, ['user_id', 'command', 'usage_count', 'last_used'], updated_rows)

    def _update_daily_activity(self, user_id: int, is_command: bool = False) -> None:
        """Обновляет дневную активность пользователя"""
        today = datetime.now().strftime('%Y-%m-%d')
        updated = False
        updated_rows = []
        
        with open(self.DAILY_ACTIVITY_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['user_id']) == user_id and row['date'] == today:
                    row['message_count'] = str(int(row['message_count']) + 1)
                    if is_command:
                        row['command_count'] = str(int(row['command_count']) + 1)
                    updated = True
                updated_rows.append(row)
        
        if not updated:
            updated_rows.append({
                'user_id': user_id,
                'date': today,
                'message_count': 1,
                'command_count': 1 if is_command else 0
            })
        
        self._write_csv(self.DAILY_ACTIVITY_FILE, ['user_id', 'date', 'message_count', 'command_count'], updated_rows)

    def _get_user_command_counts(self, user_id: int) -> Dict[str, int]:
        """Возвращает счетчики команд для пользователя"""
        command_counts = defaultdict(int)
        
        if self.COMMAND_STATS_FILE.exists():
            with open(self.COMMAND_STATS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['user_id']) == user_id:
                        command_counts[row['command']] = int(row['usage_count'])
        
        return dict(command_counts)

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Возвращает полную статистику пользователя"""
        stats = {
            'basic_info': {
                'username': '',
                'first_name': '',
                'last_name': ''
            },
            'activity': {
                'total_commands': 0,
                'last_active': 'never',
                'favorite_command': None,
                'first_seen': 'never',
                'days_active': 0
            },
            'command_stats': {},
            'recent_activity': []
        }
        
        # Основная информация
        if self.USER_STATS_FILE.exists():
            with open(self.USER_STATS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['user_id']) == user_id:
                        stats['basic_info'].update({
                            'username': row['username'],
                            'first_name': row['first_name'],
                            'last_name': row['last_name']
                        })
                        stats['activity'].update({
                            'total_commands': int(row['total_commands']),
                            'last_active': row['last_active'],
                            'favorite_command': row['favorite_command'],
                            'first_seen': row['first_seen'],
                            'days_active': int(row['days_active'])
                        })
                        break
        
        # Статистика команд
        stats['command_stats'] = self._get_user_command_counts(user_id)
        
        # Последняя активность
        if self.DAILY_ACTIVITY_FILE.exists():
            with open(self.DAILY_ACTIVITY_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                activity = []
                for row in reader:
                    if int(row['user_id']) == user_id:
                        activity.append({
                            'date': row['date'],
                            'messages': int(row['message_count']),
                            'commands': int(row['command_count'])
                        })
                
                stats['recent_activity'] = sorted(activity, key=lambda x: x['date'], reverse=True)[:30]
        
        return stats

    def _append_to_csv(self, file: Path, row: Dict[str, Any]) -> None:
        """Добавляет строку в CSV файл"""
        with open(file, 'a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            writer.writerow(row)

    def _write_csv(self, file: Path, fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
        """Полностью перезаписывает CSV файл"""
        with open(file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

# Создаем экземпляры логгеров
logger = BaseLogger()
user_stats_logger = UserStatsLogger()