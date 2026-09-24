# Traffic Light Detection Benchmark Report
## Metadata

| Field | Value |
|-------|-------|
| Generated at | 2026-09-24T19:24:24.735289 |
| Git commit   | `6e55efeb446d` |
| Resolution | 640x480 |
| FPS | 30 |
| Camera backend | picamera2 |
| Exposure (us) | 20000 |
| Analogue gain | 4.612612724304199 |
| HDR mode | HdrModeEnum.Off |
| NR mode | NoiseReductionModeEnum.Fast |
| Run note | round trip, speed 10% |

## Dataset Overview

- **Total frames**: 102
- **Ground truth with bbox**: 71
- **Ground truth without bbox**: 31
- **Housing detected**: 71
- **Housing missed as GT**: 0

## Overall Metrics

| Metric | Value |
|--------|-------|
| Phase Accuracy | 67.6% (69/102) |
| Localization Accuracy | 12.7% (13/102) |
| Mean IoU | 0.4187 |
| Median IoU | 0.4066 |
| IoU Std Dev | 0.1039 |
| IoU Range | [0.0000, 0.6053] |
| IoU P50 | 0.4066 |
| IoU P90 | 0.5421 |
| IoU P95 | 0.5630 |
| Avg Detection Time | 12.44 ms |

## Per-Phase Breakdown

| Phase | Count | Phase Accuracy | Mean IoU | Median IoU | Min IoU | Max IoU |
|-------|-------|----------------|----------|------------|---------|---------|
| green | 37 | 91.9% | 0.4100 | 0.4054 | 0.0454 | 0.5663 |
| off | 34 | 100.0% | 0.2835 | 0.2835 | 0.2588 | 0.3083 |
| red | 31 | 3.2% | 0.4513 | 0.4171 | 0.3603 | 0.6053 |

## Failure Modes

| Failure Mode | Count | Percentage |
|--------------|-------|------------|
| poor_localization (IoU < 0.5) | 58 | 56.9% |
| false_positive (phantom detection) | 20 | 19.6% |
| correct (no detection) | 11 | 10.8% |
| correct | 7 | 6.9% |
| phase_mismatch (GT=red, pred=red_yellow) | 6 | 5.9% |

## Per-Frame Results

