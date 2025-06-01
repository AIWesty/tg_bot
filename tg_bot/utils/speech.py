import json
from vosk import Model, KaldiRecognizer
import librosa
import soundfile as sf
import os

MODEL_DIR = "models/vosk-model-small-ru"
model = Model(MODEL_DIR)

def ogg_to_wav_bytes(ogg_path: str) -> bytes:
    """Конвертирует OGG в WAV (16kHz, моно) и возвращает bytes."""
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
        
        wav_bytes = ogg_to_wav_bytes(audio_path)
        if not wav_bytes:
            print("Ошибка: не удалось конвертировать аудио")
            return ""
            
        rec = KaldiRecognizer(model, 16000)
        if rec.AcceptWaveform(wav_bytes):
            result = json.loads(rec.Result())
            return result.get("text", "").strip()
        
        partial = json.loads(rec.PartialResult())
        return partial.get("partial", "").strip()
        
    except Exception as e:
        print(f"Ошибка распознавания: {e}")
        return ""