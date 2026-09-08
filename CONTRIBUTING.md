# Contributing to Optical Camera Compiler

Thank you for your interest in contributing to the **Optical Camera Compiler**! We are building the open-source industry standard for hardware-level optical simulation in AI photography.

---

## How You Can Contribute

1. **Add New Hardware Camera Profiles**:
   - Contribute calibrated optical profiles for missing legendary camera systems (e.g. *Canon EOS R5 II*, *Nikon Z9*, *Mamiya RZ67*, *RED V-Raptor XL*, *Sony FX6*).
   - Profiles live in `profiles/<profile_id>.json` following the schema defined in `optical_compiler/models.py`.

2. **Add or Enhance Engine Adapters**:
   - Add new target adapters in `optical_compiler/adapters/` (e.g., Ideogram 2.0, Recraft v3, Stable Video Diffusion, Kling, Runway).

3. **Frontend & Ecosystem Integrations**:
   - ComfyUI Custom Node integration (`ComfyUI-Optical-Compiler`).
   - Lovable / React web dashboard components.
   - Blender / Cinema4D physical camera EXIF bridge.

---

## Development Setup

The compiler runs on standard Python 3.9+ with **zero required runtime dependencies**:

```bash
git clone https://github.com/<your-username>/optical-camera-compiler.git
cd optical-camera-compiler

# Run the test suite (22 unit tests)
python3 -m unittest discover -s tests -v

# Launch the local studio UI
python3 -m optical_compiler.web --open
```

---

## Submitting Pull Requests

1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feat/add-canon-r5-profile
   ```
2. Ensure all unit tests pass:
   ```bash
   python3 -m unittest discover -s tests -v
   ```
3. Commit your changes with clear semantic commit messages:
   ```bash
   git commit -m "feat(profiles): add Canon EOS R5 II with RF 50mm f/1.2L profile"
   ```
4. Push to your fork and open a Pull Request.
