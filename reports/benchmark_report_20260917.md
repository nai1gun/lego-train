# Traffic Light Detection Benchmark Report
## Metadata

| Field | Value |
|-------|-------|
| Generated at | 2026-09-25T23:26:26.075572 |
| Git commit   | `e8da3320d4ee` |

## Dataset Overview

- **Total frames**: 102
- **Ground truth with bbox**: 71
- **Ground truth without bbox**: 31
- **Housing detected**: 71
- **Housing missed as GT**: 0

## Overall Metrics

| Metric | Value |
|--------|-------|
| Phase Accuracy | 94.1% (96/102) |
| Localization Accuracy | 57.8% (59/102) |
| Mean IoU | 0.6299 |
| Median IoU | 0.6545 |
| IoU Std Dev | 0.1770 |
| IoU Range | [0.0000, 0.8867] |
| IoU P50 | 0.6545 |
| IoU P90 | 0.8072 |
| IoU P95 | 0.8480 |
| Avg Detection Time | 11.03 ms |

## Per-Phase Breakdown

| Phase | Count | Phase Accuracy | Mean IoU | Median IoU | Min IoU | Max IoU |
|-------|-------|----------------|----------|------------|---------|---------|
| green | 37 | 91.9% | 0.6075 | 0.6545 | 0.0716 | 0.8538 |
| off | 34 | 91.2% | 0.2835 | 0.2835 | 0.2588 | 0.3083 |
| red | 31 | 100.0% | 0.6993 | 0.6737 | 0.5794 | 0.8867 |

## Failure Modes

| Failure Mode | Count | Percentage |
|--------------|-------|------------|
| correct | 59 | 57.8% |
| false_positive (phantom detection) | 20 | 19.6% |
| poor_localization (IoU < 0.5) | 12 | 11.8% |
| correct (no detection) | 11 | 10.8% |

## Per-Lamp Accuracy

| Lamp | Correct | Total | Accuracy |
|------|---------|-------|----------|
| green | 99 | 102 | 97.1% |
| red | 102 | 102 | 100.0% |
| yellow | 102 | 102 | 100.0% |

## Per-Frame Results

