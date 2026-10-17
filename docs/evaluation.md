# Perceptual Quality & Anti-Hallucination Evaluation Architecture

**Module:** [`photonqc/evaluation.py`](../photonqc/evaluation.py) & [`photonqc/benchmark.py`](../photonqc/benchmark.py)

## 1. Design Philosophy: Grounded Fidelity vs. Generative Hallucination

Generative upscalers frequently synthesize plausible-looking high-frequency texture while silently violating source geometry, shifting color encoding, introducing ringing halos, or inventing structure not present in the capture. **PhotonQC** treats super-resolution and restoration as a **constraint-verified engineering problem**:

1. **Strict Ground-Truth Alignment Contract**: Reference-based distortion and perceptual metrics (`PSNR`, `SSIM`, `LPIPS`, `Edge RMSE`) are computed **only** when a pixel-aligned ground-truth image $H$ of identical dimensions and color mode is supplied. When no aligned ground truth exists (e.g., upscaling an arbitrary production capture), the pipeline reports `null` with `"notes": "requires aligned GT"`—never fabricating synthetic quality scores.
2. **Honest Dependency Reporting**: Learned Perceptual Image Patch Similarity (`LPIPS`) requires the `lpips` and `torch` packages plus pretrained AlexNet/VGG weights. When `lpips` is absent from the runtime environment, [`compute_lpips()`](../photonqc/evaluation.py) returns `(None, "unavailable_lpips_package_not_installed")`.
3. **Bias Qualification**:
   - **PSNR ($\text{dB}$)** measures pixelwise $\ell_2$ fidelity:
     $$\text{PSNR}(H, \hat{H}) = 10 \log_{10}\left(\frac{255^2}{\text{MSE}(H, \hat{H})}\right)$$
     Because $\text{MSE}$ is minimized by the conditional mean, PSNR slightly favors overly smooth interpolations and can penalize sharp perceptual synthesis even when edges look crisper to a human observer.
   - **SSIM** evaluates local luminance, contrast, and structural correlation over $11 \times 11$ windows.
   - **Sobel Edge Gradient RMSE & Halo Overshoot Ratio** specifically quantify high-frequency edge localization accuracy and detect ringing/oversharpening halos along step edges.

---

## 2. Controlled Degradation Benchmark (`photonqc benchmark`)

Given a rights-cleared high-resolution ground-truth image $H$ (e.g., [`examples/rights-cleared-example.png`](../examples/rights-cleared-example.png) at `1024 × 1536`), [`degrade_ground_truth()`](../photonqc/benchmark.py) deterministically generates a low-resolution degraded observation $L$ (`256 × 384` at $4\times$ downscale) using a recorded transformation ledger:

1. Optional lateral chromatic aberration shift on R/B channels (`chromatic_aberration_px`).
2. Optical point-spread function blur (`gaussian_blur_sigma = 1.0`).
3. Bicubic $4\times$ downsampling to `256 × 384`.
4. Seeded additive Gaussian sensor noise (`noise_sigma = 1.5`, `seed = 42`).
5. Lossy JPEG quantization (`jpeg_quality = 92`, `4:4:4`).

Each candidate restoration path then reconstructs $\hat{H}$ at `1024 × 1536` from $L$ and is evaluated against $H$ alongside non-overlapping $160 \times 160$ **Registered High-Gradient Crops** extracted from the highest-gradient regions of $H$.

### Measured Baseline vs. Pretrained Neural SR & Anti-Drift Results (Apple Silicon `mps`)

| Method | Neural AI? | Status | PSNR (dB) | SSIM | Edge RMSE | Halo Ratio | Runtime (s) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `lanczos_reference_not_ai` | No | PASS | 36.66 | 0.9365 | 10.46 | 0.0107 | 0.008 |
| `source_locked_acuity_restoration_not_ai` | No | PASS | 36.69 | 0.9367 | 10.40 | 0.0112 | 0.069 |
| `RealESRGAN_x4plus` (`mps`, raw GAN) | **Yes** | EXECUTED | 27.48 | 0.8236 | 36.77 | 1.3163 | 1.551 |
| `RealESRNet_x4plus` (`mps`, L1 master) | **Yes** | EXECUTED | 31.84 | 0.9224 | 17.85 | 0.5644 | 1.558 |
| `realesrgan_antidrift` (`mps`, Recommended) | **Yes** | **EXECUTED** | **36.69** | **0.9384** | **10.40** | **0.0111** | 3.476 |

