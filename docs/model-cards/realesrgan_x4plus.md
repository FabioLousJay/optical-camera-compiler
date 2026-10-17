# Model Card: Real-ESRGAN (`RealESRGAN_x4plus` / `RealESRNet_x4plus`)

**Adapter Modules:** [`photonqc/backends.py`](../../photonqc/backends.py), [`photonqc/neural_sr.py`](../../photonqc/neural_sr.py), [`photonqc/licensing.py`](../../photonqc/licensing.py)

## 1. Architecture & Checkpoint Identity

- **Model Family**: RRDBNet (Residual-in-Residual Dense Block Network, 23 RRDB blocks, `num_feat=64`, `num_grow_ch=32`, `scale=4`).
- **Upstream Repository**: `https://github.com/xinntao/Real-ESRGAN`
- **Source License**: `BSD-3-Clause` (commercial use permitted; verify checkpoint redistribution terms independently).
- **Supported Execution Modes in PhotonQC**:
  1. **Official Subprocess Adapter (`--backend realesrgan`)**: Invokes `inference_realesrgan.py -n RealESRGAN_x4plus --model_path <weights> --outscale 4 --suffix sr --ext png --fp32` inside an isolated temporary directory.
  2. **Native PyTorch RRDBNet Adapter (`--backend realesrgan_native`)**: Loads the `.pth` state dictionary (`params_ema` / `params`) directly into [`photonqc.neural_sr.RRDBNet`](../../photonqc/neural_sr.py) with automatic Apple Silicon `mps`, `cuda`, or `cpu` device placement, overlap-padded tiled inference (`--tile-size`), and automatic OOM tile-halving fallback.

## 2. Governance & Non-Commercial Restriction Gate

[`photonqc/licensing.py`](../../photonqc/licensing.py) enforces a model governance gate before any neural backend initializes:
- `RealESRGAN_x4plus`, `RealESRNet_x4plus`, `SwinIR-M_x4`, and `HAT-S_x4` carry permissive open-source licenses (`BSD-3-Clause` / `Apache-2.0`).
- `SUPIR` carries a restrictive **Non-Commercial Research Only** license and is **blocked by default** (`PermissionError`) unless `allow_non_commercial=True` is explicitly passed for non-commercial research experiments.

## 3. Reproducible Weight Provisioning (Requires User Approval)

Per project governance, large model weights (`~64 MiB`) are never committed to Git or downloaded silently. After explicit approval:

```bash
git clone https://github.com/xinntao/Real-ESRGAN.git external/Real-ESRGAN
git -C external/Real-ESRGAN rev-parse HEAD
mkdir -p external/Real-ESRGAN/weights
curl -fL \
  https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth \
  -o external/Real-ESRGAN/weights/RealESRGAN_x4plus.pth
shasum -a 256 external/Real-ESRGAN/weights/RealESRGAN_x4plus.pth
```
