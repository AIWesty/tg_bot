import os
import json
from vosk import Model, KaldiRecognizer
import subprocess

# Путь к модели (локальная папка)
MODEL_DIR = "models/vosk-model-small-ru"
# URL модели (ZIP-архив)
MODEL_URL = "https://github.com/alphacep/vosk-api/releases/download/v0.22/vosk-model-small-ru-0.22.zip"


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
    return subprocess.run(cmd, capture_output=True).stdout

def speech_to_text(audio_path: str) -> str:
    try:
        wav_data = ogg_to_wav(audio_path)
        if not wav_data:
            print("Ошибка: не удалось конвертировать аудио")
            return ""
            
        rec = KaldiRecognizer(model, 16000)
        if rec.AcceptWaveform(wav_data):
            result = json.loads(rec.Result())
            return result.get("text", "").strip()
        
        # Получаем частичный результат, если есть
        partial = json.loads(rec.PartialResult())
        return partial.get("partial", "").strip()
        
    except Exception as e:
        print(f"Ошибка распознавания: {e}")
        return ""