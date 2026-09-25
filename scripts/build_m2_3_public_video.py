"""Build the M2-3 video with a public reference-point sky track.

Requires iqscan 1.4.1, Pillow, Skyfield, NumPy, and ffmpeg. The raw IQ file
is read locally and is never copied into the website.
"""
from argparse import ArgumentParser, Namespace
from datetime import datetime, timezone
from pathlib import Path
import json

from PIL import ImageDraw
from skyfield.api import EarthSatellite, load, wgs84
import meteor_video  # iqscan 1.4.1

repo = Path(__file__).resolve().parents[1]
parser = ArgumentParser(description=__doc__)
parser.add_argument('recording', type=Path, help='Original 2 Msps, 137.5 MHz CS16 IQ recording')
parser.add_argument('--output', type=Path, default=repo / 'media/m2-3')
args_cli = parser.parse_args()
recording = args_cli.recording
if not recording.is_file():
    parser.error('Recording not found')
args_cli.output.mkdir(parents=True, exist_ok=True)

element = json.loads((repo / 'evidence/m2-3/orbit-elements.json').read_text())
assert int(element['NORAD_CAT_ID']) == 57166
ts = load.timescale(builtin=True)
context = {
    'start': datetime(2026, 9, 24, 18, 2, 58, tzinfo=timezone.utc),
    'zone': meteor_video.ZoneInfo('America/Los_Angeles'),
    'latitude': 37.8,
    'longitude': -122.4,
    'observer': wgs84.latlon(37.8, -122.4, elevation_m=0),
    'satellite': EarthSatellite.from_omm(ts, element),
}
meta = {
    'input': str(recording),
    'sample_rate': 2_000_000,
    'center_frequency_hz': 137_500_000,
    'samples': recording.stat().st_size // 4,
    'duration_s': recording.stat().st_size / 4 / 2_000_000,
}
if not 563 < meta['duration_s'] < 565:
    parser.error('Recording length does not match the M2-3 observation')
video_args = Namespace(satellite='M2-3', frequency=137_900_000, video_seconds=60)
original_make_base = meteor_video.make_base

def public_make_base(freq, alt_track, az_track, duration, meta, args, context):
    frame = original_make_base(freq, alt_track, az_track, duration, meta, args, context)
    draw = ImageDraw.Draw(frame)
    # Replace iqscan's exact-coordinate footer before encoding any frame.
    draw.rectangle((995, 856, 1555, 883), fill='#101d2c')
    meteor_video.label(draw, (1000, 861), 'Illustrative track · San Francisco reference point', 15, '#8dabc2')
    return frame

meteor_video.make_base = public_make_base
meteor_video.render(meta, video_args, context, args_cli.output)
(args_cli.output / "waterfall-track.mp4").replace(args_cli.output / "waterfall-track-public.mp4")
(args_cli.output / "waterfall-track-poster.png").replace(args_cli.output / "waterfall-track-public-poster.png")
