# выбран наиболее рабочий вариант конвертации OGG(формат гс в телеграм) в WAV для работы с vosk 
# ffmpeg не работает под виндовc(можно запустить, но с локальной установкой и добавлением в переменную path, вердикт - неудобно)
# pydub не работает нигде(Ошибка с отсутствием audioop)
# librosa зависит от numpy (то есть при установке проекта - занимает много места)

import json
from vosk import Model, KaldiRecognizer
import librosa
import soundfile as sf
import os

MODEL_DIR = "models/vosk-model-small-ru" #путь к модели
model = Model(MODEL_DIR)

def ogg_to_wav_bytes(ogg_path: str) -> bytes:  
    """конвертирует OGG в WAV (16kHz, моно) и возвращает bytes"""
    try:
        # Загружаем аудио
        y, sr = librosa.load(ogg_path, sr=16000, mono=True)
        
        # Сохраняем во временный файл в памяти
        with sf.SoundFile('temp.wav', 'w', samplerate=sr, channels=1, format='WAV') as f:
            f.write(y)
        
        # Читаем байты из временного файла
        with open('temp.wav', 'rb') as f:
            return f.read()
        
    except Exception as e:
        print(f"Ошибка конвертации: {e}")
        return b""
    
    finally:
        # Удаляем временный файл
        if os.path.exists('temp.wav'):
            os.remove('temp.wav')

def speech_to_text(audio_path: str) -> str:
    try:
        print(f"Обработка файла: {audio_path}") 
        
        wav_bytes = ogg_to_wav_bytes(audio_path) #превращаем в байты
        
        if not wav_bytes:
            print("Ошибка: не удалось конвертировать аудио")
            return ""
            
        rec = KaldiRecognizer(model, 16000) #выбираем модель
        if rec.AcceptWaveform(wav_bytes): # передаем модели файл
            result = json.loads(rec.Result()) #загрузка результата
            return result.get("text", "").strip()
        
        partial = json.loads(rec.PartialResult()) #если не удалось расшифровать полностью делаем это частично
        return partial.get("partial", "").strip()
        
    except Exception as e:
        print(f"Ошибка распознавания: {e}")
        return ""