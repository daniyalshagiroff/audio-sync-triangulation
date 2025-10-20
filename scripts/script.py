import soundfile as sf
import numpy as np
from datetime import datetime, timedelta

# путь к файлу
filename = r".\data\raw\2025-09-16T11-00-00Z_M1.wav"

# читаем файл
data, samplerate = sf.read(filename)

# если стерео — берем среднее
if data.ndim > 1:
    data = np.mean(data, axis=1)

# индекс пика (максимального по амплитуде)
peak_index = np.argmax(np.abs(data))

# время пика в секундах
peak_time_s = peak_index / samplerate

# пример базового времени
base_time = datetime.fromisoformat("2025-09-16T11:00:00")

# прибавляем смещение в миллисекундах
true_peak_time = base_time + timedelta(seconds=peak_time_s)

print(f"📍Пик найден на {peak_time_s:.6f} секунд от начала файла")
print(f"→ Абсолютное время: {true_peak_time.isoformat(timespec='milliseconds')}")
