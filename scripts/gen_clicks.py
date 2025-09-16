import numpy as np
import soundfile as sf
from pathlib import Path

FS = 48000      
DURATION = 2.0   
CLICK_POS = 0.5  
DELAY_M2 = 0.004 
DELAY_M3 = 0.008 

def make_click(delay_s=0.0):
    n_samples = int(DURATION * FS)
    data = np.zeros(n_samples, dtype=np.float32)
    idx = int((CLICK_POS + delay_s) * FS)
    if idx < n_samples:
        data[idx:idx+10] = 1.0  # короткий импульс
    return data

def save_wav(fname, data):
    sf.write(fname, data, FS)

if __name__ == "__main__":
    outdir = Path("data/raw")
    outdir.mkdir(parents=True, exist_ok=True)

    save_wav(outdir / "2025-09-16T11-00-00Z_M1.wav", make_click(0.0))
    save_wav(outdir / "2025-09-16T11-00-00Z_M2.wav", make_click(DELAY_M2))
    save_wav(outdir / "2025-09-16T11-00-00Z_M3.wav", make_click(DELAY_M3))

    print("Click sounds generated and saved to 'data/raw'")