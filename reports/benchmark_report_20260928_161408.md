# Traffic Light Detection Benchmark Report
## Metadata

| Field | Value |
|-------|-------|
| Generated at | 2026-10-08T18:57:13.167684 |
| Git commit   | `19df6895842c` |

## Dataset Overview

- **Total frames**: 84
- **Ground truth with bbox**: 60
- **Ground truth without bbox**: 24
- **Housing detected**: 58
- **Housing missed as GT**: 2

## Overall Metrics

| Metric | Value |
|--------|-------|
| Phase Accuracy | 85.7% (72/84) |
| Localization Accuracy | 56.0% (47/84) |
| Mean IoU | 0.5781 |
| Median IoU | 0.6072 |
| IoU Std Dev | 0.2924 |
| IoU Range | [0.0000, 0.9395] |
| IoU P50 | 0.6072 |
| IoU P90 | 0.9019 |
| IoU P95 | 0.9269 |
| Avg Detection Time | 12.43 ms |

## Per-Phase Breakdown

| Phase | Count | Phase Accuracy | Mean IoU | Median IoU | Min IoU | Max IoU |
|-------|-------|----------------|----------|------------|---------|---------|
| green | 25 | 84.0% | 0.7012 | 0.7171 | 0.5574 | 0.8428 |
| off | 46 | 100.0% | 0.5373 | 0.5193 | 0.4834 | 0.6837 |
| red | 4 | 100.0% | 0.7962 | 0.8336 | 0.5909 | 0.9268 |
| red,yellow | 1 | 100.0% | 0.9296 | 0.9296 | 0.9296 | 0.9296 |
| yellow | 8 | 0.0% | 0.9063 | 0.9058 | 0.8555 | 0.9395 |

## Failure Modes

| Failure Mode | Count | Percentage |
|--------------|-------|------------|
| correct | 39 | 46.4% |
| correct (no detection) | 22 | 26.2% |
| poor_localization (IoU < 0.5) | 11 | 13.1% |
| phase_mismatch (GT={'yellow'}, pred={'green', 'yellow'}) | 8 | 9.5% |
| false_negative (missed detection) | 2 | 2.4% |
| false_positive (phantom detection) | 2 | 2.4% |

## Per-Lamp Accuracy

| Lamp | Correct | Total | Accuracy |
|------|---------|-------|----------|
| green | 72 | 84 | 85.7% |
| red | 84 | 84 | 100.0% |
| yellow | 84 | 84 | 100.0% |

## Per-Frame Results

