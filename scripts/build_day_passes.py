"""Preview a six-pass sky chart for the published San Francisco reference point."""
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skyfield.api import EarthSatellite, load, wgs84

repo = Path(__file__).resolve().parents[1]
name, line1, line2 = (repo / 'evidence/later-orbit.tle').read_text().splitlines()
ts = load.timescale(builtin=True)
satellite = EarthSatellite(line1, line2, name, ts)
observer = wgs84.latlon(37.8, -122.4, elevation_m=0)
times, kinds = satellite.find_events(observer, ts.utc(2026, 9, 23, 7), ts.utc(2026, 9, 24, 7), altitude_degrees=0)
assert len(times) == 18 and list(kinds) == [0, 1, 2] * 6

fig, axes = plt.subplots(2, 3, figsize=(12, 8.4), subplot_kw={'projection': 'polar'})
fig.patch.set_facecolor('#faf9f5')
for index, ax in enumerate(axes.flat):
    rise, peak, setting = times[index * 3:index * 3 + 3]
    sample = ts.linspace(rise, setting, 120)
    alt, az, _ = (satellite - observer).at(sample).altaz()
    peak_alt = (satellite - observer).at(peak).altaz()[0].degrees
    angle = np.deg2rad(az.degrees)
    radius = 90 - alt.degrees
    color = '#a95b36' if index == 4 else '#315b5b'
    ax.plot(angle, radius, color=color, linewidth=2.3)
    ax.scatter([angle[0], angle[-1]], [radius[0], radius[-1]], s=20, color=color, zorder=3)
    mid = len(angle) // 2
    ax.annotate('', xy=(angle[mid + 3], radius[mid + 3]),
                xytext=(angle[mid - 3], radius[mid - 3]),
                arrowprops={'arrowstyle': '-|>', 'color': color, 'lw': 1.7})
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 90)
    ax.set_thetagrids([0, 90, 180, 270], ['N', 'E', 'S', 'W'], fontsize=9)
    ax.set_rgrids([30, 60, 90], labels=['60°', '30°', '0°'], angle=135, fontsize=7)
    ax.grid(color='#cbd6d8', linewidth=.7)
    ax.spines['polar'].set_color('#a8b8bf')
    ax.set_facecolor('white')
    local_peak = peak.utc_datetime().astimezone(ZoneInfo('America/Los_Angeles'))
    label = f'Pass {index + 1} · peak {peak_alt:.0f}° · {local_peak:%H:%M}'
    if index == 4:
        label += '\nRecorded pass'
    ax.set_title(label, fontsize=11, color=color, pad=18, fontweight='bold')

fig.suptitle('Meteor M2-4 · six passes on 23 September 2026', fontsize=17, color='#252722', y=.98)
fig.text(.5, .915, 'Representative San Francisco point · times PDT · not the receiving site',
         ha='center', fontsize=10, color='#586263')
fig.text(.5, .025, 'Each path runs from rise to set. Outer ring = horizon (0°); center = overhead (90°).',
         ha='center', fontsize=10, color='#586263')
fig.subplots_adjust(left=.055, right=.945, top=.80, bottom=.08, wspace=.35, hspace=.54)
fig.savefig(repo / 'media/day-passes-reference.png', dpi=160, facecolor=fig.get_facecolor(), metadata={'Software': 'Matplotlib'})
plt.close(fig)

with Image.open(repo / 'media/day-passes-reference.png') as full:
    preview = full.convert('RGB')
    preview.thumbnail((1100, 1100), Image.Resampling.LANCZOS)
    preview.save(repo / 'media/day-passes-reference-preview.jpg', quality=87, optimize=True)
