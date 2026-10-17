# Cryptographic Provenance, Byte-Budget Integrity, and Supply-Chain Verification

**Module:** [`photonqc/report.py`](../photonqc/report.py), [`photonqc/export.py`](../photonqc/export.py), & [`photonqc/licensing.py`](../photonqc/licensing.py)

## 1. Anti-Fabrication & Truth-Labeling Rules

1. **Conventional Resampling vs. Neural Super-Resolution**:
   - Every CPU baseline export is explicitly labeled `"sr_backend": "lanczos_reference_not_ai"` with `"is_neural_ai": false`.
   - Real-ESRGAN (`--backend realesrgan` or `--backend realesrgan_native`) requires a verified `.pth` checkpoint on disk. If weights are omitted or missing, execution fails immediately with `ValueError` / `FileNotFoundError`—never falling back silently to Lanczos.
   - When Real-ESRGAN runs, the report records both the **native $4\times$ neural model output dimensions** and whether a **post-model conventional Lanczos resize** was applied to reach exact print dimensions:
     `real_esrgan_x4plus_fp32_native_{W}x{H}_final_lanczos_{True|False}`.
2. **Lossless PNG Byte-Budget Search Without Artificial Noise**:
   - [`save_png_verified()`](../photonqc/export.py) searches lossless PNG deflate compression levels `(6, 1, 0)` at the exact target pixel geometry.
   - If the requested `--min-mib` cannot be met by lossless compression at the requested pixel dimensions, the pipeline raises a `RuntimeError` rather than injecting random noise, adding metadata padding, or secretly inflating pixel dimensions.

---

## 2. Verification & Provenance Schema (`report.json`)

Every export performs a full second-pass pixel decode (`image.load()`) of the written file on disk before emitting `report.json` and `report.md`:

```json
{
  "run_id": "photonqc-66cd6c68f3ad",
  "source": "examples/rights-cleared-example.png",
  "output": "outputs/reference.png",
  "pixels": [4800, 7200],
  "megapixels": 34.56,
  "mode": "RGB",
  "requested_ppi": 300,
  "readback_ppi": [299.9994, 299.9994],
  "size_bytes": 15886636,
  "size_mib": 15.150677,
  "size_mb_decimal": 15.886636,
  "min_mib": 8.0,
  "max_mib": null,
  "png_compression_level": 1,
  "sr_backend": "lanczos_reference_not_ai",
  "embedded_icc": true,
  "input_sha256": "07560c83b83521402d6e1883da2f0686e85bbdac321f1a78520387c720620f80",
  "source_sha256": "07560c83b83521402d6e1883da2f0686e85bbdac321f1a78520387c720620f80",
  "output_sha256": "738302b3a07f7fc2da40fed6c48910ca560e3b068d32ff378ae685389ffcf84e",
  "model": {
    "backend": "lanczos",
    "name": null,
    "weights_sha256": null,
    "revision": null,
    "is_neural_ai": false
  },
  "checks": {
    "decode": true,
    "geometry": true,
    "mode_rgb": true,
    "minimum_mib": true,
    "maximum_mib": true,
    "ppi_roundtrip": true,
    "icc": true,
    "source_unmodified": true
  },
  "outcome": "PASS",
  "validation": "passed",
  "warning": "File size does not measure actual fidelity"
}
```
