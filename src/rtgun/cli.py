import json
import click
from .sync_timebase import sync_window
from .tdoa_gcc import tdoa_delays
from .config import load_cfg
from .triangulate import azimuth_from_tdoa_xy


@click.group()
def main():
    """audio-sync-triangulation CLI"""
    pass

@main.command()
@click.option("--trigger", required=True, help="ISO UTC of trigger")
@click.option("--ref", "ref_mic", default="M1", show_default=True, help="Reference mic")
@click.option("--c", "speed", default=343.0, show_default=True, type=float, help="Speed of sound (m/s)")
@click.option("--max-lag", "max_lag_s", default=0.06, show_default=True, type=float, help="Max allowed lag (s)")
def tdoa(trigger: str, ref_mic: str, speed: float, max_lag_s: float):
    """Run sync -> GCC-PHAT -> azimuth"""
    chans, fs = sync_window(trigger)
    d_smpl, d_sec, peaks = tdoa_delays(chans, fs, ref_mic=ref_mic, max_lag_s=max_lag_s)

    cfg = load_cfg()
    mic_xy = {m.mic_id: (m.x, m.y) for m in cfg.devices.mics}

    az = azimuth_from_tdoa_xy(mic_xy, d_sec, c=speed, ref_mic=ref_mic)

    out = {
        "fs": fs,
        "ref": ref_mic,
        "delays_samples": {k: round(float(v), 6) for k, v in d_smpl.items()},
        "delays_sec": {k: round(float(v), 6) for k, v in d_sec.items()},
        "peaks": {k: round(float(p), 6) for k, p in peaks.items()},
        "azimuth_deg": round(float(az), 2),
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()