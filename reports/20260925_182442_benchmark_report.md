# Traffic Light Detection Benchmark Report
## Metadata

| Field | Value |
|-------|-------|
| Generated at | 2026-09-25T19:06:30.608583 |
| Git commit   | `dc949316ea3f` |
| Resolution | 640x480 |
| FPS | 30 |
| Camera backend | picamera2 |
| Exposure (us) | 20000 |
| Analogue gain | 4.0 |
| HDR mode | HdrModeEnum.Off |
| NR mode | NoiseReductionModeEnum.Fast |
| Run note | table setup, static, various-color background |

## Dataset Overview

- **Total frames**: 18
- **Ground truth with bbox**: 18
- **Ground truth without bbox**: 0
- **Housing detected**: 12
- **Housing missed as GT**: 6

## Overall Metrics

| Metric | Value |
|--------|-------|
| Phase Accuracy | 44.4% (8/18) |
| Localization Accuracy | 5.6% (1/18) |
| Mean IoU | 0.1383 |
| Median IoU | 0.1762 |
| IoU Std Dev | 0.1604 |
| IoU Range | [0.0000, 0.6974] |
| IoU P50 | 0.1762 |
| IoU P90 | 0.1842 |
| IoU P95 | 0.2613 |
| Avg Detection Time | 9.71 ms |

## Per-Phase Breakdown

| Phase | Count | Phase Accuracy | Mean IoU | Median IoU | Min IoU | Max IoU |
|-------|-------|----------------|----------|------------|---------|---------|
| green | 4 | 75.0% | 0.1800 | 0.1795 | 0.1765 | 0.1841 |
| off | 4 | 100.0% | 0.1785 | 0.1785 | 0.1772 | 0.1799 |
| red | 9 | 0.0% | 0.1788 | 0.1776 | 0.1743 | 0.1843 |
| yellow | 1 | 100.0% | 0.6974 | 0.6974 | 0.6974 | 0.6974 |

## Failure Modes

| Failure Mode | Count | Percentage |
|--------------|-------|------------|
| poor_localization (IoU < 0.5) | 11 | 61.1% |
| false_negative (missed detection) | 6 | 33.3% |
| correct | 1 | 5.6% |

## Per-Frame Results

| Frame | GT Phase | Predicted | IoU | Localization Correct | Housing Found | Failure Mode |
|-------|----------|-----------|-----|---------------------|---------------|--------------|
| 103 | red | yellow | 0.1822 | False | True | poor_localization (IoU < 0.5) |
| 104 | off | off | 0.1799 | False | True | poor_localization (IoU < 0.5) |
| 105 | off | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 106 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 107 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 108 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 109 | red | yellow | 0.1758 | False | True | poor_localization (IoU < 0.5) |
| 110 | red | yellow | 0.1843 | False | True | poor_localization (IoU < 0.5) |
| 111 | red | yellow | 0.1743 | False | True | poor_localization (IoU < 0.5) |
| 112 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 113 | green | green | 0.1841 | False | True | poor_localization (IoU < 0.5) |
| 114 | green | green | 0.1795 | False | True | poor_localization (IoU < 0.5) |
| 115 | off | off | 0.1772 | False | True | poor_localization (IoU < 0.5) |
| 116 | off | off | 0.0000 | False | False | false_negative (missed detection) |
| 117 | green | off | 0.0000 | False | False | false_negative (missed detection) |
| 118 | green | green | 0.1765 | False | True | poor_localization (IoU < 0.5) |
| 119 | yellow | yellow | 0.6974 | True | True | correct |
| 120 | red | yellow | 0.1776 | False | True | poor_localization (IoU < 0.5) |
