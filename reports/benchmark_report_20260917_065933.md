# Traffic Light Detection Benchmark Report
## Metadata

| Field | Value |
|-------|-------|
| Generated at | 2026-09-26T22:40:34.354188 |
| Git commit   | `68957f394e0a` |

## Dataset Overview

- **Total frames**: 102
- **Ground truth with bbox**: 71
- **Ground truth without bbox**: 31
- **Housing detected**: 68
- **Housing missed as GT**: 3

## Overall Metrics

| Metric | Value |
|--------|-------|
| Phase Accuracy | 94.1% (96/102) |
| Localization Accuracy | 56.9% (58/102) |
| Mean IoU | 0.7545 |
| Median IoU | 0.8936 |
| IoU Std Dev | 0.2873 |
| IoU Range | [0.0000, 0.9711] |
| IoU P50 | 0.8936 |
| IoU P90 | 0.9426 |
| IoU P95 | 0.9508 |
| Avg Detection Time | 12.18 ms |

## Per-Phase Breakdown

| Phase | Count | Phase Accuracy | Mean IoU | Median IoU | Min IoU | Max IoU |
|-------|-------|----------------|----------|------------|---------|---------|
| green | 37 | 83.8% | 0.7310 | 0.8936 | 0.0304 | 0.9711 |
| off | 34 | 100.0% | 0.4003 | 0.4003 | 0.2596 | 0.5411 |
| red | 31 | 100.0% | 0.8769 | 0.9024 | 0.6228 | 0.9508 |

## Failure Modes

| Failure Mode | Count | Percentage |
|--------------|-------|------------|
| correct | 57 | 55.9% |
| correct (no detection) | 28 | 27.5% |
| poor_localization (IoU < 0.5) | 10 | 9.8% |
| false_positive (phantom detection) | 3 | 2.9% |
| false_negative (missed detection) | 3 | 2.9% |
| phase_mismatch (GT={'green'}, pred={'green', 'yellow'}) | 1 | 1.0% |

## Per-Lamp Accuracy

| Lamp | Correct | Total | Accuracy |
|------|---------|-------|----------|
| green | 97 | 102 | 95.1% |
| red | 102 | 102 | 100.0% |
| yellow | 101 | 102 | 99.0% |

## Per-Frame Results

