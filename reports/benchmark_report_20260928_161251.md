# Traffic Light Detection Benchmark Report
## Metadata

| Field | Value |
|-------|-------|
| Generated at | 2026-10-09T14:47:21.085152 |
| Git commit   | `650727a18979` |

## Dataset Overview

- **Total frames**: 86
- **Ground truth with bbox**: 56
- **Ground truth without bbox**: 30
- **Housing detected**: 44
- **Housing missed as GT**: 12

## Overall Metrics

| Metric | Value |
|--------|-------|
| Phase Accuracy | 87.2% (75/86) |
| Localization Accuracy | 44.2% (38/86) |
| Mean IoU | 0.4627 |
| Median IoU | 0.6187 |
| IoU Std Dev | 0.3294 |
| IoU Range | [0.0000, 0.9594] |
| IoU P50 | 0.6187 |
| IoU P90 | 0.7958 |
| IoU P95 | 0.8421 |
| Avg Detection Time | 10.08 ms |

## Per-Phase Breakdown

| Phase | Count | Phase Accuracy | Mean IoU | Median IoU | Min IoU | Max IoU |
|-------|-------|----------------|----------|------------|---------|---------|
| green | 14 | 78.6% | 0.7845 | 0.7822 | 0.6475 | 0.9594 |
| off | 37 | 100.0% | 0.6495 | 0.6495 | 0.6495 | 0.6495 |
| red | 26 | 80.8% | 0.5809 | 0.6141 | 0.0014 | 0.7226 |
| red,yellow | 9 | 66.7% | 0.7389 | 0.7536 | 0.6409 | 0.8108 |

## Failure Modes

| Failure Mode | Count | Percentage |
|--------------|-------|------------|
| correct | 37 | 43.0% |
| correct (no detection) | 27 | 31.4% |
| false_negative (missed detection) | 12 | 14.0% |
| poor_localization (IoU < 0.5) | 6 | 7.0% |
| false_positive (phantom detection) | 3 | 3.5% |
| phase_mismatch (GT={'green'}, pred=set()) | 1 | 1.2% |

## Per-Lamp Accuracy

| Lamp | Correct | Total | Accuracy |
|------|---------|-------|----------|
| green | 82 | 86 | 95.3% |
| red | 78 | 86 | 90.7% |
| yellow | 82 | 86 | 95.3% |

## Per-Frame Results

