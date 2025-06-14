import json
from pathlib import Path
from typing import Dict, Optional

class Translator:
    def __init__(self, default_lang: str = 'ru') -> None:
        self.locales: Dict[str, Dict[str, str]] = {}
        self.default_lang = default_lang
        self.load_locales()

    def load_locales(self) -> None:
        """Загружает языковые файлы из папки locales"""
        locales_dir = Path('locales')
        try:
            for lang_file in locales_dir.glob('*.json'):
                lang = lang_file.stem  # Получаем 'ru' из 'ru.json'
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.locales[lang] = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load locales: {str(e)}")

    def get(self, key: str, lang: str = 'ru', **kwargs):
        try:
            result = self.locales.get(lang, {}).get(key, key)

            if isinstance(result, dict):
                # Если это словарь команд, возвращаем как есть
                return result
            elif isinstance(result, str):
                # Если это строка, форматируем при наличии kwargs
                return result.format(**kwargs) if kwargs else result
            else:
                return str(result)
        except Exception as e:
            print(f"Translation error for key '{key}': {e}")
            return key  # Возвращаем ключ как fallback

# Создаём глобальный экземпляр переводчика
translator = Translator()