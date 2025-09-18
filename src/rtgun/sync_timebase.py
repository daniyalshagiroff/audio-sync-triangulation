from pathlib import Path
import re
import numpy as np
import soundfile as sf
from typing import Dict, Tuple

from .config import load_cfg
from .utils_time import parse_iso, shift_iso, utc_to_sample, iso_to_filename_stamp

MIC_PATTERN = re.compile(r"^(?P<stamp>[^_]+)_(?P<mic>M[0-9]+)\.(wav|flac)$", re.IGNORECASE)

def _filename_stamp_from_trigger(trigger_iso: str) -> str:
    """
    Make 'YYYY-MM-DDTHH:MM:SSZ' then replace ':'->'-'.
    Works for strings with fractional seconds or offsets.
    """
    import re
    s = trigger_iso.strip()

    # 1) Cut fractional seconds if any: .05, .500, .123456
    s = re.sub(r'\.(\d+)(?=Z|[+\-]\d{2}:\d{2}$)', '', s)

    # 3) Extract main part YYYY-MM-DDTHH:MM:SS
    m = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', s)
    if not m:
        raise ValueError(f"Bad ISO format: {trigger_iso}")
    base = m.group(1) + 'Z'

    # 4) Replace ':' with '-'
    return base.replace(':', '-')

def _iso_from_name(name: str) -> str:
    # "2025-09-16T11-00-00Z_M1.wav" -> "2025-09-16T11:00:00Z"
    stamp = name.split("_", 1)[0]
    return re.sub(r"T(\d{2})-(\d{2})-(\d{2})Z", r"T\1:\2:\3Z", stamp)

# FIND RAW AUDIO FILES BASED ON TRIGGER TIMESTAMP 
def _find_raw_files(raw_dir: Path, trigger_iso: str) -> Dict[str, Path]:
    stamp = _filename_stamp_from_trigger(trigger_iso) # e.g. '2025-09-16T11-00-00Z'
    files: Dict[str, Path] = {}
    for p in list(raw_dir.glob(f"{stamp}_M*.wav")) + list(raw_dir.glob(f"{stamp}_M*.flac")):
        m = MIC_PATTERN.match(p.name)
        if m:
            files[m.group("mic").upper()] = p
    return files

# SLICING AUDIO, working with samples
def _pad_slice(x: np.ndarray, start: int, end: int) -> np.ndarray:
    n = len(x)
    L = end - start
    # deciding how many zeros to pad on each side
    left_pad = max(0, -start)
    right_pad = max(0, end - n)
    core_start = max(0, start)
    core_end = min(n, end)
    out = np.zeros(L, dtype=np.float32)
    #create sliced numpy array with zero padding if needed, +3 sec safety margin
    if core_end > core_start:
        out[left_pad:left_pad + (core_end - core_start)] = x[core_start:core_end]
    return out

def sync_window(trigger_iso: str) -> Tuple[Dict[str, np.ndarray], int]:
    print(f"Syncing around trigger {trigger_iso}...")
    """
    Returns dict[mic_id] -> synced mono array, and fs
    Window = [trigger - pre_margin, trigger + post_margin]
    """
    cfg = load_cfg()
    fs = cfg.defaults.sample_rate
    pre = cfg.defaults.pre_margin_s
    post = cfg.defaults.post_margin_s

    project_root = Path(__file__).resolve().parents[2]
    raw_dir = project_root / "data" / "raw"
    synced_dir = project_root / "data" / "synced"
    synced_dir.mkdir(parents=True, exist_ok=True)

    files = _find_raw_files(raw_dir, trigger_iso)
    if not files:
        raise FileNotFoundError("No raw files for trigger timestamp")

    start_iso = shift_iso(trigger_iso, -pre)
    end_iso = shift_iso(trigger_iso, post)

    # Compute target window sample indices relative to each file start
    out: Dict[str, np.ndarray] = {}
    for mic_id, path in sorted(files.items()):

        data, fs_in = sf.read(path, always_2d=False)
        if data.ndim > 1:
            data = data[:, 0]
        if fs_in != fs:
            raise ValueError(f"Sample rate mismatch for {path}: {fs_in} != {fs}")
        
        file_start_iso = _iso_from_name(path.name)
        print("file_start_iso: ", file_start_iso)
    
    
        s_idx = utc_to_sample(file_start_iso, start_iso, fs)
        print("s_idx: ", s_idx)
        e_idx = utc_to_sample(file_start_iso, end_iso,   fs)
        print("e_idx: ", e_idx)


        out[mic_id] = _pad_slice(data.astype(np.float32), s_idx, e_idx)

        # save synced file
        win_stamp = f"{iso_to_filename_stamp(start_iso)}__{iso_to_filename_stamp(end_iso)}"
        out_name = f"{win_stamp}_{mic_id}_synced.wav"
        sf.write(synced_dir / out_name, out[mic_id], fs)

    return out, fs