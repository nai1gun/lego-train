# Traffic Light Detection Benchmark Report
## Metadata

| Field | Value |
|-------|-------|
| Generated at | 2026-09-26T18:47:51.814706 |
| Git commit   | `5c0b074e1ec6` |

## Dataset Overview

- **Total frames**: 18
- **Ground truth with bbox**: 18
- **Ground truth without bbox**: 0
- **Housing detected**: 18
- **Housing missed as GT**: 0

## Overall Metrics

| Metric | Value |
|--------|-------|
| Phase Accuracy | 61.1% (11/18) |
| Localization Accuracy | 77.8% (14/18) |
| Mean IoU | 0.6756 |
| Median IoU | 0.6877 |
| IoU Std Dev | 0.2258 |
| IoU Range | [0.1683, 0.9468] |
| IoU P50 | 0.6877 |
| IoU P90 | 0.9098 |
| IoU P95 | 0.9190 |
| Avg Detection Time | 14.49 ms |

## Per-Phase Breakdown

| Phase | Count | Phase Accuracy | Mean IoU | Median IoU | Min IoU | Max IoU |
|-------|-------|----------------|----------|------------|---------|---------|
| green | 4 | 75.0% | 0.6819 | 0.6853 | 0.4725 | 0.8845 |
| green,red,yellow | 1 | 100.0% | 0.9080 | 0.9080 | 0.9080 | 0.9080 |
| off | 4 | 0.0% | 0.5488 | 0.5565 | 0.1683 | 0.9141 |
| red | 5 | 80.0% | 0.6578 | 0.6195 | 0.3020 | 0.9468 |
| red,yellow | 3 | 66.7% | 0.7246 | 0.6387 | 0.6346 | 0.9006 |
| yellow | 1 | 100.0% | 0.8676 | 0.8676 | 0.8676 | 0.8676 |

## Failure Modes

| Failure Mode | Count | Percentage |
|--------------|-------|------------|
| correct | 11 | 61.1% |
| poor_localization (IoU < 0.5) | 4 | 22.2% |
| phase_mismatch (GT={'off'}, pred=set()) | 2 | 11.1% |
| phase_mismatch (GT={'yellow', 'red'}, pred={'yellow', 'red', 'green'}) | 1 | 5.6% |

## Per-Lamp Accuracy

| Lamp | Correct | Total | Accuracy |
|------|---------|-------|----------|
| green | 15 | 18 | 83.3% |
| red | 17 | 18 | 94.4% |
| yellow | 18 | 18 | 100.0% |

## Per-Frame Results

| Frame | GT Phases | Predicted | IoU | Localization Correct | Housing Found | Failure Mode |
|-------|-----------|-----------|-----|---------------------|---------------|--------------|
| 103 | red | red | 0.5536 | True | True | correct |
| 104 | off | off | 0.9141 | True | True | phase_mismatch (GT={'off'}, pred=set()) |
| 105 | off | off | 0.1683 | False | True | poor_localization (IoU < 0.5) |
| 106 | red | green | 0.3020 | False | True | poor_localization (IoU < 0.5) |
| 107 | red | red | 0.8673 | True | True | correct |
| 108 | red | red | 0.6195 | True | True | correct |
| 109 | red,yellow | red,yellow | 0.6346 | True | True | correct |
| 110 | red,yellow | red,yellow | 0.6387 | True | True | correct |
| 111 | red,yellow | green,red,yellow | 0.9006 | True | True | phase_mismatch (GT={'yellow', 'red'}, pred={'yellow', 'red', 'green'}) |
| 112 | green,red,yellow | green,red,yellow | 0.9080 | True | True | correct |
| 113 | green | green | 0.8845 | True | True | correct |
| 114 | green | green | 0.7659 | True | True | correct |
| 115 | off | off | 0.7367 | True | True | phase_mismatch (GT={'off'}, pred=set()) |
| 116 | off | off | 0.3762 | False | True | poor_localization (IoU < 0.5) |
| 117 | green | off | 0.4725 | False | True | poor_localization (IoU < 0.5) |
| 118 | green | green | 0.6046 | True | True | correct |
| 119 | yellow | yellow | 0.8676 | True | True | correct |
| 120 | red | red | 0.9468 | True | True | correct |
