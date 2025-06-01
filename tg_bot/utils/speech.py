import os
import wave
import json
from vosk import Model, KaldiRecognizer

MODEL_PATH = 'utils/vosk-model-small-ru-0.22'
model = Model(MODEL_PATH)

def speech_to_text(audio_path: str) -> str:
    try:
        with wave.open(audio_path, "rb") as wf:
            rec = KaldiRecognizer(model, wf.getframerate())
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    results.append(json.loads(rec.Result())["text"])
            return " ".join(results).strip()
    except Exception as e:
        print(f"Ошибка распознавания: {e}")
        return ""