| Frame | GT Phases | Predicted | IoU | Localization Correct | Housing Found | Failure Mode |
|-------|-----------|-----------|-----|---------------------|---------------|--------------|
| 207 | off | off | 0.5589 | True | True | correct |
| 208 | off | off | 0.5396 | True | True | correct |
| 209 | off | off | 0.5044 | True | True | correct |
| 210 | off | off | 0.4857 | False | True | poor_localization (IoU < 0.5) |
| 211 | off | off | 0.5375 | True | True | correct |
| 212 | off | off | 0.5196 | True | True | correct |
| 213 | off | off | 0.5190 | True | True | correct |
| 214 | off | off | 0.4834 | False | True | poor_localization (IoU < 0.5) |
| 215 | off | off | 0.4916 | False | True | poor_localization (IoU < 0.5) |
| 216 | off | off | 0.5132 | True | True | correct |
| 217 | off | off | 0.5083 | True | True | correct |
| 218 | off | off | 0.5190 | True | True | correct |
| 219 | off | off | 0.5576 | True | True | correct |
| 220 | off | off | 0.6089 | True | True | correct |
| 221 | off | off | 0.5669 | True | True | correct |
| 222 | off | off | 0.6837 | True | True | correct |
| 223 | off | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 224 | off | off | 0.0000 | False | False | false_negative (missed detection) |
| 225 | off | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 226 | off | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 227 | off | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 228 | off | off | 0.0000 | False | False | false_negative (missed detection) |
| 229 | green | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 230 | green | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 231 | green | green | 0.5763 | True | True | correct |
| 232 | green | green | 0.5574 | True | True | correct |
| 233 | green | green | 0.5646 | True | True | correct |
| 234 | green | green | 0.5816 | True | True | correct |
| 235 | green | green | 0.6332 | True | True | correct |
| 236 | green | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 237 | green | green | 0.6054 | True | True | correct |
| 238 | green | off | 0.0000 | False | True | poor_localization (IoU < 0.5) |
| 239 | green | green | 0.6502 | True | True | correct |
| 240 | green | green | 0.7153 | True | True | correct |
| 241 | green | green | 0.7396 | True | True | correct |
| 242 | green | green | 0.6878 | True | True | correct |
| 243 | green | green | 0.6718 | True | True | correct |
| 244 | green | green | 0.7253 | True | True | correct |
| 245 | green | green | 0.7537 | True | True | correct |
| 246 | green | green | 0.7171 | True | True | correct |
| 247 | green | green | 0.7380 | True | True | correct |
| 248 | green | green | 0.7709 | True | True | correct |
| 249 | green | green | 0.7821 | True | True | correct |
| 250 | green | green | 0.7808 | True | True | correct |
| 251 | green | green | 0.7979 | True | True | correct |
| 252 | green | green | 0.8428 | True | True | correct |
| 253 | green | green | 0.8343 | True | True | correct |
| 254 | yellow | green,yellow | 0.8555 | True | True | phase_mismatch (GT={'yellow'}, pred={'green', 'yellow'}) |
| 255 | yellow | green,yellow | 0.8800 | True | True | phase_mismatch (GT={'yellow'}, pred={'green', 'yellow'}) |
| 256 | yellow | green,yellow | 0.9009 | True | True | phase_mismatch (GT={'yellow'}, pred={'green', 'yellow'}) |
| 257 | yellow | green,yellow | 0.8986 | True | True | phase_mismatch (GT={'yellow'}, pred={'green', 'yellow'}) |
| 258 | yellow | green,yellow | 0.9261 | True | True | phase_mismatch (GT={'yellow'}, pred={'green', 'yellow'}) |
| 259 | yellow | green,yellow | 0.9395 | True | True | phase_mismatch (GT={'yellow'}, pred={'green', 'yellow'}) |
| 260 | yellow | green,yellow | 0.9389 | True | True | phase_mismatch (GT={'yellow'}, pred={'green', 'yellow'}) |
| 261 | yellow | green,yellow | 0.9107 | True | True | phase_mismatch (GT={'yellow'}, pred={'green', 'yellow'}) |
| 262 | red,yellow | red,yellow | 0.9296 | True | True | correct |
| 263 | red | red | 0.9268 | True | True | correct |
| 264 | red | red | 0.8653 | True | True | correct |
| 265 | red | red | 0.8019 | True | True | correct |
| 266 | red | red | 0.5909 | True | True | correct |
| 267 | off | off | 0.0000 | False | False | correct (no detection) |
| 268 | off | off | 0.0000 | False | False | correct (no detection) |
| 269 | off | off | 0.0000 | False | False | correct (no detection) |
| 270 | off | off | 0.0000 | False | False | correct (no detection) |
| 271 | off | off | 0.0000 | False | False | correct (no detection) |
| 272 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 273 | off | off | 0.0000 | False | False | correct (no detection) |
| 274 | off | off | 0.0000 | False | False | correct (no detection) |
| 275 | off | off | 0.0000 | False | False | correct (no detection) |
| 276 | off | off | 0.0000 | False | False | correct (no detection) |
| 277 | off | off | 0.0000 | False | True | false_positive (phantom detection) |
| 278 | off | off | 0.0000 | False | False | correct (no detection) |
| 279 | off | off | 0.0000 | False | False | correct (no detection) |
| 280 | off | off | 0.0000 | False | False | correct (no detection) |
| 281 | off | off | 0.0000 | False | False | correct (no detection) |
| 282 | off | off | 0.0000 | False | False | correct (no detection) |
| 283 | off | off | 0.0000 | False | False | correct (no detection) |
| 284 | off | off | 0.0000 | False | False | correct (no detection) |
| 285 | off | off | 0.0000 | False | False | correct (no detection) |
| 286 | off | off | 0.0000 | False | False | correct (no detection) |
| 287 | off | off | 0.0000 | False | False | correct (no detection) |
| 288 | off | off | 0.0000 | False | False | correct (no detection) |
| 289 | off | off | 0.0000 | False | False | correct (no detection) |
| 290 | off | off | 0.0000 | False | False | correct (no detection) |