| Frame | GT Phase | Predicted | IoU | Localization Correct | Housing Found | Failure Mode |
|-------|----------|-----------|-----|---------------------|---------------|--------------|
| 1 | green | green | 0.4138 | False | True | poor_localization (IoU < 0.5) |
| 10 | green | green | 0.3739 | False | True | poor_localization (IoU < 0.5) |
| 100 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 101 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 102 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 11 | green | green | 0.3944 | False | True | poor_localization (IoU < 0.5) |
| 12 | green | green | 0.3887 | False | True | poor_localization (IoU < 0.5) |
| 13 | green | green | 0.3727 | False | True | poor_localization (IoU < 0.5) |
| 14 | green | green | 0.3851 | False | True | poor_localization (IoU < 0.5) |
| 15 | green | green | 0.3982 | False | True | poor_localization (IoU < 0.5) |
| 16 | green | green | 0.4049 | False | True | poor_localization (IoU < 0.5) |
| 17 | green | green | 0.4054 | False | True | poor_localization (IoU < 0.5) |
| 18 | green | green | 0.4066 | False | True | poor_localization (IoU < 0.5) |
| 19 | green | green | 0.3985 | False | True | poor_localization (IoU < 0.5) |
| 2 | green | green | 0.3481 | False | True | poor_localization (IoU < 0.5) |
| 20 | green | green | 0.4112 | False | True | poor_localization (IoU < 0.5) |
| 21 | green | green | 0.4654 | False | True | poor_localization (IoU < 0.5) |
| 22 | green | green | 0.4448 | False | True | poor_localization (IoU < 0.5) |
| 23 | green | green | 0.4644 | False | True | poor_localization (IoU < 0.5) |
| 24 | green | green | 0.4891 | False | True | poor_localization (IoU < 0.5) |
| 25 | green | green | 0.4947 | False | True | poor_localization (IoU < 0.5) |
| 26 | green | green | 0.4659 | False | True | poor_localization (IoU < 0.5) |
| 27 | green | green | 0.4539 | False | True | poor_localization (IoU < 0.5) |
| 28 | green | green | 0.4737 | False | True | poor_localization (IoU < 0.5) |
| 29 | green | green | 0.5003 | True | True | correct |
| 3 | green | green | 0.3627 | False | True | poor_localization (IoU < 0.5) |
| 30 | green | green | 0.5143 | True | True | correct |
| 31 | green | green | 0.5204 | True | True | correct |
| 32 | green | green | 0.5421 | True | True | correct |
| 33 | green | green | 0.5597 | True | True | correct |
| 34 | green | green | 0.5663 | True | True | correct |
| 35 | green | off | 0.0454 | False | True | poor_localization (IoU < 0.5) |
| 36 | green | off | 0.1582 | False | True | poor_localization (IoU < 0.5) |
| 37 | green | off | 0.2689 | False | True | poor_localization (IoU < 0.5) |
| 38 | off | off | 0.2588 | False | True | poor_localization (IoU < 0.5) |
| 39 | off | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 4 | green | green | 0.3667 | False | True | poor_localization (IoU < 0.5) |
| 40 | red | red_yellow | 0.4052 | False | True | poor_localization (IoU < 0.5) |
| 41 | red | red_yellow | 0.3603 | False | True | poor_localization (IoU < 0.5) |
| 42 | red | red_yellow | 0.3609 | False | True | poor_localization (IoU < 0.5) |
| 43 | red | red_yellow | 0.3758 | False | True | poor_localization (IoU < 0.5) |
| 44 | red | red_yellow | 0.3886 | False | True | poor_localization (IoU < 0.5) |
| 45 | red | red_yellow | 0.4038 | False | True | poor_localization (IoU < 0.5) |
| 46 | red | red_yellow | 0.3944 | False | True | poor_localization (IoU < 0.5) |
| 47 | red | red_yellow | 0.3950 | False | True | poor_localization (IoU < 0.5) |
| 48 | red | red_yellow | 0.3902 | False | True | poor_localization (IoU < 0.5) |
| 49 | red | red_yellow | 0.3855 | False | True | poor_localization (IoU < 0.5) |
| 5 | green | green | 0.3860 | False | True | poor_localization (IoU < 0.5) |
| 50 | red | red_yellow | 0.3967 | False | True | poor_localization (IoU < 0.5) |
| 51 | red | red_yellow | 0.4088 | False | True | poor_localization (IoU < 0.5) |
| 52 | red | red_yellow | 0.4015 | False | True | poor_localization (IoU < 0.5) |
| 53 | red | red_yellow | 0.4065 | False | True | poor_localization (IoU < 0.5) |
| 54 | red | red_yellow | 0.4084 | False | True | poor_localization (IoU < 0.5) |
| 55 | red | red_yellow | 0.4171 | False | True | poor_localization (IoU < 0.5) |
| 56 | red | red_yellow | 0.4361 | False | True | poor_localization (IoU < 0.5) |
| 57 | red | red_yellow | 0.4605 | False | True | poor_localization (IoU < 0.5) |
| 58 | red | red_yellow | 0.4937 | False | True | poor_localization (IoU < 0.5) |
| 59 | red | red_yellow | 0.4563 | False | True | poor_localization (IoU < 0.5) |
| 6 | green | green | 0.3890 | False | True | poor_localization (IoU < 0.5) |
| 60 | red | red_yellow | 0.4666 | False | True | poor_localization (IoU < 0.5) |
| 61 | red | red_yellow | 0.4667 | False | True | poor_localization (IoU < 0.5) |
| 62 | red | red_yellow | 0.4793 | False | True | poor_localization (IoU < 0.5) |
| 63 | red | red_yellow | 0.4935 | False | True | poor_localization (IoU < 0.5) |
| 64 | red | red_yellow | 0.5112 | True | True | phase_mismatch (GT=red, pred=red_yellow) |
| 65 | red | red_yellow | 0.5345 | True | True | phase_mismatch (GT=red, pred=red_yellow) |
| 66 | red | red_yellow | 0.5501 | True | True | phase_mismatch (GT=red, pred=red_yellow) |
| 67 | red | red_yellow | 0.5554 | True | True | phase_mismatch (GT=red, pred=red_yellow) |
| 68 | red | red_yellow | 0.5970 | True | True | phase_mismatch (GT=red, pred=red_yellow) |
| 69 | red | red_yellow | 0.6053 | True | True | phase_mismatch (GT=red, pred=red_yellow) |
| 7 | green | green | 0.4222 | False | True | poor_localization (IoU < 0.5) |
| 70 | red | red | 0.5843 | True | True | correct |
| 71 | off | off | 0.3083 | False | True | poor_localization (IoU < 0.5) |
| 72 | off | off | 0.0000 | False | False | correct (no detection) |
| 73 | off | off | 0.0000 | False | False | correct (no detection) |
| 74 | off | off | 0.0000 | False | False | correct (no detection) |
| 75 | off | off | 0.0000 | False | False | correct (no detection) |
| 76 | off | off | 0.0000 | False | False | correct (no detection) |
| 77 | off | off | 0.0000 | False | False | correct (no detection) |
| 78 | off | off | 0.0000 | False | False | correct (no detection) |
| 79 | off | off | 0.0000 | False | False | correct (no detection) |
| 8 | green | green | 0.3659 | False | True | poor_localization (IoU < 0.5) |
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
| 9 | green | green | 0.3475 | False | True | poor_localization (IoU < 0.5) |
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
