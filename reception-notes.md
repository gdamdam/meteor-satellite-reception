# Meteor M2-4 LRPT reception — 23 September 2026

## Recording

| Item | Value |
| --- | --- |
| Satellite / instrument | Meteor M2-4 / MSU-MR |
| IQ file | `2026-09-23_22-41-11_2000000SPS_137500000Hz.cs16` |
| Archive directory | External archive; local path withheld |
| Recording start | 22:41:11 UTC / 15:41:11 PDT, from the filename |
| Recording duration | 730.308096 seconds, derived from byte count and sample rate |
| Recording end | Approximately 22:53:21 UTC / 15:53:21 PDT |
| Raw file size | 5,842,464,768 bytes (5.44 GiB) |
| Format | Interleaved signed 16-bit I/Q (`cs16`), 2,000,000 complex samples/s |
| Receiver center | 137.500 MHz |
| Meteor signal | Approximately 137.900 MHz; **+400 kHz above center** |
| Decoder shift | **−400 kHz**, translating that signal to baseband in this SatDump setup |

The original recording is preserved externally. Its checksum and source identities are in [the manifest](evidence/manifest.json).

## Two decode runs must remain distinct

| Evidence | Original publication | Later saved OUT run |
| --- | --- | --- |
| Frame count | 3,796, reported in original notes; matching frame file unavailable | 3,851, measured from archived CADU size |
| Telemetry | 349 records / 50 analog, reported; matching source unavailable | 356 records / no analog, verified from archived JSON |
| SNR | 8.03 dB snapshot / 13.41 dB peak, reported; log unavailable | 13.46 dB snapshot / 14.08 dB peak-so-far, verified from log |
| Channel dimensions | 1568 × 3192 publication PNGs | 1568 × 3216 / 3224 / 3224, logged for channels 1 / 2 / 4 |

Neither SNR snapshot is a pass-wide average. The later log confirms synchronization and explicitly disables calibration. It does not validate the original numbers. See the [evidence guide](evidence/README.md) and [later log excerpt](evidence/later-decode.log).

The earlier telemetry trace has been withdrawn because the original analog records are unavailable. A “Detector Temperature Channel 5” telemetry field does not imply recovery of channel 5 imagery.

## Bands and display processing

| Channel | Nominal center | Spectral interval | Interpretation |
| --- | --- | --- | --- |
| 1 | 0.60 µm | 0.50–0.70 µm | Reflected visible daylight |
| 2 | 0.90 µm | 0.70–1.10 µm | Reflected near-infrared daylight |
| 4 | 3.80 µm | 3.50–4.10 µm | Midwave infrared, including daytime reflected sunlight |

