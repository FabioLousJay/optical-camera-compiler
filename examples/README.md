# Rights-Cleared Reference Imagery (`examples/`)

## `rights-cleared-example.png`

- **Dimensions**: `1024 × 1536` px (`2:3` aspect ratio, `1.5729 MP`)
- **Color Mode & Profile**: `RGB` PNG with embedded `sRGB built-in` ICC profile (`588` bytes)
- **Raster Density Metadata**: `300 PPI`
- **File Size**: `1,095,272` bytes (`1.044533 MiB`)
- **SHA-256**: `f957ee12f66741270ed7af40d9d6f0b30f002ad25f2deddca0893d3cc54a7efa`
- **Provenance & Rights**: 100% original procedural test image generated deterministically by [`photonqc/assets.py`](../photonqc/assets.py) (`generate_rights_cleared_heart_example`). Zero third-party copyright, trademark, or biometric privacy restrictions.

### Gold-Case Invariants Satisfied
1. **Frontal Orthographic Red Cubic Heart**: Zero yaw, pitch, or roll; strict byte-level horizontal bilateral symmetry (`bilateral_symmetry_iou = 1.0`, `horizontal_center_offset_ratio = 0.0`).
2. **Full-Frame Unclipped Subject & Pure Flat-Black Studio Perimeter**: Complete upper lobes, lateral flanks, and bottom tip contained inside the frame with generous bokeh margins (`full_frame_unclipped = True`), framed by an exact `#000000` outer studio border (`border_max_rgb = 0`, `exact_zero_fraction = 1.0`).
3. **Lossless Byte-Budget Compatibility**: Continuous-tone multi-depth optical bokeh and beveled cube highlights yield **`10.254 MiB`** at `4000 × 6000` (`realesrgan_antidrift`, `--min-mib 10 --max-mib 15`) and **`15.151 MiB`** at `4800 × 7200` (`16 × 24 in @ 300 PPI`, `--min-mib 8`) under lossless PNG encoding without artificial noise or padding.
