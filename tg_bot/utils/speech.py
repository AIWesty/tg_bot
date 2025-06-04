# выбран наиболее рабочий вариант конвертации OGG(формат гс в телеграм) в WAV для работы с vosk 
# ffmpeg не работает под виндовc(можно запустить, но с локальной установкой и добавлением в переменную path, вердикт - неудобно)
# pydub не работает нигде(Ошибка с отсутствием audioop)
# librosa зависит от numpy (то есть при установке проекта - занимает много места)

import os
import json
from vosk import Model, KaldiRecognizer
import subprocess

# Путь к модели (локальная папка)
MODEL_DIR = "models/vosk-model-small-ru"


# Теперь загружаем модель из локальной папки
model = Model(MODEL_DIR)

def ogg_to_wav(ogg_path: str) -> bytes:
    """Конвертирует OGG в WAV (16kHz, моно) через ffmpeg."""
    cmd = [
        "ffmpeg",
        "-i", ogg_path,
        "-f", "wav",
        "-ar", "16000",
        "-ac", "1",
        "-"
    ]
    return subprocess.run(cmd, capture_output=True).stdout #запускает программу и возвращает wav в байтах 

def speech_to_text(audio_path: str) -> str:
    try:
        wav_data = ogg_to_wav(audio_path)  #применил функцию перевода wav
        if not wav_data:
            print("Ошибка: не удалось конвертировать аудио")
            return ""
            
        rec = KaldiRecognizer(model, 16000) # создание распознователя речи
        if rec.AcceptWaveform(wav_data):  #если распознование завершилось 
            result = json.loads(rec.Result()) #загужаем результат 
            return result.get("text", "").strip()
        
        # Получаем частичный результат, если есть
        partial = json.loads(rec.PartialResult())
        return partial.get("partial", "").strip()
        
    except Exception as e:
        print(f"Ошибка распознавания: {e}")
        return ""