Band definitions and the nominal 1 km IFOV come from [WMO OSCAR](https://space.oscar.wmo.int/instruments/view/msu_mr). That IFOV is not uniform ground resolution across these unprojected PNGs.

No channel 3, 5 or 6 image is included. These bands cannot make a natural-color photograph. The publication PNGs are 8-bit grayscale, 1568 × 3192; their black-row counts are 344 / 328 / 360, or 10.78% / 10.28% / 11.28%. These are display-raster statistics, not packet-loss rates. Partial-row gaps are not counted.

Channels 1 and 4 match surviving source images after a 180° rotation. The displayed channel 2 image differs from the saved original, and no records were found explaining what changes were made. The existing composites are retained as published. Their historical notes specify a 1st-to-99th-percentile stretch and gamma 0.85 per constituent channel, but the original generation script was not recovered.

The new pseudocolor figure is reproducible: it stretches nonzero channel-4 pixels between their 1st and 99th percentiles, normalizes to 0–1, applies power 0.85 and the inferno color map, and masks zeros. It represents **normalized decoded intensity**, not calibrated radiance or temperature.

## Files in this repository

| File | Dimensions | Role |
| --- | --- | --- |
| [Channel 1](media/channel-1-visible.png) | 1568 × 3192 | Preserved publication raster |
| [Channel 2](media/channel-2-near-ir.png) | 1568 × 3192 | Preserved publication raster |
| [Channel 4](media/channel-4-mid-ir.png) | 1568 × 3192 | Preserved publication raster |
| [4-2-1 composite](media/false-color-421.png) | 1568 × 3192 | Red=4, green=2, blue=1 |
| [2-2-1 composite](media/visible-near-ir-221.png) | 1568 × 3192 | Red=2, green=2, blue=1 |
| [Channel 4 intensity](media/channel-4-intensity.png) | 900 × 1800 | Regenerated upright pseudocolor display |
| [Waterfall](media/waterfall.png) | 2040 × 1530 | Relative received power; no absolute dBm calibration |
| [Video](media/waterfall-track.mp4) | 1600 × 900; 60 s; 20 fps | Recorded signal and illustrative sky track from the public reference point |
| [Video poster](media/waterfall-track-poster.jpg) | 1600 × 900 | Frame from the public video |

JPEG gallery previews show the entire raster. Full-resolution links retain the PNGs. The video accelerates the 730.308-second recording by approximately 12.2×. The sky path is calculated from the archived TLE for the same representative San Francisco point used in the charts, not the exact receiving site. The exact-site coordinate label is omitted. [Build script](scripts/build_public_video.py).

## Orbital predictions

The original nextpass summary placed rise near 15:41 PDT, peak near 15:49 at about 62°, and set near 15:56. Its exact pass times and observer coordinates are kept privately. The original summary used a TLE epoch of 07:26:39 UTC, but the exact orbital elements were not preserved. The 0° horizon gives the full geometric pass; a 10° reception threshold gives a shorter window.

The new timeline is independently recomputed from the [later product TLE](evidence/later-orbit.tle), epoch 22:38:16.87 UTC, using a representative San Francisco reference point rather than the exact receiving site. [Reference-point elevation samples](evidence/elevation.csv) are included. The shaded signal and fade windows remain approximate visual readings from the waterfall, not decoder-lock measurements.

The [six-pass sky chart](media/day-passes-reference.png) uses the same archived TLE and public reference point. It is regenerated by [build_day_passes.py](scripts/build_day_passes.py); minute labels are rounded, and the highlighted afternoon path corresponds to the recorded pass. It is not the original exact-site prediction.

## Repeat a decode

For an installed iqscan command:

```sh
iqscan meteor /path/to/recording_2000000SPS_137500000Hz.cs16 \
  --satellite M2-4 --frequency 137900000 --video
```

From the root of an iqscan source checkout, `./scan.sh meteor …` is the alternative launcher. The report used iqscan 1.4.1 and SatDump 1.2.2; inspect the actual image/CADU outputs, not just process exit status. A later CLI attempt returned success but produced zero frames.

For SatDump offline processing: Meteor M2-x LRPT 72k, baseband CS16, 2 Msps, shift −400 kHz, DC blocking on, I/Q swap off, RS check on, fill missing off, satellite M2-4. Use a new output directory. Preserve logs, product metadata, exact orbital elements and recovered frames alongside the IQ file.

Settings glossary: baseband I/Q is the raw recording of two radio-signal components. CS16 stores each component as a signed 16-bit integer; 2 Msps means two million complex samples per second. Decimation reduces the sample rate, so 1 means no reduction at that stage. LNA and IF are gain controls; AGC adjusts gain automatically. Notches reject selected interfering bands, and bias supplies power through the antenna connection. DC blocking removes a constant offset; I/Q swap exchanges the two components; RS check rejects frames that fail Reed–Solomon error checking. These definitions explain this run, not universal receiver settings. Keeping “fill missing” off preserves missing rows. The video workflow uses ffmpeg, Pillow, Skyfield, the configured observing position and orbital data.

The LRPT pipeline uses 72,000 OQPSK symbols/s, Viterbi and Reed–Solomon decoding, and 1,024-byte CADUs. Symbol rate is not receiver sample rate or image-pixel rate. See the [SatDump pipeline](https://github.com/SatDump/SatDump/blob/master/resources/pipelines/Meteor-M.json).

## Next-pass measurements

Record through predicted set. Save time-aligned SNR, lock and frame counts. Measure the suspected house obstruction’s azimuth/elevation before attributing a fade to it. Compare one antenna height, orientation or gain change at a time, and retain untouched data for each run.
