# Print Geometry, Color Management, and Exhibition Calibration

**Module:** [`photonqc/calibration.py`](../photonqc/calibration.py) & [`photonqc/sizing.py`](../photonqc/sizing.py)

## 1. Exact Print Geometry (`inches × PPI`)

Physical print preparation requires exact raster dimensions derived from physical print size and raster density in **Pixels Per Inch (PPI)** (distinct from printer halftone droplet density in DPI):

$$\text{width}_{\text{px}} = \text{round}\left(\text{width}_{\text{in}} \times \text{PPI}\right), \quad \text{height}_{\text{px}} = \text{round}\left(\text{height}_{\text{in}} \times \text{PPI}\right)$$

Implemented with exact `Decimal` arithmetic (`ROUND_HALF_UP`) in [`inches_to_pixels()`](../photonqc/sizing.py):
- `16 × 24 in @ 300 PPI` $\rightarrow$ **`4800 × 7200` px** (`34.56 MP`)
- `24 × 36 in @ 240 PPI` $\rightarrow$ **`5760 × 8640` px** (`49.77 MP`)
- **Strict Aspect-Ratio Guard**: If the source aspect ratio differs from the target aspect ratio by more than `0.2%`, [`check_aspect_ratio()`](../photonqc/sizing.py) raises a `ValueError` rather than stretching or silently cropping the image. Explicit cropping (`--crop-policy center-crop`) or padding (`--crop-policy pad-black`) must be opted into and is recorded in the provenance ledger.

---

## 2. Color Management: ICC Embedding vs. CMM Soft-Proofing

PhotonQC enforces a strict separation between **profile assignment/embedding** and **color space conversion**:

1. **ICC Profile Preservation**: When an RGB source image contains a valid embedded ICC profile (such as `sRGB built-in`), `photonqc export` preserves those exact profile bytes in the exported PNG (`icc_profile`) without altering pixel values.
2. **Measured LittleCMS2 Soft-Proofing (`color_managed_icc_cmm`)**: When a real destination printer/paper ICC profile file is supplied via `--destination-icc <path.icc>`, [`soft_proof_icc()`](../photonqc/calibration.py) executes genuine LittleCMS2 (`PIL.ImageCms`) color transformations comparing:
   - `RELATIVE_COLORIMETRIC` with Black Point Compensation (`BLACKPOINTCOMPENSATION`),
   - `RELATIVE_COLORIMETRIC` without BPC,
   - `PERCEPTUAL` with BPC,
   and quantifies the out-of-gamut pixel fraction and rendering-intent shift.
3. **Honest Planning Mode (`planning_only_no_measured_icc`)**: When only a paper preset name (`--profile matte_300ppi`, `glossy_300ppi`, `canvas_240ppi`, `baryta_300ppi`) is supplied without a physical lab ICC profile, the report explicitly sets `"calibration_mode": "planning_only_no_measured_icc"`. PhotonQC never applies arbitrary percentage contrast boosts pretending to be colorimetric calibration.

---

## 3. Print Media Profiles (`profiles/`)

| Profile ID | File | Target PPI | Expected $D_{\max}$ | Output Sharpening `(r, %, th)` |
| :--- | :--- | :--- | :--- | :--- |
| `matte_300ppi` | [`profiles/matte_300ppi.json`](../profiles/matte_300ppi.json) | 300 | `1.65 – 1.75` | `(0.85, 52%, 3)` |
| `glossy_300ppi` | [`profiles/glossy_300ppi.json`](../profiles/glossy_300ppi.json) | 300 | `2.40 – 2.65` | `(0.65, 35%, 4)` |
| `canvas_240ppi` | [`profiles/canvas_240ppi.json`](../profiles/canvas_240ppi.json) | 240 | `1.80 – 1.95` | `(1.10, 65%, 4)` |
| `baryta_300ppi` | [`profiles/baryta_300ppi.json`](../profiles/baryta_300ppi.json) | 300 | `2.60 – 2.75` | `(0.70, 40%, 3)` |

---

## 4. Multi-Print Exhibition Series Cohesion (`photonqc calibrate --series`)

When preparing a gallery sequence, [`evaluate_series_cohesion()`](../photonqc/calibration.py) audits candidate prints against an **anchor master print** across:
- Midtone luminance weight (`P50` median luminance),
- Deep shadow floor (`P05` luminance),
- Highlight rolloff (`P95` luminance),
- Mean chroma and red-green / blue-yellow neutral balance,
flagging outliers in an exception report without destructively equalizing individual print histograms.