| Frame | GT Phases | Predicted | IoU | Localization Correct | Housing Found | Failure Mode |
|-------|-----------|-----------|-----|---------------------|---------------|--------------|
| 121 | off | off | 0.0000 | False | False | correct (no detection) |
| 122 | off | off | 0.0000 | False | False | correct (no detection) |
| 123 | off | off | 0.0000 | False | False | correct (no detection) |
| 124 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 125 | off | off | 0.0000 | False | False | correct (no detection) |
| 126 | off | off | 0.0000 | False | False | correct (no detection) |
| 127 | off | off | 0.0000 | False | False | correct (no detection) |
| 128 | off | off | 0.0000 | False | False | correct (no detection) |
| 129 | off | off | 0.6495 | True | True | correct |
| 130 | off | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 131 | off | off | 0.0000 | False | False | false_negative (missed detection) |
| 132 | off | off | 0.0000 | False | False | false_negative (missed detection) |
| 133 | off | off | 0.0000 | False | False | false_negative (missed detection) |
| 134 | off | off | 0.0000 | False | False | false_negative (missed detection) |
| 135 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 136 | off | off | 0.0000 | False | False | false_negative (missed detection) |
| 137 | red | off | 0.0000 | False | False | false_negative (missed detection) |
| 138 | red | green,yellow | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 139 | red | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 140 | red | red | 0.5677 | True | True | correct |
| 141 | red | red | 0.5485 | True | True | correct |
| 142 | red | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 143 | red | red | 0.5982 | True | True | correct |
| 144 | red | red | 0.5572 | True | True | correct |
| 145 | red | red | 0.5684 | True | True | correct |
| 146 | red | red | 0.5313 | True | True | correct |
| 147 | red | red | 0.5635 | True | True | correct |
| 148 | red | red | 0.6141 | True | True | correct |
| 149 | red | red | 0.6233 | True | True | correct |
| 150 | red | red | 0.5760 | True | True | correct |
| 151 | red | red | 0.6415 | True | True | correct |
| 152 | red | red | 0.5844 | True | True | correct |
| 153 | red | red | 0.6377 | True | True | correct |
| 154 | red | red | 0.6380 | True | True | correct |
| 155 | red | red | 0.6467 | True | True | correct |
| 156 | red | red | 0.6437 | True | True | correct |
| 157 | red | red | 0.6316 | True | True | correct |
| 158 | red | red | 0.6662 | True | True | correct |
| 159 | red | red | 0.0014 | False | True | poor_localization (IoU < 0.5) |
| 160 | red | red | 0.6366 | True | True | correct |
| 161 | red | red | 0.7226 | True | True | correct |
| 162 | red,yellow | red,yellow | 0.6409 | True | True | correct |
| 163 | red,yellow | red,yellow | 0.7826 | True | True | correct |
| 164 | red,yellow | red,yellow | 0.6922 | True | True | correct |
| 165 | red,yellow | red,yellow | 0.8108 | True | True | correct |
| 166 | red,yellow | red,yellow | 0.7822 | True | True | correct |
| 167 | red,yellow | red,yellow | 0.7250 | True | True | correct |
| 168 | red,yellow | off | 0.0000 | False | False | false_negative (missed detection) |
| 169 | red,yellow | off | 0.0000 | False | False | false_negative (missed detection) |
| 170 | red,yellow | off | 0.0000 | False | False | false_negative (missed detection) |
| 171 | green | off | 0.0000 | False | False | false_negative (missed detection) |
| 172 | green | off | 0.0000 | False | False | false_negative (missed detection) |
| 173 | green | green | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 174 | green | green | 0.7014 | True | True | correct |
| 175 | green | green | 0.8091 | True | True | correct |
| 176 | green | green | 0.8416 | True | True | correct |
| 177 | green | green | 0.9055 | True | True | correct |
| 178 | green | green | 0.9594 | True | True | correct |
| 179 | green | green | 0.6475 | True | True | correct |
| 180 | green | green | 0.7170 | True | True | correct |
| 181 | green | green | 0.7822 | True | True | correct |
| 182 | green | green | 0.8438 | True | True | correct |
| 183 | green | green | 0.7151 | True | True | correct |
| 184 | green | off | 0.7074 | True | True | phase_mismatch (GT={'green'}, pred=set()) |
| 185 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 186 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 187 | off | off | 0.0000 | False | False | correct (no detection) |
| 188 | off | off | 0.0000 | False | False | correct (no detection) |
| 189 | off | off | 0.0000 | False | False | correct (no detection) |
| 190 | off | off | 0.0000 | False | False | correct (no detection) |
| 191 | off | off | 0.0000 | False | False | correct (no detection) |
| 192 | off | off | 0.0000 | False | False | correct (no detection) |
| 193 | off | off | 0.0000 | False | False | correct (no detection) |
| 194 | off | off | 0.0000 | False | False | correct (no detection) |
| 195 | off | off | 0.0000 | False | False | correct (no detection) |
| 196 | off | off | 0.0000 | False | False | correct (no detection) |
| 197 | off | off | 0.0000 | False | False | correct (no detection) |
| 198 | off | off | 0.0000 | False | False | correct (no detection) |
| 199 | off | off | 0.0000 | False | False | correct (no detection) |
| 200 | off | off | 0.0000 | False | False | correct (no detection) |
| 201 | off | off | 0.0000 | False | False | correct (no detection) |
| 202 | off | off | 0.0000 | False | False | correct (no detection) |
| 203 | off | off | 0.0000 | False | False | correct (no detection) |
| 204 | off | off | 0.0000 | False | False | correct (no detection) |
| 205 | off | off | 0.0000 | False | False | correct (no detection) |
| 206 | off | off | 0.0000 | False | False | correct (no detection) |