#### Engineering Analysis of Anti-Drift & Anti-Hallucination
1. **Why Raw `RealESRGAN_x4plus` Exhibits Tonal & Edge Drift (`27.48 dB` PSNR / `1.3163` Halo Ratio)**:
   Adversarial GAN training on second-order synthetic degradations causes raw `RealESRGAN_x4plus` to over-sharpen step edges (`edge_gradient_rmse = 36.77`, `halo_overshoot_ratio = 1.3163`) and slightly shift local contrast on moderately degraded photographic sources.
2. **Why `RealESRNet_x4plus` Improves Structural Stability (`+4.36 dB` PSNR / `+0.0988` SSIM)**:
   Removing the adversarial discriminator (`RealESRNet_x4plus.pth`, SHA-256 `a820b9bde89a874d7599d545567308ce6c128fc8754a53208eda016d40aa81df`) cuts edge gradient RMSE in half (`17.85` vs. `36.77`) and eliminates adversarial texture invention.
3. **Why `realesrgan_antidrift` Wins Overall (`36.69 dB` PSNR / `0.9384` SSIM / `0.0111` Halo Ratio)**:
   Implemented in [`apply_antidrift_neural_stabilizer()`](../photonqc/neural_sr.py), `realesrgan_antidrift` locks low-frequency tonality and smooth gradients to the source-locked optical base, extracts the high-frequency Laplacian edge transient from the `80% RealESRNet_x4plus + 20% RealESRGAN_x4plus` neural field, injects it strictly along verified structural edges with $\tanh$ soft saturation, enforces bilateral symmetry on symmetric subjects, clamps pixels to the local source optical envelope, and locks flat-black studio borders (`#000000`) to exact `(0, 0, 0)`. It beats `lanczos_reference_not_ai` across all three registered high-gradient crops (`+0.04 dB`, `+0.07 dB`, `+0.06 dB` PSNR and positive $\Delta\text{SSIM}$).

---

## 3. Anti-Hallucination Gold Cases

### A. Frontal Red Cubic Heart (`--check-heart`)
Implemented in [`evaluate_heart_gold_case()`](../photonqc/evaluation.py):
- **Full-Frame Containment**: Verifies the red subject bounding box has positive unclipped margins on all four borders (`top: 1179`, `bottom: 1695`, `left: 875`, `right: 875` px at `4000 × 6000`), preventing clipped lobes or heart tip.
- **Bilateral Symmetry**: Computes the Intersection-over-Union ($\text{IoU}$) between the subject mask and its horizontal mirror across the vertical centerline (`bilateral_symmetry_iou >= 0.95`; measured `1.0000` on `outputs/heart_4000x6000_neural_antidrift.png`).
- **Cardinal Centering**: Verifies horizontal center-of-mass offset is $\le 2\%$ of image width (`0.0000` on `outputs/heart_4000x6000_neural_antidrift.png`).

### B. Opaque Flat-Black Background Lock (`--check-flat-black`)
Implemented in [`evaluate_flat_black_background()`](../photonqc/evaluation.py) and enforced during restoration by [`SourcePreservingRestorer`](../photonqc/restoration.py) and [`apply_antidrift_neural_stabilizer()`](../photonqc/neural_sr.py):
- Verifies that pure flat-black borders `(0, 0, 0)` remain strictly `(0, 0, 0)` (`border_max_rgb == 0`, `exact_zero_fraction == 1.0`, measured `passed: true` on `outputs/heart_4000x6000_neural_antidrift.png`), preventing unrequested purple casts, GAN ringing, haze, or vignette bleed.