| Frame | GT Phases | Predicted | IoU | Localization Correct | Housing Found | Failure Mode |
|-------|-----------|-----------|-----|---------------------|---------------|--------------|
| 1 | green | green | 0.3612 | False | True | poor_localization (IoU < 0.5) |
| 10 | green | green | 0.9100 | True | True | correct |
| 100 | off | off | 0.0000 | False | False | correct (no detection) |
| 101 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 102 | off | off | 0.0000 | False | False | correct (no detection) |
| 11 | green | green | 0.9104 | True | True | correct |
| 12 | green | green | 0.8775 | True | True | correct |
| 13 | green | green | 0.8708 | True | True | correct |
| 14 | green | green | 0.9038 | True | True | correct |
| 15 | green | green | 0.8913 | True | True | correct |
| 16 | green | green | 0.8798 | True | True | correct |
| 17 | green | green | 0.9261 | True | True | correct |
| 18 | green | green | 0.9375 | True | True | correct |
| 19 | green | green | 0.9399 | True | True | correct |
| 2 | green | green | 0.2861 | False | True | poor_localization (IoU < 0.5) |
| 20 | green | green | 0.9373 | True | True | correct |
| 21 | green | green | 0.9159 | True | True | correct |
| 22 | green | green | 0.9266 | True | True | correct |
| 23 | green | green | 0.9711 | True | True | correct |
| 24 | green | green | 0.9637 | True | True | correct |
| 25 | green | green | 0.9240 | True | True | correct |
| 26 | green | green | 0.9509 | True | True | correct |
| 27 | green | green | 0.9655 | True | True | correct |
| 28 | green | green | 0.9124 | True | True | correct |
| 29 | green | green | 0.9077 | True | True | correct |
| 3 | green | green | 0.3024 | False | True | poor_localization (IoU < 0.5) |
| 30 | green | green | 0.8936 | True | True | correct |
| 31 | green | green | 0.8751 | True | True | correct |
| 32 | green | off | 0.2676 | False | True | poor_localization (IoU < 0.5) |
| 33 | green | green,yellow | 0.6115 | True | True | phase_mismatch (GT={'green'}, pred={'green', 'yellow'}) |
| 34 | green | off | 0.0304 | False | True | poor_localization (IoU < 0.5) |
| 35 | green | off | 0.0313 | False | True | poor_localization (IoU < 0.5) |
| 36 | green | off | 0.0000 | False | False | false_negative (missed detection) |
| 37 | green | off | 0.0000 | False | False | false_negative (missed detection) |
| 38 | off | off | 0.0000 | False | False | false_negative (missed detection) |
| 39 | off | off | 0.2596 | False | True | poor_localization (IoU < 0.5) |
| 4 | green | green | 0.2906 | False | True | poor_localization (IoU < 0.5) |
| 40 | red | red | 0.8708 | True | True | correct |
| 41 | red | red | 0.8409 | True | True | correct |
| 42 | red | red | 0.8972 | True | True | correct |
| 43 | red | red | 0.9040 | True | True | correct |
| 44 | red | red | 0.8416 | True | True | correct |
| 45 | red | red | 0.8916 | True | True | correct |
| 46 | red | red | 0.8601 | True | True | correct |
| 47 | red | red | 0.8884 | True | True | correct |
| 48 | red | red | 0.8827 | True | True | correct |
| 49 | red | red | 0.9024 | True | True | correct |
| 5 | green | green | 0.2843 | False | True | poor_localization (IoU < 0.5) |
| 50 | red | red | 0.9261 | True | True | correct |
| 51 | red | red | 0.9372 | True | True | correct |
| 52 | red | red | 0.9219 | True | True | correct |
| 53 | red | red | 0.9412 | True | True | correct |
| 54 | red | red | 0.9264 | True | True | correct |
| 55 | red | red | 0.9302 | True | True | correct |
| 56 | red | red | 0.9426 | True | True | correct |
| 57 | red | red | 0.9495 | True | True | correct |
| 58 | red | red | 0.9069 | True | True | correct |
| 59 | red | red | 0.9508 | True | True | correct |
| 6 | green | green | 0.3150 | False | True | poor_localization (IoU < 0.5) |
| 60 | red | red | 0.9253 | True | True | correct |
| 61 | red | red | 0.9471 | True | True | correct |
| 62 | red | red | 0.9133 | True | True | correct |
| 63 | red | red | 0.9318 | True | True | correct |
| 64 | red | red | 0.8961 | True | True | correct |
| 65 | red | red | 0.8653 | True | True | correct |
| 66 | red | red | 0.8361 | True | True | correct |
| 67 | red | red | 0.8588 | True | True | correct |
| 68 | red | red | 0.6396 | True | True | correct |
| 69 | red | red | 0.6355 | True | True | correct |
| 7 | green | green | 0.8293 | True | True | correct |
| 70 | red | red | 0.6228 | True | True | correct |
| 71 | off | off | 0.5411 | True | True | correct |
| 72 | off | off | 0.0000 | False | False | correct (no detection) |
| 73 | off | off | 0.0000 | False | False | correct (no detection) |
| 74 | off | off | 0.0000 | False | False | correct (no detection) |
| 75 | off | off | 0.0000 | False | False | correct (no detection) |
| 76 | off | off | 0.0000 | False | False | correct (no detection) |
| 77 | off | off | 0.0000 | False | False | correct (no detection) |
| 78 | off | off | 0.0000 | False | False | correct (no detection) |
| 79 | off | off | 0.0000 | False | False | correct (no detection) |
| 8 | green | green | 0.9334 | True | True | correct |
| 80 | off | off | 0.0000 | False | False | correct (no detection) |
| 81 | off | off | 0.0000 | False | False | correct (no detection) |
| 82 | off | off | 0.0000 | False | False | correct (no detection) |
| 83 | off | off | 0.0000 | False | False | correct (no detection) |
| 84 | off | off | 0.0000 | False | False | correct (no detection) |
| 85 | off | off | 0.0000 | False | False | correct (no detection) |
| 86 | off | off | 0.0000 | False | False | correct (no detection) |
| 87 | off | off | 0.0000 | False | False | correct (no detection) |
| 88 | off | off | 0.0000 | False | False | correct (no detection) |
| 89 | off | off | 0.0000 | False | False | correct (no detection) |
| 9 | green | green | 0.8522 | True | True | correct |
| 90 | off | off | 0.0000 | False | False | correct (no detection) |
| 91 | off | off | 0.0000 | False | False | correct (no detection) |
| 92 | off | off | 0.0000 | False | False | correct (no detection) |
| 93 | off | off | 0.0000 | False | False | correct (no detection) |
| 94 | off | off | 0.0000 | False | False | correct (no detection) |
| 95 | off | off | 0.0000 | False | False | correct (no detection) |
| 96 | off | off | 0.0000 | False | False | correct (no detection) |
| 97 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 98 | off | off | 0.0000 | False | False | correct (no detection) |
| 99 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
