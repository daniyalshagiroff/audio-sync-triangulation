import soundfile as sf
import numpy as np

filename = r".\data\raw\2025-09-16T11-00-00Z_M1.wav"
data, samplerate = sf.read(filename)

# функция для сдвига
def shift_audio(data, samplerate, shift_seconds):
    shift_samples = int(shift_seconds * samplerate)
    if shift_samples > 0:
        # сдвигаем вправо
        shifted = np.concatenate([np.zeros(shift_samples), data[:-shift_samples]])
    elif shift_samples < 0:
        # сдвигаем влево
        shifted = np.concatenate([data[-shift_samples:], np.zeros(-shift_samples)])
    else:
        shifted = data
    return shifted

# создаем варианты
shifted_plus = shift_audio(data, samplerate, +0.07)
shifted_minus = shift_audio(data, samplerate, -0.05)
shifted_plus2 = shift_audio(data, samplerate, +0.10)  # например, ещё один вариант

# сохраняем
sf.write("gunshot_shifted_plus0.07.wav", shifted_plus, samplerate)
sf.write("gunshot_shifted_minus0.05.wav", shifted_minus, samplerate)
sf.write("gunshot_shifted_plus0.10.wav", shifted_plus2, samplerate)

print("✅ 3 файла созданы с нужными сдвигами.")
