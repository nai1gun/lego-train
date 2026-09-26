# Traffic Light Detection Benchmark Report
## Metadata

| Field | Value |
|-------|-------|
| Generated at | 2026-09-26T22:40:15.763695 |
| Git commit   | `68957f394e0a` |

## Dataset Overview

- **Total frames**: 18
- **Ground truth with bbox**: 18
- **Ground truth without bbox**: 0
- **Housing detected**: 18
- **Housing missed as GT**: 0

## Overall Metrics

| Metric | Value |
|--------|-------|
| Phase Accuracy | 77.8% (14/18) |
| Localization Accuracy | 72.2% (13/18) |
| Mean IoU | 0.6433 |
| Median IoU | 0.6367 |
| IoU Std Dev | 0.2373 |
| IoU Range | [0.1683, 0.9468] |
| IoU P50 | 0.6367 |
| IoU P90 | 0.9098 |
| IoU P95 | 0.9190 |
| Avg Detection Time | 14.26 ms |

## Per-Phase Breakdown

| Phase | Count | Phase Accuracy | Mean IoU | Median IoU | Min IoU | Max IoU |
|-------|-------|----------------|----------|------------|---------|---------|
| green | 4 | 75.0% | 0.6519 | 0.6853 | 0.3528 | 0.8845 |
| green,red,yellow | 1 | 100.0% | 0.9080 | 0.9080 | 0.9080 | 0.9080 |
| off | 4 | 100.0% | 0.5307 | 0.5201 | 0.1683 | 0.9141 |
| red | 5 | 60.0% | 0.5800 | 0.5536 | 0.3020 | 0.9468 |
| red,yellow | 3 | 66.7% | 0.7246 | 0.6387 | 0.6346 | 0.9006 |
| yellow | 1 | 100.0% | 0.8676 | 0.8676 | 0.8676 | 0.8676 |

## Failure Modes

| Failure Mode | Count | Percentage |
|--------------|-------|------------|
| correct | 12 | 66.7% |
| poor_localization (IoU < 0.5) | 5 | 27.8% |
| phase_mismatch (GT={'red', 'yellow'}, pred={'red', 'yellow', 'green'}) | 1 | 5.6% |

## Per-Lamp Accuracy

| Lamp | Correct | Total | Accuracy |
|------|---------|-------|----------|
| green | 14 | 18 | 77.8% |
| red | 16 | 18 | 88.9% |
| yellow | 17 | 18 | 94.4% |

## Per-Frame Results

| Frame | GT Phases | Predicted | IoU | Localization Correct | Housing Found | Failure Mode |
|-------|-----------|-----------|-----|---------------------|---------------|--------------|
| 103 | red | red | 0.5536 | True | True | correct |
| 104 | off | off | 0.9141 | True | True | correct |
| 105 | off | off | 0.1683 | False | True | poor_localization (IoU < 0.5) |
| 106 | red | green | 0.3020 | False | True | poor_localization (IoU < 0.5) |
| 107 | red | green,yellow | 0.4783 | False | True | poor_localization (IoU < 0.5) |
| 108 | red | red | 0.6195 | True | True | correct |
| 109 | red,yellow | red,yellow | 0.6346 | True | True | correct |
| 110 | red,yellow | red,yellow | 0.6387 | True | True | correct |
| 111 | red,yellow | green,red,yellow | 0.9006 | True | True | phase_mismatch (GT={'red', 'yellow'}, pred={'red', 'yellow', 'green'}) |
| 112 | green,red,yellow | green,red,yellow | 0.9080 | True | True | correct |
| 113 | green | green | 0.8845 | True | True | correct |
| 114 | green | green | 0.7659 | True | True | correct |
| 115 | off | off | 0.7367 | True | True | correct |
| 116 | off | off | 0.3035 | False | True | poor_localization (IoU < 0.5) |
| 117 | green | off | 0.3528 | False | True | poor_localization (IoU < 0.5) |
| 118 | green | green | 0.6046 | True | True | correct |
| 119 | yellow | yellow | 0.8676 | True | True | correct |
| 120 | red | red | 0.9468 | True | True | correct |
