# Evidence guide

This archive distinguishes the **original publication images** from a **later decode of the same IQ recording**. Do not mix their counts, telemetry, or SNR values.

## Original publication

- `../media/channel-{1,2,4}-*.png`: the existing 1568 × 3192 publication rasters, preserved byte-for-byte.
- `black-rows.csv`: freshly measured fully zero rows in those rasters. This is not a packet-loss measure and misses partial-row gaps.
- The original detailed pass prediction remains in a private archive because its times and coordinates can identify the receiving site. The report gives rounded times.
- `manifest.json`: SHA-256 and size of the original IQ, identities of the publication rasters and surviving source PNGs, and historical values from the original report.

The original report listed 3,796 frames, 349 telemetry records (50 analog), an 8.03 dB SNR snapshot and a 13.41 dB peak. Its matching log, CADU and telemetry file were not located. These values remain explicitly historical, not independently verified. The old telemetry plot was removed because its source records are unavailable.

Channels 1 and 4 match the surviving `IMAGES` originals after a 180° rotation. The displayed channel 2 image differs from the saved original, and no records were found explaining what changes were made. It is kept as originally published. The original composite-processing script is also unavailable, so its stated percentile/gamma settings are historical documentation rather than a reproduced transformation.

## Later decode: 2026-09-24 03:01 UTC

- `later-decode.log`: exact lines 780–876 from `satdump-20260923T195616.log`. This excerpt includes genericized input/output paths, settings, synchronized decoder, SNR snapshot and calibration warning. The manifest identifies and hashes the full source log.
- `later-frames.cadu`: saved OUT frame stream, 3,943,424 bytes / 1,024 = **3,851 frames**.
- `later-telemetry.json`: **356 records**, containing instrument ID/set fields, with no analog values.
- `later-dataset.json` and `later-product.cbor`: later SatDump metadata.
- `later-orbit.tle`: exact 69-column TLE lines extracted from that product, epoch **2026-09-23 22:38:16.87 UTC**.
- `elevation.csv`: predicted elevation recomputed with Skyfield using that TLE and a representative San Francisco reference point, not the receiving site. This is a new, reproducible curve, not a reconstruction using the lost original nextpass elements.
- `../media/day-passes-reference.png`: six sky paths recomputed from the same TLE and public reference point by `../scripts/build_day_passes.py`. The original exact-site chart is not published.

The later log shows **13.456419 dB SNR and 14.081358 dB peak-so-far at one progress snapshot**. Its channel heights are 3,216 / 3,224 / 3,224, unlike the publication images. It explicitly reports that calibration is disabled. It cannot substantiate the original run’s different statistics.

A subsequent 03:12 UTC command-line attempt produced zero frames despite exit code 0. That attempt is not used as evidence for successful decoding. Check actual output products when repeating a decode; process exit status alone is insufficient.

## Rebuild the figures

From the repository root, in a Python environment with `scripts/requirements.txt` installed:

```sh
python scripts/build_figures.py
python scripts/verify_report.py
```

The script requires no network or external IQ. It regenerates the correctly scaled row chart/CSV, a TLE-based elevation chart/CSV, the normalized-intensity figure, photo/poster previews and sharing card. The scientific image is generated directly from the upright channel 4 PNG, without embedded image cropping or CSS rotation.

Intensity processing: exclude zero-valued pixels when finding the 1st and 99th percentiles, clip to that range, normalize to 0–1, raise to power 0.85, and map through `inferno`. Zero pixels are masked dark. This is a display transform, not radiance calibration. Missing data is not interpolated.

The original decoded composites, waterfall and map overlay are preserved artifacts; this script does not claim to regenerate them. The public video shows the recorded spectrum and waterfall alongside a sky track calculated for the public San Francisco reference point. The exact-site track and coordinate label are not published. [Build script](../scripts/build_public_video.py).

## External raw recording

The 5,842,464,768-byte CS16 recording remains in a private external archive; it is not committed to Git. The manifest uses a generic path label. Its SHA-256 is:

`dad6cbf59329a634b7cf02b728fdf5445b1f3b5aa4cfe356b331d1f6d957877d`

At 2,000,000 complex samples/s × 4 bytes/sample, this is 730.308096 seconds. Retain that file, the original source PNGs and decoder outputs for future reprocessing. The source archives were not modified while preparing this report.
