# Traffic Light Detection Benchmark Report
## Metadata

| Field | Value |
|-------|-------|
| Generated at | 2026-09-23T20:07:59.192743 |
| Git commit   | `6c883a8d93bf` |

## Dataset Overview

- **Total frames**: 102
- **Ground truth with bbox**: 71
- **Ground truth without bbox**: 31
- **Housing detected**: 33
- **Housing missed as GT**: 38

## Overall Metrics

| Metric | Value |
|--------|-------|
| Phase Accuracy | 60.8% (61/102) |
| Localization Accuracy | 0.0% (0/102) |
| Mean IoU | 0.0531 |
| Median IoU | 0.0000 |
| IoU Std Dev | 0.0933 |
| IoU Range | [0.0000, 0.2991] |
| IoU P50 | 0.0000 |
| IoU P90 | 0.2181 |
| IoU P95 | 0.2687 |
| Avg Detection Time | 9.96 ms |

## Per-Phase Breakdown

| Phase | Count | Phase Accuracy | Mean IoU | Median IoU | Min IoU | Max IoU |
|-------|-------|----------------|----------|------------|---------|---------|
| green | 37 | 75.7% | 0.1885 | 0.1805 | 0.0221 | 0.2991 |
| off | 34 | 100.0% | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| red | 31 | 0.0% | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## Failure Modes

| Failure Mode | Count | Percentage |
|--------------|-------|------------|
| false_negative (missed detection) | 38 | 37.3% |
| poor_localization (IoU < 0.5) | 33 | 32.4% |
| false_positive (phantom detection) | 20 | 19.6% |
| correct (no detection) | 11 | 10.8% |

## Per-Frame Results

| Frame | GT Phase | Predicted | IoU | Localization Correct | Housing Found | Failure Mode |
|-------|----------|-----------|-----|---------------------|---------------|--------------|
| 1 | green | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 10 | green | green | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 100 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 101 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 102 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 11 | green | green | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 12 | green | green | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 13 | green | green | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 14 | green | green | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 15 | green | green | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 16 | green | green | 0.1094 | False | True | poor_localization (IoU < 0.5) |
| 17 | green | green | 0.2181 | False | True | poor_localization (IoU < 0.5) |
| 18 | green | green | 0.2636 | False | True | poor_localization (IoU < 0.5) |
| 19 | green | green | 0.2844 | False | True | poor_localization (IoU < 0.5) |
| 2 | green | green | 0.1897 | False | True | poor_localization (IoU < 0.5) |
| 20 | green | green | 0.2991 | False | True | poor_localization (IoU < 0.5) |
| 21 | green | green | 0.2748 | False | True | poor_localization (IoU < 0.5) |
| 22 | green | green | 0.2739 | False | True | poor_localization (IoU < 0.5) |
| 23 | green | green | 0.2576 | False | True | poor_localization (IoU < 0.5) |
| 24 | green | green | 0.2354 | False | True | poor_localization (IoU < 0.5) |
| 25 | green | green | 0.2029 | False | True | poor_localization (IoU < 0.5) |
| 26 | green | green | 0.1652 | False | True | poor_localization (IoU < 0.5) |
| 27 | green | green | 0.1244 | False | True | poor_localization (IoU < 0.5) |
| 28 | green | green | 0.1162 | False | True | poor_localization (IoU < 0.5) |
| 29 | green | green | 0.0792 | False | True | poor_localization (IoU < 0.5) |
| 3 | green | green | 0.1679 | False | True | poor_localization (IoU < 0.5) |
| 30 | green | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 31 | green | off | 0.0221 | False | True | poor_localization (IoU < 0.5) |
| 32 | green | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 33 | green | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 34 | green | off | 0.0000 | False | False | false_negative (missed detection) |
| 35 | green | off | 0.0000 | False | False | false_negative (missed detection) |
| 36 | green | off | 0.0000 | False | False | false_negative (missed detection) |
| 37 | green | off | 0.0000 | False | False | false_negative (missed detection) |
| 38 | off | off | 0.0000 | False | False | false_negative (missed detection) |
| 39 | off | off | 0.0000 | False | False | false_negative (missed detection) |
| 4 | green | green | 0.1713 | False | True | poor_localization (IoU < 0.5) |
| 40 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 41 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 42 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 43 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 44 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 45 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 46 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 47 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 48 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 49 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 5 | green | green | 0.1553 | False | True | poor_localization (IoU < 0.5) |
| 50 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 51 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 52 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 53 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 54 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 55 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 56 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 57 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 58 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 59 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 6 | green | green | 0.1587 | False | True | poor_localization (IoU < 0.5) |
| 60 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 61 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 62 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 63 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 64 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 65 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 66 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 67 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 68 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 69 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 7 | green | green | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 70 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 71 | off | off | 0.0000 | False | False | false_negative (missed detection) |
| 72 | off | off | 0.0000 | False | False | correct (no detection) |
| 73 | off | off | 0.0000 | False | False | correct (no detection) |
| 74 | off | off | 0.0000 | False | False | correct (no detection) |
| 75 | off | off | 0.0000 | False | False | correct (no detection) |
| 76 | off | off | 0.0000 | False | False | correct (no detection) |
| 77 | off | off | 0.0000 | False | False | correct (no detection) |
| 78 | off | off | 0.0000 | False | False | correct (no detection) |
| 79 | off | off | 0.0000 | False | False | correct (no detection) |
| 8 | green | green | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 80 | off | off | 0.0000 | False | False | correct (no detection) |
| 81 | off | off | 0.0000 | False | False | correct (no detection) |
| 82 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 83 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 84 | off | off | 0.0000 | False | False | correct (no detection) |
| 85 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 86 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 87 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 88 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 89 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 9 | green | green | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 90 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 91 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 92 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 93 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 94 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 95 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 96 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 97 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 98 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 99 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
