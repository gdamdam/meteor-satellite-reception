#!/usr/bin/env python3
"""Check local references, scientific counts and archived evidence consistency."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]; self.ids=[]; self.images=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        for key in ('src','href','poster'):
            if key in a: self.refs.append(a[key])
        if tag=='img': self.images.append(a)

for page_name in ('index.html', 'meteor-m2-4-2026-09-23.html',
                  'meteor-m2-3-2026-09-24.html'):
    p=Page();p.feed((ROOT/page_name).read_text())
    assert len(p.ids)==len(set(p.ids)), (page_name, 'Duplicate IDs')
    for ref in p.refs:
        url=urlsplit(ref)
        if url.scheme or url.netloc: continue
        if url.path: assert (ROOT/unquote(url.path)).is_file(), (page_name, ref)
        elif url.fragment: assert url.fragment in p.ids, (page_name, ref)
    for a in p.images:
        assert a.get('alt') is not None, (page_name, a)
        if a['src'].endswith(('.png','.jpg')) and 'width' in a and 'height' in a:
            im=Image.open(ROOT/a['src'])
            assert im.size==(int(a['width']),int(a['height'])), (a['src'],im.size)
for path in ROOT.rglob('*.md'):
    for ref in re.findall(r'\]\(([^)]+)\)',path.read_text()):
        if not urlsplit(ref).scheme: assert (path.parent/ref).is_file(), (path,ref)
for path in (ROOT/'media').rglob('*.svg'): ET.parse(path)
m=json.loads((ROOT/'evidence/manifest.json').read_text())
for n,stats in m['published_images'].items():
    path=ROOT/stats['path'];a=np.asarray(Image.open(path))
    assert hashlib.sha256(path.read_bytes()).hexdigest()==stats['sha256']
    assert int(np.all(a==0,axis=1).sum())==stats['black_rows']
for name,data in m['later_decode'].items():
    path=ROOT/'evidence'/name
    if path.is_file() and isinstance(data,dict) and 'sha256' in data:
        assert hashlib.sha256(path.read_bytes()).hexdigest()==data['sha256'], name
assert (ROOT/'evidence/later-frames.cadu').stat().st_size==3851*1024
records=json.loads((ROOT/'evidence/later-telemetry.json').read_text())
assert len(records)==356
assert all(set(r)<= {'msu_mr_id','msu_mr_set'} for r in records)
for line in (ROOT/'evidence/later-orbit.tle').read_text().splitlines()[1:]:
    assert len(line)==69
    checksum=sum(int(c) if c.isdigit() else 1 if c=='-' else 0 for c in line[:68])%10
    assert checksum==int(line[68]),line
for row in csv.DictReader((ROOT/'evidence/black-rows.csv').open()):
    assert abs(float(row['percent'])-int(row['fully_black_rows'])/int(row['total_rows'])*100)<1e-8
m23=ROOT/'evidence/m2-3'
assert json.loads((m23/'successful-dataset.json').read_text())['satellite']=='METEOR-M2-3'
assert (m23/'successful-frames.cadu').stat().st_size==3559*1024
assert len(json.loads((m23/'successful-telemetry.json').read_text()))==330
for part in ('m2-3',):
    folder=ROOT/'evidence'/part
    for line in (folder/'sha256sums.txt').read_text().splitlines():
        digest,name=line.split('  ',1)
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest, (part,name)
print('PASS: three pages, links, images, source hashes, frame counts and TLE checksums')
