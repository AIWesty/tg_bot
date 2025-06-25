# выбран наиболее рабочий вариант конвертации OGG(формат гс в телеграм) в WAV для работы с vosk 
# ffmpeg не работает под виндовc(можно запустить, но с локальной установкой и добавлением в переменную path, вердикт - неудобно)
# pydub не работает нигде(Ошибка с отсутствием audioop)
# librosa зависит от numpy (то есть при установке проекта - занимает много места)

import os
import json
import logging
import numpy as np
from io import BytesIO
from typing import Optional
import librosa
import soundfile as sf
from vosk import Model, KaldiRecognizer
from aiogram import Router, F
from aiogram.types import Message

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
MODEL_DIR = "models/vosk-model-small-ru"  # Путь к модели Vosk
TEMP_DIR = "temp"  # Папка для временных файлов
os.makedirs(TEMP_DIR, exist_ok=True)  # Создаем папку, если её нет

# Загрузка модели Vosk
try:
    model = Model(MODEL_DIR)
    logger.info(f"Модель Vosk загружена из {MODEL_DIR}")
except Exception as e:
    logger.error(f"Ошибка загрузки модели Vosk: {e}")
    model = None

def ogg_to_wav(ogg_path: str) -> Optional[bytes]:
    """Конвертирует OGG в WAV (16kHz, моно) с проверками."""
    try:
        # Проверка существования файла
        if not os.path.exists(ogg_path):
            logger.error(f"Файл не найден: {ogg_path}")
            return None

        # Проверка размера файла
        if os.path.getsize(ogg_path) == 0:
            logger.error("Файл пуст")
            return None

        # Загрузка аудио
        y, sr = librosa.load(ogg_path, sr=16000, mono=True)
        if len(y) == 0:
            logger.error("Аудио не содержит данных")
            return None

        # Проверка громкости
        max_volume = np.max(np.abs(y))
        if max_volume < 0.01:  # Порог громкости
            logger.warning(f"Слишком тихое аудио (громкость: {max_volume:.3f})")

        # Конвертация в WAV
        wav_bytes = BytesIO()
        sf.write(wav_bytes, y, 16000, format="WAV", subtype="PCM_16")
        wav_bytes.seek(0)
        return wav_bytes.read()

    except Exception as e:
        logger.error(f"Ошибка конвертации: {e}")
        return None

def speech_to_text(audio_path: str) -> str:
    """Распознает текст из аудио с проверками."""
    if model is None:
        logger.error("Модель Vosk не загружена")
        return ""

    wav_data = ogg_to_wav(audio_path)
    if not wav_data:
        return ""

    try:
        rec = KaldiRecognizer(model, 16000)
        if rec.AcceptWaveform(wav_data):
            result = json.loads(rec.Result())
            text = result.get("text", "").strip()
            if text:
                logger.info(f"Распознано: {text}")
                return text

        partial = json.loads(rec.PartialResult()).get("partial", "").strip()
        if partial:
            logger.info(f"Частично распознано: {partial}")
            return partial

        logger.warning("Не удалось распознать речь")
        return ""

    except Exception as e:
        logger.error(f"Ошибка распознавания: {e}")
        return ""
