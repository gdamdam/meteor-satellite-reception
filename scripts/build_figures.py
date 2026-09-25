#!/usr/bin/env python3
"""Rebuild report figures from published pixels and explicitly identified evidence.

Run from any directory. Never reads or modifies the external IQ archive.
"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import csv
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from skyfield.api import EarthSatellite, load, wgs84

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'media'
EVIDENCE = ROOT / 'evidence'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
                     'svg.fonttype': 'path', 'svg.hashsalt': 'meteor-report'})
PAPER = '#faf9f5'
INK = '#252722'
TEAL = '#315b5b'


def save(fig, name):
    fig.savefig(MEDIA / name, facecolor=PAPER, metadata={'Date': None})
    plt.close(fig)
    path = MEDIA / name
    if path.suffix == '.svg':
        path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')


def main():
    rows = []
    for n, label in [(1, 'visible'), (2, 'near-ir'), (4, 'mid-ir')]:
        path = MEDIA / f'channel-{n}-{label}.png'
        arr = np.asarray(Image.open(path))
        count = int(np.all(arr == 0, axis=1).sum())
        rows.append((n, count, len(arr), count / len(arr) * 100))
    with (EVIDENCE / 'black-rows.csv').open('w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['channel', 'fully_black_rows', 'total_rows', 'percent'])
        writer.writerows(rows)
    fig, ax = plt.subplots(figsize=(8.2, 2.8), layout='constrained')
    ax.set_facecolor(PAPER)
    ax.barh(range(3), [100]*3, color='#e5e3dc', height=.46)
    ax.barh(range(3), [r[3] for r in rows], color=TEAL, height=.46)
    for i, (_, count, total, percent) in enumerate(rows):
        ax.text(percent + 2, i, f'{count:,} / {total:,} rows · {percent:.2f}%', va='center', fontsize=11)
    ax.set(yticks=range(3), yticklabels=[f'Channel {r[0]}' for r in rows],
           xlim=(0, 100), xticks=[0,25,50,75,100], xlabel='Fully black rows (%)',
           title='Missing display rows: about one-tenth of each raster')
    ax.invert_yaxis()
    ax.spines[['top','right','left']].set_visible(False)
    save(fig, 'revised-line-completeness.svg')

    # Display intensity only: no radiometric calibration is available for these PNGs.
    a = np.asarray(Image.open(MEDIA / 'channel-4-mid-ir.png'), dtype=float)
    valid = a > 0
    low, high = np.percentile(a[valid], [1, 99])
    intensity = np.ma.array(np.clip((a-low)/(high-low),0,1)**.85, mask=~valid)
    fig, ax = plt.subplots(figsize=(6, 12), layout='constrained')
    cmap = plt.get_cmap('inferno').copy(); cmap.set_bad('#101820')
    im = ax.imshow(intensity, cmap=cmap, vmin=0, vmax=1, interpolation='nearest')
    ax.set_title('Meteor M2-4 · channel 4\nNormalized decoded intensity', fontsize=14)
    ax.set_axis_off()
    cb = fig.colorbar(im, ax=ax, orientation='horizontal', fraction=.035, pad=.02)
    cb.set_ticks([0,1], labels=['Lower display value','Higher display value'])
    cb.ax.tick_params(labelsize=10)
    cb.set_label('1–99% stretch · gamma 0.85 · no temperature calibration', fontsize=9)
    fig.savefig(MEDIA / 'channel-4-intensity.png', dpi=150, facecolor=PAPER)
    plt.close(fig)
    Image.open(MEDIA/'channel-4-intensity.png').convert('RGB').save(MEDIA/'channel-4-intensity-preview.jpg', quality=86, optimize=True)

    # Regenerate the curve from the archived later product TLE, NOT today's cache.
    ts = load.timescale(builtin=True)
    name, line1, line2 = (EVIDENCE/'later-orbit.tle').read_text().splitlines()
    satellite = EarthSatellite(line1, line2, name, ts)
    # Public, approximate San Francisco reference point; NOT the receiving site.
    observer = wgs84.latlon(37.8, -122.4, elevation_m=0)
    start = datetime(2026,9,23,22,41,11,tzinfo=timezone.utc)
    seconds = np.arange(-11, 931, 2)
    dates = [start+timedelta(seconds=int(s)) for s in seconds]
    elevations = (satellite-observer).at(ts.from_datetimes(dates)).altaz()[0].degrees
    with (EVIDENCE/'elevation.csv').open('w',newline='') as f:
        w=csv.writer(f, lineterminator='\n');w.writerow(['utc','seconds_from_recording_start','elevation_deg'])
        w.writerows((d.isoformat(),int(s),float(a)) for d,s,a in zip(dates,seconds,elevations))
    fig,ax=plt.subplots(figsize=(8.2,3.5),layout='constrained')
    ax.set_facecolor(PAPER)
    ax.axvspan(210,730.308096,color='#d9e8e3',label='Signal visible (approx.)')
    ax.axvspan(330,420,color='#eee3ce',label='Deep fade (approx.)')
    ax.plot(seconds,elevations,color=TEAL,label='Reference-point elevation')
    ax.axvline(730.308096,color='#8f4d37',linestyle='--')
    ax.text(720,65,'Recording ends',ha='right',fontsize=10,color='#8f4d37')
    ax.set(xlim=(-11,919),ylim=(0,75),ylabel='Elevation (°)',
           xticks=[-11,169,349,529,709,889],xticklabels=['15:41','15:44','15:47','15:50','15:53','15:56'],
           xlabel='23 September 2026 · PDT',title='Approximate pass geometry and the received signal')
    ax.legend(loc='upper left',fontsize=9,frameon=False)
    ax.spines[['top','right']].set_visible(False)
    save(fig,'revised-pass-timeline.svg')

    for source,target in [('antenna-feedpoint-crop.png','antenna-feedpoint-preview.jpg'),
                          ('waterfall-track-poster.png','waterfall-track-poster.jpg')]:
        Image.open(MEDIA/source).convert('RGB').save(MEDIA/target, quality=85, optimize=True)
    # A full swath, contained in a landscape card, avoids silently cropping data.
    with Image.open(MEDIA/'false-color-421.png') as source:
        card=Image.new('RGB',(1200,630),PAPER)
        preview=source.copy();preview.thumbnail((1200,630),Image.Resampling.LANCZOS)
        card.paste(preview,((1200-preview.width)//2,(630-preview.height)//2))
        card.save(MEDIA/'social-preview.jpg',quality=88,optimize=True)
    print('Rebuilt row statistics, timeline, intensity figure and optimized previews.')


if __name__ == '__main__':
    main()
