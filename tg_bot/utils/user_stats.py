import csv
from typing import Any, Dict

from utils.logger import logger
from utils.i18n import translator

def get_user_stats(user_id: int) -> dict:
    """Получает статистику пользователя из CSV"""
    stats = {
        'total_commands': 0,
        'last_active': 'never',
        'favorite_command': None
    }
    
    try:
        with open('data/user_activity.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            user_commands = []
            
            for row in reader:
                if int(row['user_id']) == user_id:
                    stats['total_commands'] += 1
                    user_commands.append(row['command'])
                    stats['last_active'] = row['timestamp']
            
            if user_commands:
                stats['favorite_command'] = max(set(user_commands), key=user_commands.count)
    
    except FileNotFoundError:
        logger.log_error("user_activity.csv not found")
    except Exception as e:
        logger.log_error(f"Error reading stats: {e}")
    
    return stats

def format_stats_message(stats: Dict[str, Any], lang: str) -> str:
    """Форматирует статистику в сообщение"""
    # Рассчитываем среднюю активность
    avg_activity = 0
    if stats['recent_activity']:
        total = sum(day['messages'] for day in stats['recent_activity'])
        avg_activity = round(total / len(stats['recent_activity']), 1)
    
    # Формируем топ команд
    top_commands = "\n".join(
        f"    • {cmd}: {count}" 
        for cmd, count in sorted(
            stats['command_stats'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
    ) if stats['command_stats'] else translator.get("no_commands", lang=lang, default="    • Нет данных")
    
    # Основное сообщение
    return (
        f"<b>📊 {translator.get('stats_title', lang=lang, default='Ваша статистика')}</b>\n\n"
        f"👤 <b>{stats['basic_info']['first_name']} {stats['basic_info']['last_name']}</b>\n"
        f"🔹 @{stats['basic_info']['username']}\n\n"
        f"• {translator.get('stats_total', lang=lang, default='Всего команд')}: <code>{stats['activity']['total_commands']}</code>\n"
        f"• {translator.get('stats_last', lang=lang, default='Последняя активность')}: <code>{stats['activity']['last_active']}</code>\n"
        f"• {translator.get('stats_first', lang=lang, default='Первое посещение')}: <code>{stats['activity']['first_seen']}</code>\n"
        f"• {translator.get('stats_days', lang=lang, default='Дней активности')}: <code>{stats['activity']['days_active']}</code>\n"
        f"• {translator.get('stats_avg', lang=lang, default='Ср. активность (30д)')}: <code>{avg_activity} сообщ./день</code>\n\n"
        f"<b>🏆 {translator.get('stats_top_commands', lang=lang, default='Топ команд')}:</b>\n"
        f"{top_commands}\n\n"
    )

