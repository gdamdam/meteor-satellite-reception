"""Rebuild the public video with an illustrative San Francisco sky track.

Requires iqscan 1.4.1, Pillow, Skyfield, NumPy, and ffmpeg. The raw IQ is
supplied locally and is never copied into this repository.
"""
from argparse import ArgumentParser, Namespace
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw
from skyfield.api import EarthSatellite, load, wgs84
import meteor_video  # iqscan 1.4.1

repo = Path(__file__).resolve().parents[1]
parser = ArgumentParser(description=__doc__)
parser.add_argument('recording', type=Path, help='Original 2 Msps, 137.5 MHz CS16 IQ recording')
parser.add_argument('--output', type=Path, default=repo / 'media')
args_cli = parser.parse_args()
recording = args_cli.recording
if not recording.is_file():
    parser.error('Recording not found')
args_cli.output.mkdir(parents=True, exist_ok=True)
name, line1, line2 = (repo / 'evidence/later-orbit.tle').read_text().splitlines()
ts = load.timescale(builtin=True)
context = {
    'start': datetime(2026, 9, 23, 22, 41, 11, tzinfo=timezone.utc),
    'zone': meteor_video.ZoneInfo('America/Los_Angeles'),
    'latitude': 37.8,
    'longitude': -122.4,
    'observer': wgs84.latlon(37.8, -122.4, elevation_m=0),
    'satellite': EarthSatellite(line1, line2, name, ts),
}
meta = {
    'input': str(recording),
    'sample_rate': 2_000_000,
    'center_frequency_hz': 137_500_000,
    'samples': recording.stat().st_size // 4,
    'duration_s': recording.stat().st_size / 4 / 2_000_000,
}
if not 729 < meta['duration_s'] < 731:
    parser.error('Recording length does not match this report')
video_args = Namespace(satellite='M2-4', frequency=137_900_000, video_seconds=60)
original_make_base = meteor_video.make_base

def public_make_base(freq, alt_track, az_track, duration, meta, args, context):
    frame = original_make_base(freq, alt_track, az_track, duration, meta, args, context)
    draw = ImageDraw.Draw(frame)
    # iqscan 1.4.1 writes exact coordinates into this footer. Replace them
    # before any frame is encoded, and label the representative-point track.
    draw.rectangle((995, 856, 1555, 883), fill='#101d2c')
    meteor_video.label(draw, (1000, 861), 'Illustrative track · San Francisco reference point', 15, '#8dabc2')
    return frame

meteor_video.make_base = public_make_base
meteor_video.render(meta, video_args, context, args_cli.output)
with Image.open(args_cli.output / 'waterfall-track-poster.png') as poster:
    poster.convert('RGB').save(args_cli.output / 'waterfall-track-poster.jpg', quality=85, optimize=True)
