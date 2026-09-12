# Optical Camera Compiler 📷⚡

[![CI](https://github.com/FabioLousJay/optical-camera-compiler/actions/workflows/ci.yml/badge.svg)](https://github.com/FabioLousJay/optical-camera-compiler/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 43 Passing](https://img.shields.io/badge/tests-43%20passing-brightgreen.svg)](tests/)
[![ComfyUI: Supported](https://img.shields.io/badge/ComfyUI-Custom%20Node-blueviolet.svg)](#comfyui-custom-node-integration)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20runtime-success.svg)](pyproject.toml)
[![Targets](https://img.shields.io/badge/engines-GPT%20Images%20%7C%20Gemini%20%7C%20Midjourney%20%7C%20Flux%20%7C%20SDXL%20%7C%20JSON-orange.svg)](#supported-target-adapters)

> **Deterministic Hardware-Level Optical Simulation for Zero-Artifact Photorealism**

The **Optical Camera Compiler** bridges the gap between artistic creative intent and modern AI image models (**ChatGPT / GPT Images**, **Google Gemini / Imagen 3**, **Midjourney v8.2**, **Flux.1**, **SDXL**). Instead of using buzzwords like *"photorealistic, 8k, masterpiece"*, which trigger synthetic 3D-render, airbrushing, and stock-photo biases, this compiler compiles descriptive intent into physical laws of optics, sensor silicon, lighting transport, and rigorous anti-drift shields.

---

### The AI Photography Problem vs. Optical Simulation

| The "AI Look" Trap (Buzzwords) | Optical Camera Compiler Solution |
| :--- | :--- |
| **Plastic, poreless airbrushed skin** | **Resolved epidermal pores, fine vellus hair, subsurface dermal scattering** |
| **Fake Gaussian computational bokeh (slicing)** | **Physical lens sweet-spot MTF falloff ($f/5.6$, $f/8$) on large format & stacked glass** |
| **Digital sharpening edge halos & unsharp masking** | **Natural optical acutance & uncompressed raw specular highlight roll-off** |
| **Random logos, fake brands & typography drift** | **Hard Negative Anti-Brand Shield: zero watermarks, logos, typography, or labels** |
| **Soft focus & motion blur on critical features** | **Brutal Sharpness Protocol: Tack-sharp focus locked on the near-eye pupil & iris** |
| **Identity drift & facial warping on references** | **1:1 Biometric Anti-Drift Engine ($98\%$ lock) & Mode C Full-Body Outpainting** |
| **Flat, synthetic 3D-render ambient lighting** | **Flash sync ($1/400\,\text{s}$) strobe key ($35\text{--}45^\circ$) with black flag negative fill** |

---

## ⚡ New: Brutally Sharp Portrait Kit Capabilities

### 1. 🎯 Brutal Sharpness Protocol
* **Near-Eye Pupil Lock**: Explicitly anchors critical focal depth to the nearest iris and eyelash line, preventing models from averaging focal planes across the cheek or nose.
* **Micro-Texture Physics**: Enforces epidermal pore resolution, vellus facial hair, and authentic dermal subsurface scattering without waxy specularities or post-process edge smearing.
* **Camera Stability Cues**: Injects mechanical stabilization parameters (heavy carbon fiber tripod, dual-axis gear head, zero motion cadence) to suppress micro-motion blur.
* **Lighting Geometry ($35\text{--}45^\circ$)**: Enforces flash-dominated directional key light positioned slightly above eye line with black flag negative fill on the shadow side to maximize optical micro-contrast.

### 2. 🚫 Anti-Brand / Anti-Logo / Anti-Text Negative Shield
Diffusion and autoregressive models frequently hallucinate fake clothing brand logos, watermarks, timestamps, or illegible typography. When enabled, the compiler enforces hard negative suppression across all engines:
* **GPT Images**: Embedded natural-language directive: `Hard negative constraints (MUST ELIMINATE): watermarks, logos, brand trademarks, typography, labels, signatures, letters, words...`
* **Midjourney**: Automatic injection into `--no watermark logo text brand typography letters words signature label`.
* **SDXL / Flux / Gemini**: Layered anti-text token suppression preventing typographic drift and commercial graphics.

### 3. 📐 High-Bitrate Uncompressed Resolution Targets
Standard AI generations often suffer from JPEG block compression, chroma subsampling (4:2:0), and low bitrate banding. The compiler supports full uncompressed output targets:
* **`9:11 (12MP PNG, 3132x3828)`** *(Recommended portrait baseline)*
* **`16:9 (8K UHD, 7680x4320, 33.2MP uncompressed)`**
* **`4:5 (12MP PNG, 3100x3875)`**
* **`3:2 (12MP PNG, 4248x2832)`**
* **`4:3 (12MP PNG, 4000x3000)`**
* **`5:4 (12MP PNG, 3875x3100)`**
* **`1:1 (12MP PNG, 3464x3464)`**

---

## Reference Image Pipeline (Modes A, B, & C)

Attach any reference image from your **local hardware** (drag & drop or file select) into the compiler to unlock three production workflows:

### 🔬 Mode A: Optical Re-Master & Max-Fidelity Upscale (`restore_upscale`)
Elevates existing low-resolution or AI-distorted photos to medium-format camera quality (**Phase One IQ4 150MP**, **Hasselblad H6D-100c**) while preserving 100% of the original subject identity, composition, and physical details.

### 🎨 Mode B: Controlled Transformation & Re-Shoot (`transform_adapt`)
Adapts the reference subject into a completely new scene, lighting condition, wardrobe, or environment while locking in the subject's exact facial architecture, eye gaze, and bone structure.

### 🧍 Mode C: Full-Body Outpainting (`outpaint_full_body`)
Extends a medium-shot or tight headshot downward into a full-length head-to-toe portrait. Preserves the exact head, face, skin texture, and hair from the reference while generating seamless torso, legs, footwear, and shadows with zero perspective distortion.

---

## Supported Target Adapters (In Priority Order)

1. **GPT Images (ChatGPT / GPT-4o / DALL-E 3)**:
   Outputs the **Page 17 Master Execution Prompt** format: declarative modular blocks covering Subject, Focus discipline, Surface rendering, Lighting geometry, Camera hardware, Output specification, and Hard negative constraints.
2. **Google Gemini / Imagen 3**:
   Cohesive photographic prose focusing on spatial balance, light transport, sensor physics, and authentic raw capture fidelity.
3. **Midjourney (v8.2+)**:
   Concise optical rig strings with `--style raw`, `--v 8.2`, `--ar`, `--cref`, `--cw`, and `--no` suppression flags.
4. **Flux.1 (Dev / Schnell)**:
   Technical declarative prose with negative assertions embedded directly into the physical prompt.
5. **Stable Diffusion XL (SDXL)**:
   Dual-channel positive/negative payloads with exact resolution mapping based on aspect ratio.
6. **Raw Spec**:
   Complete structured hardware audit view for inspection, EXIF metadata generation, and Custom GPT system instructions.
7. **JSON All-in-One Prompt (`json`)**:
   Unified, machine-readable JSON specification containing the complete hardware profile, lighting geometry, micro-physics, negative shield, and cross-compiled prompts for **GPT Images**, **Gemini**, **Midjourney v8.2**, **Flux.1**, and **SDXL** in a single structured payload. Ideal for developer pipelines, API webhooks, and automation workflows.

---

## ❓ Where and How to Use the "Raw Spec" Prompt

The **Raw Spec** output is the unadorned, pure optical blueprint generated by the compiler. It is not tied to any single image generator's syntax quirks. Here is where to use it:

1. **Custom GPT / System Instructions**:
   Paste the Raw Spec into the **Instructions** box of a Custom GPT or Gemini Gem as a foundational system prompt (e.g., *"Whenever generating images, format the underlying photographic rig according to this specification"*).
2. **API Pipelines & Backends**:
   Use it in automated pipelines that ingest pure JSON/YAML specifications to pass to downstream custom models or LoRA stacks.
3. **Hardware Audits & Photorealism Calibration**:
   Use it to verify lens element counts, aperture MTF sweet spots, and shutter sync speeds before generating.
4. **ComfyUI Metadata Ingestion**:
   Embed into image EXIF chunks or node metadata so your rendered PNGs contain full camera and lens provenance.

---

## 🎛️ A/B Camera Harness (`compile_ab_harness`)

Compare two camera systems head-to-head on the exact same subject and lighting:

```python
from optical_compiler import compile_ab_harness

harness = compile_ab_harness(
    scene="Portrait of a ceramicist with clay-dusted hands",
    module_a="sony_a1_ii",
    module_b="phase_one_iq4",
    target="gpt_images",
    output_resolution="12MP PNG (3132x3828, 9:11)",
)

print("--- RIG A (Sony a1 II) ---")
print(harness["module_a"].positive_prompt)

print("--- RIG B (Phase One IQ4) ---")
print(harness["module_b"].positive_prompt)
```

---

## Hardware Profile Library (19 Elite Camera Systems)

The compiler includes calibrated optical profiles across stacked full-frame, medium format, large format, 35mm rangefinders, cinema cameras, and analog film:

### 🧠 Intelligent Auto Camera Router (`profile="auto"`)
When `profile="auto"` is specified (default in ComfyUI), the compiler inspects your scene intent and automatically routes it to the optimal hardware profile:
* **Wildlife & Fauna** $\rightarrow$ `sony_a1_ii` (Ultra-high-speed AF tracking, 50.1MP reach, $1/400\,\text{s}$ freeze)
* **Sports & Decisive Action** $\rightarrow$ `canon_eos_r1` (40 fps burst, zero rolling shutter, high-speed sports primes)
* **Macro & Specimen Science** $\rightarrow$ `panasonic_lumix_s1rii` (1:1 reproduction ratio, micro-relief acutance, diffraction suppression)
* **Cinema & Narrative Film Stills** $\rightarrow$ `sony_fx_series` (Venice color science, $180^\circ$ shutter, 10-bit S-Log3)
* **Feature Film Hollywood Masters** $\rightarrow$ `arri_alexa_35` (Super 35 ALEV 4 sensor, Cooke S4/i primes, LogC4)
* **Architecture & Interior Structure** $\rightarrow$ `linhof_technika_4x5` (Large-format sheet film, Scheimpflug tilt-shift perspective control)
* **Luxury, Horology & Fine Art** $\rightarrow$ `phase_one_iq4` (150MP Trichromatic medium format, 16-bit raw latitude)
* **Portraits, Beauty & Fashion** $\rightarrow$ `hasselblad_x2d_ii_100c` (100MP BSI CMOS, HNCS natural skin tonality, XCD 90V prime)
* **Street & Travel Documentary** $\rightarrow$ `fujifilm_gfx100rf` (102MP large-format rangefinder, Classic Chrome / Reala Ace)
* **Prestige Photojournalism & Reportage** $\rightarrow$ `leica_sl3_p` (44.9MP BSI CMOS, Maestro IV processor, APO-Summicron-SL glass)
* **Nostalgic 35mm Analog Film** $\rightarrow$ `leica_m6_analog` (35mm silver halide, Kodak Tri-X 400, classic German micro-contrast)
* **Analog Medium Format Film** $\rightarrow$ `pentax_67ii` (6x7 oversized negative, legendary SMC 105mm $f/2.4$ bokeh king)

---

### Stacked Full-Frame & Flagship Action
1. **Sony a1 II Stacked Full-Frame (`sony_a1_ii`)**:
   * *Sensor*: $35.9 \times 24.0\,\text{mm}$ 50.1MP Exmor RS stacked CMOS.
   * *Optics*: Sony FE 85mm F1.4 GM II (SEL85F14GM2) at $f/5.6$ sweet spot, FE 50mm F1.2 GM, FE 135mm F1.8 GM.
   * *Physics*: $1/400\,\text{s}$ flash sync, maximum sharpness hit-rate, micro-motion freeze.
2. **Canon EOS R1 Stacked Flagship Action (`canon_eos_r1`)**:
   * *Sensor*: $36.0 \times 24.0\,\text{mm}$ 24.2MP back-illuminated stacked CMOS, Accelerated Capture DIGIC Accelerator.
   * *Optics*: Canon RF 85mm F1.2L USM, RF 70-200mm F2.8L IS USM Z, RF 400mm F2.8L IS USM.
   * *Physics*: 40 fps burst rate, $1/2000\,\text{s}$ freeze, zero rolling shutter, cross-type AF tracking.
3. **Canon EOS R5 Mark II Stacked Full-Frame (`canon_eos_r5_ii`)**:
   * *Sensor*: $36.0 \times 24.0\,\text{mm}$ 45.0MP back-illuminated stacked CMOS.
   * *Optics*: Canon RF 85mm F1.2L USM at $f/5.6$ sweet spot, RF 50mm F1.2L USM, RF 135mm F1.8L IS USM.
   * *Physics*: Accelerated capture architecture, organic skin tonal gradation, dual-pixel micro-contrast.
4. **Nikon Z 9 Stacked Flagship Full-Frame (`nikon_z9`)**:
   * *Sensor*: $35.9 \times 23.9\,\text{mm}$ 45.7MP stacked CMOS (pure electronic shutter).
   * *Optics*: NIKKOR Z 135mm f/1.8 S Plena at $f/5.0$ sweet spot, Z 85mm f/1.2 S, Z 50mm f/1.2 S.
   * *Physics*: Zero rolling shutter, Plena circular bokeh geometry, base ISO 64 High-Efficiency RAW.

### Medium & Large Format
5. **Phase One XF IQ4 150MP Trichromatic (`phase_one_iq4`)**:
   * *Sensor*: $54 \times 40\,\text{mm}$ BSI CMOS Medium Format, 150MP, base ISO 50.
   * *Optics*: Schneider Kreuznach 80mm LS f/2.8 Blue Ring at $f/8$, 55mm LS, 110mm LS, 150mm LS.
   * *Physics*: 16-bit raw latitude, leaf shutter $1/1600\,\text{s}$ sync, negative fill contrast carving.
6. **Hasselblad X2D II 100C Medium Format (`hasselblad_x2d_ii_100c`)**:
   * *Sensor*: $43.8 \times 32.9\,\text{mm}$ 100MP BSI CMOS, 16-bit raw, 15.3 stops dynamic range.
   * *Optics*: Hasselblad XCD 90mm f/2.5 V, XCD 55mm f/2.5 V, XCD 38mm f/2.5 V.
   * *Physics*: Hasselblad Natural Colour Solution (HNCS), 10-stop IBIS, leaf shutter $1/4000\,\text{s}$ flash sync.
7. **Hasselblad H6D-100c Medium Format (`hasselblad_h6d`)**:
   * *Sensor*: $53.4 \times 40.0\,\text{mm}$ 100MP CMOS.
   * *Optics*: Hasselblad HC 100mm f/2.2, HC 50mm f/3.5 II, HC 150mm f/3.2.
   * *Physics*: Central lens shutter $1/2000\,\text{s}$ sync, studio commercial baseline.
8. **Fujifilm GFX 100 II 102MP Medium Format (`fujifilm_gfx100ii`)**:
   * *Sensor*: $43.8 \times 32.9\,\text{mm}$ high-speed 102MP CMOS II HS.
   * *Optics*: Fujinon GF 110mm f/2 R LM WR, GF 80mm f/1.7, GF 55mm f/1.7.
   * *Physics*: Fujifilm color science (Classic Chrome / Reala Ace / Astia), 16-bit raw latitude.
9. **FUJIFILM GFX100RF Rangefinder Large Format (`fujifilm_gfx100rf`)**:
   * *Sensor*: $43.8 \times 32.9\,\text{mm}$ 102MP Large-Format CMOS II rangefinder.
   * *Optics*: Fujinon GF 45mm f/2.8 R WR, GF 63mm f/2.8 R WR, GF 110mm f/2 R LM WR.
   * *Physics*: Rangefinder form factor, street documentary fidelity, film simulation color science.
10. **Linhof Master Technika 4x5 Large Format (`linhof_technika_4x5`)**:
    * *Sensor*: $102 \times 127\,\text{mm}$ (4x5 inch) sheet film.
    * *Optics*: Schneider Apo-Symmar 150mm f/5.6 L, Rodenstock Grandagon-N 90mm f/4.5.
    * *Physics*: Scheimpflug optical plane alignment, zero vertical keystoning, Kodak Ektar 100 resolution.

### Rangefinders, Reportage & Micro-Science
11. **Leica SL3-P Mirrorless Maestro IV (`leica_sl3_p`)**:
    * *Sensor*: $36.0 \times 24.0\,\text{mm}$ 44.9MP BSI CMOS, Maestro IV processor with L-Mount optics.
    * *Optics*: Leica APO-Summicron-SL 50mm f/2 ASPH, APO-Summicron-SL 75mm f/2 ASPH.
    * *Physics*: Benchmark apochromatic acutance, zero color fringing, prestige documentary reportage.
12. **Panasonic LUMIX S1RII Micro-Science Master (`panasonic_lumix_s1rii`)**:
    * *Sensor*: $35.9 \times 23.9\,\text{mm}$ 44.3MP CMOS with Dual Native ISO (100/640).
    * *Optics*: Lumix S PRO 50mm f/1.4 (Certified by Leica), Lumix S 100mm f/2.8 Macro.
    * *Physics*: 1:1 macro reproduction ratio, micro-relief diffraction suppression, scientific fidelity.
13. **Leica M11 60MP Rangefinder (`leica_m11`)**:
    * *Sensor*: Full-frame 35mm BSI CMOS, zero optical low-pass filter (no AA filter).
    * *Optics*: Leica Summilux-M 35mm f/1.4 ASPH FLE II, Noctilux-M 50mm f/0.95, APO-Summicron 50mm f/2.
    * *Physics*: German aspherical acutance, extreme optical micro-contrast, street reportage realism.
14. **Sony Alpha A7R V 61MP High-Resolution (`sony_a7rv`)**:
    * *Sensor*: Full-frame 61MP Exmor R BSI CMOS.
    * *Optics*: Sony FE 50mm f/1.2 GM, FE 85mm f/1.4 GM II, FE 135mm f/1.8 GM.
    * *Physics*: Modern commercial resolution, razor-sharp G-Master optical acutance.

### Cinema Production & Venice Color Science
15. **Sony FX Cinema Line Full-Frame (`sony_fx_series`)**:
    * *Format*: $35.6 \times 23.8\,\text{mm}$ full-frame cinema 4K Exmor R BSI CMOS, 15+ stops dynamic range.
    * *Optics*: Sony FE 50mm f/1.2 GM stopped down to $f/2.8$ cinematic sweet spot, FE 24-70mm f/2.8 GM II, FE 85mm f/1.4 GM II.
    * *Physics*: Venice color science highlight rolloff, $180^\circ$ cinema shutter angle ($1/48\,\text{s}$ cadence), Dual Base ISO 800/12800, 10-bit 4:2:2 All-Intra S-Log3/S-Gamut3.Cine.
16. **ARRI Alexa 35 Cinema Large-Sensor (`arri_alexa_35`)**:
    * *Format*: Super 35 Native 4K ALEV 4 sensor, Cooke S4/i 50mm T2.0 Prime, ARRI LogC4.

### Analog Film Classics
17. **Hasselblad 500C/M 6x6 Analog Medium Format (`hasselblad_500cm`)**:
    * *Format*: $56 \times 56\,\text{mm}$ square 120 film gate, Carl Zeiss Planar T* 80mm f/2.8 CF.
18. **Pentax 67 II 6x7 Medium Format Film (`pentax_67ii`)**:
    * *Format*: $56 \times 70\,\text{mm}$ oversized negative, SMC Pentax 67 105mm f/2.4 Reference Lens.
19. **Leica M6 Classic 35mm Analog Rangefinder (`leica_m6_analog`)**:
    * *Format*: 35mm silver halide film gate, Leica Summicron-M 50mm f/2 Dual-Range, Kodak Tri-X 400.

---

## 💡 Master Photographic Lighting Presets
Apply physical lighting recipes via `--lighting-preset` or in the Studio UI:
* **`golden_hour`**: Low-angle directional golden sunlight (3200K–3800K), warm specular edge wrap, soft atmospheric glow.
* **`blue_hour`**: Deep twilight ambient sky illumination (7500K–9000K), cool soft fill balanced against 2700K tungsten practical lights.
* **`studio_soft`**: Large parabolic softbox key at $45^\circ$, subtle negative fill, diffused wrap-around illumination.
* **`studio_hard`**: Focused beauty dish or fresnel key, crisp shadow boundaries, sculpted facial micro-contrast.
* **`flash_freeze`**: High-speed optical flash strobe ($1/1600\,\text{s}$ leaf sync), microsecond duration motion freeze.
* **`overcast`**: Giant natural atmospheric softbox, diffused neutral daylight (5500K–6000K), linear shadow gradient.
* **`dramatic`**: Chiaroscuro high-contrast lighting, single directional key, 8:1 contrast ratio, deep true black shadows.
* **`neon`**: Multi-chromatic saturated ambient rim and key lights, complementary cyan/magenta or amber/teal contrast.

---

## 🎯 Modular Capture Modes
Enforce physical camera discipline via `--capture-mode`:
* **`static_max_detail`**: Tripod-mounted lock, zero sensor shake, base ISO, maximum MTF optical acutance.
* **`portrait_max_detail`**: Focus locked on the near eye, iris and eyelashes tack sharp, resolved epidermal skin pores.
* **`action_max_detail`**: Decisive-moment freeze, high-speed shutter, zero motion smear, dynamic muscle tension.
* **`macro_max_detail`**: 1:1 reproduction ratio, extreme micro-plane depth slicing, diffraction-suppressed optical plane.
* **`landscape_architecture_max_detail`**: Rectilinear zero-distortion geometry, infinite hyperfocal plane, level horizon.

---

## Virtual Rig Studio (Interactive Local Web App)

Launch the dark-mode studio UI locally with zero setup:

```bash
optical-studio
# or: python3 -m optical_compiler.web --open
```

* **Live URL**: `http://localhost:8765`
* **Features**:
  * **14 Elite Camera Systems**: Full coverage of all stacked full-frame, medium format, cinema, and analog rigs.
  * **GPT Images / ChatGPT Master Execution Tab**: Instant copyable prompts formatted for ChatGPT.
  * **Section 05 Brutal Sharpness Toggles**: Near-eye focus lock, Anti-Brand Shield, and 12MP/8K resolution targets.
  * **Mode C Outpaint UI**: Dedicated full-body vertical outpainting button with reference preview.
  * **Local Hardware Image Uploader**: Drag & drop reference photos directly from your machine with client-side resolution & aspect ratio autodetection.
  * **Interactive Aperture Ring**: `f/2.8`, `f/4`, `f/5.6`, `f/8 [SWEET SPOT]`, `f/11`, `f/16`.
  * **Embedded REST API**: `/api/compile`, `/api/profiles`, `/api/health` with full CORS support for external frontends.

---

## ComfyUI Custom Node Integration

The repository acts as a native **ComfyUI custom node** with zero extra dependencies:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/FabioLousJay/optical-camera-compiler.git
```

Restart ComfyUI, then right-click on the graph canvas:
**Add Node ➔ prompt/optical ➔ 📷 Optical Camera Compiler**

* **Outputs**:
  * `positive_prompt` ➔ Pipe directly into `CLIP Text Encode (Prompt)`
  * `negative_prompt` ➔ Pipe into `CLIP Text Encode (Negative)`
  * `unified_payload` ➔ Full prompt with negative shield for single-prompt nodes (GPT / Flux.1 / Midjourney)
* **Controls**:
  * `camera_rig`: Select from all 13 camera systems (including Sony a1 II, Canon R5 II, Nikon Z 9).
  * `model_target`: `gpt_images`, `imagen`, `midjourney`, `flux`, `sdxl`.
  * `reference_mode`: `disabled`, `transform_adapt`, `restore_upscale`, `outpaint_full_body`.
  * `aspect_ratio`: `9:11` (default 12MP), `4:5`, `3:2`, `4:3`, `5:4`, `16:9`, `1:1`, `21:9`, `9:16`.
  * `brutal_sharpness_protocol`: `enabled` / `disabled`.
  * `suppress_text_branding`: `enabled` / `disabled`.

---

## Quickstart & Installation

Install directly via pip:

```bash
pip install optical-camera-compiler
```

Or clone the repository locally:

```bash
git clone https://github.com/FabioLousJay/optical-camera-compiler.git
cd optical-camera-compiler
```

Run test suite:
```bash
python3 -m unittest discover -s tests -v
```

---

## CLI Usage

### 1. Compile for GPT Images (ChatGPT Master Execution Prompt)
```bash
python3 -m optical_compiler "Portrait of an architect examining structural models" \
  --profile sony_a1_ii \
  --target gpt_images \
  --ar 9:11 \
  -c
```

### 2. Compile for Google Gemini / Imagen 3
```bash
python3 -m optical_compiler "Sculptor with marble dust on hands" \
  --profile canon_eos_r5_ii \
  --target imagen \
  --aperture f/5.6 \
  --ar 4:5
```

### 3. Direct macOS Clipboard Copy (`pbcopy`)
Pass `-c` or `--copy` to automatically send the compiled prompt directly to your macOS clipboard:
```bash
python3 -m optical_compiler "Elderly fisherman with weathered skin" \
  --profile nikon_z9 \
  --target gpt_images \
  -c
```

---

## Python API Usage

```python
from optical_compiler import OpticalCompiler, SceneInput, compile_ab_harness

# 1. Initialize compiler with Sony a1 II profile
compiler = OpticalCompiler(profile="sony_a1_ii")

# 2. Compile with Brutal Sharpness Protocol and Anti-Brand Shield
payload = compiler.compile(
    "Master watchmaker inspecting an escapement",
    target="gpt_images",
    output_resolution="12MP PNG (3132x3828, 9:11)",
    sharpness_protocol=True,
    suppress_text_branding=True,
)

print(payload.positive_prompt)
print(payload.negative_prompt)

# 3. Side-by-side A/B Camera comparison harness
harness = compile_ab_harness(
    scene="Botanist cataloging rare orchids",
    module_a="sony_a1_ii",
    module_b="phase_one_iq4",
    target="gpt_images",
)
```

---

## License

MIT License. Designed and maintained for open-source AI photography engineering.
