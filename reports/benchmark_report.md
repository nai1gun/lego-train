# Traffic Light Detection Benchmark Report
## Metadata

| Field | Value |
|-------|-------|
| Generated at | 2026-10-09T15:28:59.712671 |
| Git commit   | `650727a18979` |

## Dataset Overview

- **Total frames**: 284
- **Ground truth with bbox**: 199
- **Ground truth without bbox**: 85
- **Housing detected**: 182
- **Housing missed as GT**: 17

## Overall Metrics

| Metric | Value |
|--------|-------|
| Phase Accuracy | 91.5% (260/284) |
| Localization Accuracy | 54.9% (156/284) |
| Mean IoU | 0.6227 |
| Median IoU | 0.7014 |
| IoU Std Dev | 0.3191 |
| IoU Range | [0.0000, 0.9711] |
| IoU P50 | 0.7014 |
| IoU P90 | 0.9297 |
| IoU P95 | 0.9413 |
| Avg Detection Time | 10.37 ms |

## Per-Phase Breakdown

| Phase | Count | Phase Accuracy | Mean IoU | Median IoU | Min IoU | Max IoU |
|-------|-------|----------------|----------|------------|---------|---------|
| green | 74 | 81.1% | 0.7648 | 0.8091 | 0.0304 | 0.9711 |
| green,red,yellow | 1 | 100.0% | 0.9080 | 0.9080 | 0.9080 | 0.9080 |
| off | 121 | 100.0% | 0.5291 | 0.5196 | 0.1683 | 0.9141 |
| red | 66 | 89.4% | 0.7454 | 0.8361 | 0.0014 | 0.9508 |
| red,yellow | 13 | 76.9% | 0.7537 | 0.7536 | 0.6346 | 0.9296 |
| yellow | 9 | 100.0% | 0.9020 | 0.9009 | 0.8555 | 0.9395 |

## Failure Modes

| Failure Mode | Count | Percentage |
|--------------|-------|------------|
| correct | 154 | 54.2% |
| correct (no detection) | 77 | 27.1% |
| poor_localization (IoU < 0.5) | 26 | 9.2% |
| false_negative (missed detection) | 17 | 6.0% |
| false_positive (phantom detection) | 8 | 2.8% |
| phase_mismatch (GT={'green'}, pred={'green', 'yellow'}) | 1 | 0.4% |
| phase_mismatch (GT={'green'}, pred=set()) | 1 | 0.4% |

## Per-Lamp Accuracy

| Lamp | Correct | Total | Accuracy |
|------|---------|-------|----------|
| green | 268 | 284 | 94.4% |
| red | 274 | 284 | 96.5% |
| yellow | 278 | 284 | 97.9% |

## Per-Frame Results

| Frame | GT Phases | Predicted | IoU | Localization Correct | Housing Found | Failure Mode |
|-------|-----------|-----------|-----|---------------------|---------------|--------------|
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
| 103 | red | red | 0.5536 | True | True | correct |
| 104 | off | off | 0.9141 | True | True | correct |
| 105 | off | off | 0.1683 | False | True | poor_localization (IoU < 0.5) |
| 106 | red | green | 0.3020 | False | True | poor_localization (IoU < 0.5) |
| 107 | red | green,yellow | 0.4783 | False | True | poor_localization (IoU < 0.5) |
| 108 | red | red | 0.6195 | True | True | correct |
| 109 | red,yellow | red,yellow | 0.6346 | True | True | correct |
| 110 | red,yellow | red,yellow | 0.6387 | True | True | correct |
| 111 | red,yellow | red,yellow | 0.9006 | True | True | correct |
| 112 | green,red,yellow | green,red,yellow | 0.9080 | True | True | correct |
| 113 | green | green | 0.8845 | True | True | correct |
| 114 | green | green | 0.7659 | True | True | correct |
| 115 | off | off | 0.7367 | True | True | correct |
| 116 | off | off | 0.3035 | False | True | poor_localization (IoU < 0.5) |
| 117 | green | off | 0.3528 | False | True | poor_localization (IoU < 0.5) |
| 118 | green | green | 0.6046 | True | True | correct |
| 119 | yellow | yellow | 0.8676 | True | True | correct |
| 120 | red | red | 0.9468 | True | True | correct |
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
| 254 | yellow | yellow | 0.8555 | True | True | correct |
| 255 | yellow | yellow | 0.8800 | True | True | correct |
| 256 | yellow | yellow | 0.9009 | True | True | correct |
| 257 | yellow | yellow | 0.8986 | True | True | correct |
| 258 | yellow | yellow | 0.9261 | True | True | correct |
| 259 | yellow | yellow | 0.9395 | True | True | correct |
| 260 | yellow | yellow | 0.9389 | True | True | correct |
| 261 | yellow | yellow | 0.9107 | True | True | correct |
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
