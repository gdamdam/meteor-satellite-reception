# Meteor M2-3 observation, 24 September 2026

The source recording is `2026-09-24_18-02-58_2000000SPS_137500000Hz.cs16`: signed 16-bit interleaved I/Q, 2,000,000 complex samples/s, 137.500 MHz center, and 563.867136 seconds. It begins at 18:02:58 UTC (11:02:58 PDT). Its SHA-256 is `f64a20baa6d75f768289b697169151b23fcaff570ea48b8f7c8c828f108223d3`. The original 4.5 GB recording remains off the website.

The saved SatDump [dataset](successful-dataset.json) identifies `METEOR-M2-3`. Its [CADU file](successful-frames.cadu) contains 3,559 1,024-byte decoded frames, and its [telemetry](successful-telemetry.json) has 330 records. The image products are MSU-MR channels 1, 2 and 4 plus SatDump’s 1-2-4 false-color composite. These PNGs are reproduced on the report page without pixel changes. The successful run's full log was not provided, so the exact decoder settings beyond the recording format and frequency cannot be verified from these files.

The video on the report page shows the recorded spectrum and waterfall alongside a predicted sky track and elevation chart recomputed for a representative San Francisco point using the [archived orbital elements](orbit-elements.json) with epoch 24 September 2026, 07:24 UTC. The original exact receiving-coordinate label and sky chart were not used in the public copy. The observer says a physical obstacle ended useful reception; the files themselves do not locate it or establish the exact moment of blockage.

Checksums of the public evidence files are in [sha256sums.txt](sha256sums.txt).
