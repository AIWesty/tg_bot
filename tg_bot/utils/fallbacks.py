from typing import Optional
import json
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta

class FallbackManager:
    def __init__(self):
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # кеш последних успешных запросов
        self.weather_cache = self._load_cache("weather")
        self.cat_cache = self._load_cache("cats")

    def _load_cache(self, cache_type: str) -> Dict:
        cache_file = self.cache_dir / f"{cache_type}_cache.json"
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_cache(self, cache_type: str, data: Dict):
        cache_file = self.cache_dir / f"{cache_type}_cache.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def get_weather_fallback(self, city: str) -> Optional[str]:
        """Возвращает закэшированные данные или None"""
        cached = self.weather_cache.get(city)
        if cached and datetime.now() - datetime.fromisoformat(cached["time"]) < timedelta(hours=1):
            return cached["text"]
        return None
    
    def update_weather_cache(self, city: str, temperature: str, wind: str, clouds: str):
        """Обновляет кэш погоды с полными данными"""
        self.weather_cache[city] = {
            "text": (
                f"🌤 Погода в {city}:\n"
                f"🌡 Температура: {temperature}\n"
                f"💨 Ветер: {wind}\n"
                f"☁️ Облачность: {clouds}"
            ),
            "time": datetime.now().isoformat()
        }
        self._save_cache("weather", self.weather_cache)

    def get_cat_fallback(self) -> str:
        """Возвращает последнюю успешную ссылку или дефолтную"""
        return self.cat_cache.get("last_url", "https://cdn.pixabay.com/photo/2017/02/20/18/03/cat-2083492_640.jpg")

    def update_cat_cache(self, image_url: str):
        """Обновляет кэш котиков"""
        self.cat_cache["last_url"] = image_url
        self._save_cache("cats", self.cat_cache)

    def get_voice_fallback(self) -> str:
        return "Извините, сейчас не могу распознать речь. Попробуйте написать текстом."

# Глобальный экземпляр для импорта
fallback = FallbackManager()