| Frame | GT Phases | Predicted | IoU | Localization Correct | Housing Found | Failure Mode |
|-------|-----------|-----------|-----|---------------------|---------------|--------------|
| 1 | green | green | 0.4138 | False | True | poor_localization (IoU < 0.5) |
| 10 | green | green | 0.6580 | True | True | correct |
| 100 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 101 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 102 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 11 | green | green | 0.6545 | True | True | correct |
| 12 | green | green | 0.6064 | True | True | correct |
| 13 | green | green | 0.5955 | True | True | correct |
| 14 | green | green | 0.6241 | True | True | correct |
| 15 | green | green | 0.6497 | True | True | correct |
| 16 | green | green | 0.6180 | True | True | correct |
| 17 | green | green | 0.6422 | True | True | correct |
| 18 | green | green | 0.6452 | True | True | correct |
| 19 | green | green | 0.6625 | True | True | correct |
| 2 | green | green | 0.3481 | False | True | poor_localization (IoU < 0.5) |
| 20 | green | green | 0.6693 | True | True | correct |
| 21 | green | green | 0.6934 | True | True | correct |
| 22 | green | green | 0.6942 | True | True | correct |
| 23 | green | green | 0.6948 | True | True | correct |
| 24 | green | green | 0.7121 | True | True | correct |
| 25 | green | green | 0.7244 | True | True | correct |
| 26 | green | green | 0.7311 | True | True | correct |
| 27 | green | green | 0.7049 | True | True | correct |
| 28 | green | green | 0.7573 | True | True | correct |
| 29 | green | green | 0.7661 | True | True | correct |
| 3 | green | green | 0.3627 | False | True | poor_localization (IoU < 0.5) |
| 30 | green | green | 0.7719 | True | True | correct |
| 31 | green | green | 0.7925 | True | True | correct |
| 32 | green | green | 0.8113 | True | True | correct |
| 33 | green | green | 0.8422 | True | True | correct |
| 34 | green | green | 0.8538 | True | True | correct |
| 35 | green | off | 0.0716 | False | True | poor_localization (IoU < 0.5) |
| 36 | green | off | 0.2486 | False | True | poor_localization (IoU < 0.5) |
| 37 | green | off | 0.3411 | False | True | poor_localization (IoU < 0.5) |
| 38 | off | off | 0.2588 | False | True | poor_localization (IoU < 0.5) |
| 39 | off | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 4 | green | green | 0.3667 | False | True | poor_localization (IoU < 0.5) |
| 40 | red | red | 0.6042 | True | True | correct |
| 41 | red | red | 0.5794 | True | True | correct |
| 42 | red | red | 0.6315 | True | True | correct |
| 43 | red | red | 0.6314 | True | True | correct |
| 44 | red | red | 0.5830 | True | True | correct |
| 45 | red | red | 0.6161 | True | True | correct |
| 46 | red | red | 0.6044 | True | True | correct |
| 47 | red | red | 0.6195 | True | True | correct |
| 48 | red | red | 0.6251 | True | True | correct |
| 49 | red | red | 0.6242 | True | True | correct |
| 5 | green | green | 0.3860 | False | True | poor_localization (IoU < 0.5) |
| 50 | red | red | 0.6422 | True | True | correct |
| 51 | red | red | 0.6490 | True | True | correct |
| 52 | red | red | 0.6474 | True | True | correct |
| 53 | red | red | 0.6721 | True | True | correct |
| 54 | red | red | 0.6533 | True | True | correct |
| 55 | red | red | 0.6895 | True | True | correct |
| 56 | red | red | 0.6737 | True | True | correct |
| 57 | red | red | 0.6920 | True | True | correct |
| 58 | red | red | 0.7328 | True | True | correct |
| 59 | red | red | 0.7144 | True | True | correct |
| 6 | green | green | 0.3890 | False | True | poor_localization (IoU < 0.5) |
| 60 | red | red | 0.7480 | True | True | correct |
| 61 | red | red | 0.7220 | True | True | correct |
| 62 | red | red | 0.7353 | True | True | correct |
| 63 | red | red | 0.7393 | True | True | correct |
| 64 | red | red | 0.7772 | True | True | correct |
| 65 | red | red | 0.8052 | True | True | correct |
| 66 | red | red | 0.8280 | True | True | correct |
| 67 | red | red | 0.8072 | True | True | correct |
| 68 | red | red | 0.8843 | True | True | correct |
| 69 | red | red | 0.8867 | True | True | correct |
| 7 | green | green | 0.7355 | True | True | correct |
| 70 | red | red | 0.8607 | True | True | correct |
| 71 | off | off | 0.3083 | False | True | poor_localization (IoU < 0.5) |
| 72 | off | off | 0.0000 | False | False | correct (no detection) |
| 73 | off | off | 0.0000 | False | False | correct (no detection) |
| 74 | off | off | 0.0000 | False | False | correct (no detection) |
| 75 | off | off | 0.0000 | False | False | correct (no detection) |
| 76 | off | off | 0.0000 | False | False | correct (no detection) |
| 77 | off | off | 0.0000 | False | False | correct (no detection) |
| 78 | off | off | 0.0000 | False | False | correct (no detection) |
| 79 | off | off | 0.0000 | False | False | correct (no detection) |
| 8 | green | green | 0.6399 | True | True | correct |
| 80 | off | off | 0.0000 | False | False | correct (no detection) |
| 81 | off | off | 0.0000 | False | False | correct (no detection) |
| 82 | off | off | 0.0000 | False | False | correct (no detection) |
| 83 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 84 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 85 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 86 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 87 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 88 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 89 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 9 | green | green | 0.6002 | True | True | correct |
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
