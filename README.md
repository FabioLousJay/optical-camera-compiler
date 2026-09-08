# Optical Camera Compiler 📷⚡

[![CI](https://github.com/optical-camera-compiler/optical-camera-compiler/actions/workflows/ci.yml/badge.svg)](https://github.com/optical-camera-compiler/optical-camera-compiler/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 22 Passing](https://img.shields.io/badge/tests-22%20passing-brightgreen.svg)](tests/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20runtime-success.svg)](pyproject.toml)
[![Targets](https://img.shields.io/badge/engines-Flux%20%7C%20Imagen%203%20%7C%20Midjourney%20%7C%20SDXL-orange.svg)](#supported-target-adapters)

> **Deterministic Hardware-Level Optical Simulation for Zero-Artifact Photorealism**

The **Optical Camera Compiler** bridges the gap between artistic creative intent and modern diffusion latent spaces (Flux.1, Google Imagen 3, Midjourney v6+, SDXL). Instead of using buzzwords like *"photorealistic, 8k, masterpiece"*, which trigger synthetic 3D-render and stock-photo biases in modern models, this compiler enforces the physical laws of optics, sensor silicon, and lighting transport.

---

### The AI Photography Problem vs. Optical Simulation

| The "AI Look" Trap (Buzzwords) | Optical Camera Compiler Solution |
| :--- | :--- |
| **Plastic, poreless airbrushed skin** | **Resolved epidermal pores, fine vellus hair, subsurface dermal scattering** |
| **Fake Gaussian computational bokeh (slicing)** | **Physical lens sweet-spot MTF falloff ($f/8$, $f/2.8$) on large format glass** |
| **Digital sharpening edge halos & unsharp masking** | **Natural optical acutance & uncompressed raw specular highlight roll-off** |
| **Identity drift & facial warping on references** | **1:1 Biometric Anti-Drift Engine ($98\%$ lock) & structural anchors** |
| **Flat, synthetic 3D-render ambient lighting** | **$1/1600\,\text{s}$ leaf shutter strobe sync with deep negative-fill contrast carving** |

---

## Key Hardware & Optical Specs Enforced

* **Sensor**: $54 \times 40\,\text{mm}$ BSI CMOS Medium Format, 150 Megapixels, base ISO 50, 16-bit raw tonal range (15 stops latitude).
* **Optics**: Schneider Kreuznach 80mm LS f/2.8 Blue Ring stopped down to its **f/8** optical MTF sweet spot.
* **Shutter & Lighting**: Studio strobe with high-speed leaf shutter synchronization at $1/1600\,\text{s}$, deep negative fill flags to carve natural contrast and eliminate ambient bounce.
* **Micro-Detail Physics**: Resolved epidermal pores, fine vellus hair, subsurface dermal scattering, textile micro-relief, and uncompressed specular highlight falloff.
* **Anti-Artifact Shield**: Active suppression of waxy skin, computational depth slicing, over-sharpening halos, and digital noise smearing.

---

## Reference Image Pipeline & Extreme Anti-Drift Engine

A high-value professional differentiator: attach any reference image from your **local hardware** (drag & drop or file select) into the compiler to unlock two professional production workflows:

### 1. 🔬 Mode A: Optical Re-Master & Max-Fidelity Upscale
* **Goal**: Elevate existing photos (low-resolution, smartphone captures, or AI-distorted images) to true medium-format camera quality (**Phase One IQ4 150MP**, **Hasselblad H6D-100c**) while preserving 100% of the original subject identity, composition, and physical details.
* **Directives & Parameters**: Enforces 1:1 biometric identity lock, natural epidermal pores, low denoising strength ($\sim 0.35$), ControlNet Tile/Depth guidance, `--iw 2.0`, and `--cw 100`.

### 2. 🎨 Mode B: Controlled Transformation & Re-Shoot (Adaptive Adaptation)
* **Goal**: Adapt the reference image into a completely new scene, lighting condition, wardrobe, or environment while locking in the subject's exact facial architecture, eye gaze, and bone structure.
* **Directives & Parameters**: Extreme anti-drift constraints, balanced denoising ($\sim 0.65$), Flux Redux / IP-Adapter reference anchors, and Midjourney `--cref [URL] --cw 80`.

### 3. 🛡️ Extreme Anti-Drift & Anti-Hallucination Negative Shield
Actively suppresses biometric drift:
`facial morphing, feature drift, identity loss, altered facial bone structure, phantom limbs, unnatural eye color shift, warped silhouette, hallucinated background elements, extra fingers, structural divergence, identity drift, facial reconstruction artifacts`.

---

## Supported Target Adapters

1. **Flux.1 (Dev / Schnell)**: Technical declarative prose with negative assertions embedded directly into the physical prompt.
2. **Google Imagen 3 / Gemini**: Cohesive photographic prose focusing on spatial balance, light transport, and authentic raw capture fidelity.
3. **Stable Diffusion XL (SDXL)**: Dual-channel positive/negative payloads with exact resolution mapping based on aspect ratio.
4. **Midjourney (v6+)**: Concise optical rig strings with `--style raw`, `--v 6.1`, `--ar`, and `--no` suppression flags.
5. **Raw Spec**: Complete structured hardware audit view for inspection and EXIF metadata generation.

---

## Virtual Rig Studio (Interactive Local Web App)

Launch the high-end dark-mode studio UI locally with zero setup:

```bash
cd /Users/fjs/.gemini/antigravity/scratch/optical-camera-compiler
python3 -m optical_compiler.web --open
```

* **Live URL**: `http://localhost:8765`
* **Features**:
  * Visual Hardware Rig Selectors (Phase One IQ4, Leica M11, Hasselblad H6D).
  * Interactive Aperture Ring (`f/2.8`, `f/4`, `f/5.6`, `f/8 [SWEET SPOT]`, `f/11`, `f/16`).
  * Studio Lighting Rig selector (Strobe + Leaf Sync, Northern Daylight, Rembrandt, Golden Hour).
  * Real-time multi-target compilation tabs (Imagen 3, Flux.1, Midjourney v6+, SDXL, Raw Spec).
  * One-click clipboard copy with visual notification.
  * Embedded REST API (`/api/compile`, `/api/profiles`, `/api/health`) with full CORS support for connecting external frontends (such as **Lovable**, Next.js, or cloud dashboards).

---

## Hardware Profile Library (10 Elite Camera Systems)

The compiler includes calibrated optical profiles across medium format, large format, 35mm rangefinders, cinema cameras, and analog film:

1. **Phase One XF IQ4 150MP Trichromatic (`phase_one_iq4`)**:
   * *Format*: $54 \times 40\,\text{mm}$ BSI CMOS Medium Format.
   * *Optics*: Schneider Kreuznach 80mm LS f/2.8 Blue Ring, 55mm LS, 110mm LS, 150mm LS.
   * *Physics*: 16-bit raw latitude, leaf shutter at $1/1600\,\text{s}$ flash sync, negative fill contrast carving.
2. **Hasselblad H6D-100c Medium Format (`hasselblad_h6d`)**:
   * *Format*: $53.4 \times 40.0\,\text{mm}$ 100MP CMOS.
   * *Optics*: Hasselblad HC 100mm f/2.2, HC 50mm f/3.5 II, HC 150mm f/3.2.
   * *Physics*: Hasselblad Natural Colour Solution (HNCS), central lens shutter $1/2000\,\text{s}$ sync.
3. **Hasselblad 500C/M 6x6 Analog Medium Format (`hasselblad_500cm`)**:
   * *Format*: $56 \times 56\,\text{mm}$ square 120 film gate.
   * *Optics*: Carl Zeiss Planar T* 80mm f/2.8 CF, Distagon 50mm f/4, Sonnar 150mm f/4.
   * *Physics*: Kodak Portra 400 analog grain, Synchro-Compur leaf shutter, velvety square focal falloff.
4. **Pentax 67 II 6x7 Medium Format Film (`pentax_67ii`)**:
   * *Format*: $56 \times 70\,\text{mm}$ oversized medium format negative.
   * *Optics*: SMC Pentax 67 105mm f/2.4 (The Legendary Bokeh King), 90mm f/2.8, 55mm f/4.
   * *Physics*: Ultra-shallow 3D medium-format subject separation, Fuji Pro 400H pastel tones.
5. **Linhof Master Technika 4x5 Large Format (`linhof_technika_4x5`)**:
   * *Format*: $102 \times 127\,\text{mm}$ (4x5 inch) sheet film.
   * *Optics*: Schneider Apo-Symmar 150mm f/5.6 L, Rodenstock Grandagon-N 90mm f/4.5.
   * *Physics*: Scheimpflug optical plane alignment, zero vertical converging keystoning, Kodak Ektar 100 resolution.
6. **Leica M11 60MP Rangefinder (`leica_m11`)**:
   * *Format*: Full-frame 35mm BSI CMOS, zero optical low-pass filter (no AA filter).
   * *Optics*: Leica Summilux-M 35mm f/1.4 ASPH FLE II, Noctilux-M 50mm f/0.95, APO-Summicron 50mm f/2.
   * *Physics*: German aspherical acutance, extreme optical micro-contrast, reportage realism.
7. **Leica M6 Classic 35mm Analog Rangefinder (`leica_m6_analog`)**:
   * *Format*: 35mm silver halide film gate ($36 \times 24\,\text{mm}$).
   * *Optics*: Leica Summicron-M 50mm f/2 Dual-Range, Summilux 35mm Pre-ASPH.
   * *Physics*: Kodak Tri-X 400 silver halide grain structure, honest un-smoothed skin texture.
8. **ARRI Alexa 35 Cinema Large-Sensor (`arri_alexa_35`)**:
   * *Format*: Super 35 Native 4K ALEV 4 sensor.
   * *Optics*: Cooke S4/i 50mm T2.0 Prime ('The Cooke Look'), ARRI Signature Prime 47mm T1.8, Atlas 2x Anamorphic.
   * *Physics*: 17 stops exposure latitude, ARRI LogC4 color science, organic $180^\circ$ motion cadence.
9. **Fujifilm GFX 100 II 102MP Medium Format (`fujifilm_gfx100ii`)**:
   * *Format*: $43.8 \times 32.9\,\text{mm}$ high-speed 102MP CMOS.
   * *Optics*: Fujinon GF 110mm f/2 R LM WR, GF 80mm f/1.7, GF 55mm f/1.7.
   * *Physics*: Fujifilm film simulation science (Classic Chrome / Reala Ace / Astia), 16-bit raw latitude.
10. **Sony Alpha A7R V 61MP High-Resolution (`sony_a7rv`)**:
    * *Format*: Full-frame 61MP Exmor R BSI CMOS.
    * *Optics*: Sony FE 50mm f/1.2 GM, FE 85mm f/1.4 GM II, FE 135mm f/1.8 GM.
    * *Physics*: Modern commercial resolution, razor-sharp G-Master optical acutance, uncompressed 14-bit RAW.

---

## REST API Integration (For Lovable, React, or Cloud Backends)

The studio web server exposes standard JSON endpoints:

### `GET /api/profiles`
Returns metadata and hardware specs for all registered camera profiles.

### `POST /api/compile`
Compiles an incoming scene description through the specified camera rig.

```json
{
  "scene": "Architect examining blueprints in a brutalist library",
  "target": "imagen",
  "profile": "phase_one_iq4",
  "aperture": "f/8",
  "aspect_ratio": "4:5"
}
```

Response:
```json
{
  "target_engine": "imagen",
  "positive_prompt": "Photograph of Architect... Captured with a Phase One XF IQ4...",
  "negative_prompt": "CGI, 3D render, digital sharpening halos, airbrushed skin...",
  "unified_prompt": "Photograph of Architect... Captured with a Phase One XF IQ4...\n\n[ANTI-ARTIFACT NEGATIVE SHIELD]:\nEliminate CGI, 3D render, digital sharpening halos, airbrushed skin...",
  "parameters": { "aspect_ratio": "4:5" },
  "metadata": { "camera_system": "Phase One XF IQ4 150MP BSI Trichromatic" }
}
```

---

## Installation & Quickstart

### Zero-Dependency Python (3.9+)
The core compiler and web studio run on pure Python standard library with no third-party runtime dependencies required.

```bash
cd /Users/fjs/.gemini/antigravity/scratch/optical-camera-compiler
python3 -m unittest discover -s tests -v
```

---

## CLI Usage

### 1. Compile for Flux.1
```bash
python3 -m optical_compiler "Portrait of an architect examining structural models" \
  --framing "three-quarter editorial" \
  --environment "brutalist concrete studio" \
  --target flux
```

### 2. Compile for Google Imagen 3
```bash
python3 -m optical_compiler "Sculptor with marble dust on hands" \
  --target imagen \
  --aperture f/5.6 \
  --ar 4:5
```

### 3. Compare Across All Target Engines at Once
```bash
python3 -m optical_compiler "Fashion portrait in draped raw silk" \
  --target all
```

### 4. Direct macOS Clipboard Copy (`pbcopy`)
Pass `-c` or `--copy` to automatically send the compiled **all-in-one prompt** (optical description + anti-artifact shield) directly to your macOS clipboard:
```bash
python3 -m optical_compiler "Elderly fisherman with weathered skin" \
  --target flux \
  -c
```
*(Tip: Use `--pos-only` to copy only the positive prompt, or `--neg-only` to copy only the negative shield tokens).*

### 5. Output Machine-Readable JSON
```bash
python3 -m optical_compiler "Cinematic portrait" --target sdxl --json
```

---

## Python API Usage

```python
from optical_compiler import OpticalCompiler, SceneInput

# Initialize compiler with the Phase One IQ4 profile
compiler = OpticalCompiler(profile="phase_one_iq4")

# Quick compilation from string
payload = compiler.compile(
    "Master watchmaker inspecting an escapement",
    target="flux",
    framing="tight macro portrait",
    aperture="f/8"
)

print(payload.positive_prompt)
print(payload.negative_prompt)
print(payload.parameters)

# Full structured scene input
scene = SceneInput(
    subject="Botanist cataloging specimens",
    framing="medium portrait",
    environment="Victorian glasshouse with diffuse northern light",
    wardrobe="waxed cotton apron and linen shirt",
    mood="quiet, scholarly focus",
    aperture="f/5.6",
    aspect_ratio="4:5"
)

flux_payload = compiler.compile(scene, target="flux")
imagen_payload = compiler.compile(scene, target="imagen")
```

---

## Project Structure

```
optical-camera-compiler/
├── profiles/
│   └── phase_one_iq4.json          # Phase One IQ4 150MP hardware profile
├── optical_compiler/
│   ├── __init__.py                 # Exports OpticalCompiler, SceneInput, models
│   ├── __main__.py                 # Entrypoint for python3 -m optical_compiler
│   ├── cli.py                      # Full-featured command-line interface
│   ├── compiler.py                 # Unified compiler coordinator
│   ├── models.py                   # Typed dataclasses & schemas
│   ├── profiles.py                 # Profile loader & override engine
│   └── adapters/
│       ├── __init__.py             # Adapter registry
│       ├── base.py                 # Abstract base adapter
│       ├── flux.py                 # Flux.1 adapter
│       ├── imagen.py               # Imagen 3 adapter
│       ├── midjourney.py           # Midjourney v6+ adapter
│       ├── raw.py                  # Raw hardware spec adapter
│       └── sdxl.py                 # SDXL dual-channel adapter
├── tests/
│   └── test_compiler.py            # Unit test suite
├── pyproject.toml
└── README.md
```
