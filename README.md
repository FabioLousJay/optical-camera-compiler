# Optical Camera Compiler 📷⚡

[![CI](https://github.com/FabioLousJay/optical-camera-compiler/actions/workflows/ci.yml/badge.svg)](https://github.com/FabioLousJay/optical-camera-compiler/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 128 Passing](https://img.shields.io/badge/tests-128%20passing-brightgreen.svg)](tests/)
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

## Reference Image Pipeline (Modes A, B, C, D, & E)

Attach any reference image from your **local hardware** (drag & drop or file select) into the compiler to unlock five production workflows:

### 🔬 Mode A: Optical Re-Master & Max-Fidelity Upscale (`restore_upscale`)
Elevates existing low-resolution or AI-distorted photos to medium-format camera quality (**Phase One IQ4 150MP**, **Hasselblad H6D-100c**) while preserving 100% of the original subject identity, composition, and physical details.

### 🎨 Mode B: Controlled Transformation & Re-Shoot (`transform_adapt`)
Adapts the reference subject into a completely new scene, lighting condition, wardrobe, or environment while locking in the subject's exact facial architecture, eye gaze, and bone structure.

### 🧍 Mode C: Full-Body Outpainting (`outpaint_full_body`)
Extends a medium-shot or tight headshot downward into a full-length head-to-toe portrait. Preserves the exact head, face, skin texture, and hair from the reference while generating seamless torso, legs, footwear, and shadows with zero perspective distortion.

### ✨ Mode D: Universal De-Pixelate & 102MP Upscale Restoration v3.1 (`depixelate_gfx100rf` / `--depixelate`)
Reference-guided image restoration and resolution enhancement with fixed **Fujifilm GFX100RF 102MP** rendering target and non-negotiable **Human Skin Realism Override Protocol**. Eliminates pixelation, JPEG macro-blocking, compression damage, aliasing, and digital softness while preserving source identity, proportions, and lighting logic.

#### 🛡️ Human Skin Realism Override Protocol
Whenever human skin is present in the image, skin realism takes absolute priority over micro-detail recovery, perceived resolution, sharpening, and texture reconstruction:
* **Organic Skin Softness**: Skin must remain softer than eyes, hair, jewelry, teeth, clothing, text, and hard edges.
* **Zero Synthetic Texturing**: Strictly prohibits pore stamping, repeated procedural dots, artificial pebbled leather skin, AI skin swirls/worms/lace, and synthetic high-frequency noise.
* **Zero Plastic Waxiness**: Prohibits plastic airbrushing, wax figure skin, porcelain smoothing, and beauty filter smearing.
* **Natural Dynamic Range**: Realistic skin subsurface scattering with soft tonal transitions and natural tonal gradation.

#### 📄 Content Classification & Flat Copy-Stand Reproduction
The compiler classifies content into 8 domain archetypes (`photograph`, `portrait`, `product_photo`, `document_scan`, `poster_or_flyer`, `meme_or_infographic`, `ui_or_screenshot`, `mixed_content`):
* **Flat Reproduction Enforcement**: For document scans, UI screenshots, infographics, posters, and memes, optical depth-of-field falloff, background defocus bokeh, chromatic aberration, lens vignetting, and analog grain are strictly suppressed.
* **Strict Text & Structured Content Preservation**: Enforces character-for-character typographic accuracy, font weights, tabular alignments, and diagram connectors without hallucinated glyphs or drift.

### 🔒 Mode E: Editorial Documentary Identity Lock (`identity_lock` / `--ref-mode identity_lock`)
Reference-faithful documentary and editorial portraits with absolute anatomical and biometric locking:
* **Anatomical & Bone Geometry Preservation**: Locks skull structure, eye spacing, nose bridge, jawline contour, lip fullness, hairline pattern, and beard pattern.
* **Strict Anti-Drift Prohibitions**: Hard suppression of gender reinterpretation, age alteration, body slimming, facial reshaping, feature feminization/masculinization, and synthetic skin smoothing.
* **Independent Environmental Flow**: Allows surrounding scene, lighting, and dynamic crowds to move freely while the reference subject remains immutably anchored.

### 📦 Mode F: Product-Reference Crop & 100% Commercial SKU Approval Gate (`product_lock` / `--product-lock`)
Commercial packaging and SKU generation with forensic anti-drift protection for sellable objects:
* **The Failure Mode Solved**: While optical cues (MTF acutance, specular roll-off, skin texture) make human hands and backdrops hyper-realistic, diffusion models frequently drift the sellable product itself—altering cap closure geometry (e.g. mutating screw caps into droppers), corrupting label kerning/tracking, erasing mold parting seams, and drifting brand Pantone colors.
* **Product-Reference Crop Anchor (`--product-crop <path>`)**: Isolates and anchors the genuine commercial SKU packaging as an unyielding physical reference.
* **Mandatory 5-Point Forensic Inspection Gate (`approval_gate_100pct` / `--no-approval-gate`)**:
  1. **Gate 1: Cap & Closure Geometry (`--cap-geometry`)**: Form factor, diameter, knurling rib count, threading, and closure mechanics locked.
  2. **Gate 2: Label Kerning & Typography (`--label-kerning`)**: Character-for-character typographic fidelity, letter spacing, font weight, and zero hallucinated text.
  3. **Gate 3: Manufacturing Seams & Parting Lines (`--seams`)**: Mold lines, glass parting seams, and base rim radiuses preserved.
  4. **Gate 4: Material Finish & Specular Response (`--material-finish`)**: Matte, satin, gloss, frosted glass, refractive index, and anti-plastic enforcement.
  5. **Gate 5: SKU Color Integrity (`--sku-color`)**: Exact Pantone/hex brand color lock across shifting scene lighting.
* **Intelligent Camera Routing**: Commercial product locks auto-route to the **Phase One XF IQ4 150MP Trichromatic** digital back with Schneider Kreuznach optics.

---

## 🚀 Industry-Pioneering Precision Suites (v3.3)

Three breakthrough features inspired by professional cinema optics, biomechanical hand anatomy research, and commercial billboard advertising standards:

### 1. 🖐️ Biomechanical Hand & Finger Precision Gate (The 5-Point Grip Lock)
Solves the quintessential AI image generation failure mode (mutated hands, fused fingers, polydactyly, rubber knuckles, lack of grip physics):
* **Gate H1: 5-Ray Metacarpal Architecture**: Exactly five articulated digits (thumb, index, middle, ring, pinky) following anatomical human length ratios ($2:3:4:3.5:2.5$) and distinct metacarpophalangeal (MCP), proximal interphalangeal (PIP), and distal interphalangeal (DIP) joints.
* **Gate H2: Contact Physics & Tissue Blanching**: Micro-vascular capillary displacement and authentic skin blanching where flesh compresses against grasped surfaces under mechanical load. Prohibits clipping or penetration through solid objects.
* **Gate H3: Flexion Creases & Thenar Musculature**: Authentic palmar and digital flexion creases, distinct thenar and hypothenar eminence musculature, and visible wrist tendon tension.
* **Gate H4: Ungual Bed & Lunula Precision**: Translucent nail plates with natural pinkish vascular flush, pale lunula crescents, micro-cuticles, and clean natural nail margins.
* **Gate H5: Anti-Hallucination Hand Negative Lock**: 32+ specialized anti-mutation negative tokens (`extra fingers`, `missing fingers`, `fused digits`, `polydactyly`, `ectrodactyly`, `webbed digits`, `floating knuckles`, `rubber knuckles`, etc.).
* **Grip Type Taxonomy (`--grip-type`)**: `precision_pinch`, `cylindrical_wrap`, `palm_support`, `relaxed_rest`, `open_palm`.
* **CLI Flag**: `--hand-lock`, `--grip-type precision_pinch`, `--hand-details "..."`

### 2. 🎬 Cinema Anamorphic Optics & Flare Engine
Simulates authentic anamorphic cinema primes (Cooke Anamorphic /i Full Frame Plus, ARRI Master Anamorphic):
* **Auto-Routing to ARRI Alexa 35**: Specifying anamorphic squeeze automatically routes to `arri_alexa_35` Super 35 cinema sensor.
* **Cylindrical Elements & Squeeze Factors (`--squeeze`)**: `2.0x` (standard cinema scope), `1.8x`, `1.5x`, `1.33x`, `1.0x`.
* **2:1 Vertical Elliptical Oval Bokeh**: Simulates horizontal optical squeeze where out-of-focus background highlights render as vertical oval discs with subtle edge astigmatism and gentle barrel curvature.
* **Chromatic Streak Flare Coatings (`--streak-flare`)**:
  * `cyan_blue`: Classic modern sci-fi / dramatic cinema horizontal streak flares.
  * `warm_gold`: 1970s Panavision golden hour nostalgia.
  * `neutral_silver`: Clean, uncolored high-end commercial streaks.
  * `vintage_magenta`: Retro neon indie aesthetics.
* **Iris Blade Diffraction Spikes (`--iris-blades`)**: `14_blade_circular` (smooth circular bokeh), `9_blade_rounded`, `8_blade_octagonal` (8-point starburst spikes), `6_blade_hexagonal` (classic 6-point starburst).
* **Automatic Cinema Framing**: Midjourney outputs `--ar 2.39:1` cinema scope automatically.
* **CLI Flag**: `--anamorphic`, `--squeeze 2.0x`, `--streak-flare cyan_blue`, `--iris-blades 14_blade_circular`

### 3. 📢 Commercial Advertising Suite (Gobo Light Shapers + Ad-Safe Copy-Space)
Transforms raw photo generations into ready-to-deploy commercial, print, billboard, and social advertising assets:
* **Optical Gobo Projection Cookies (`--gobo`)**: Projects crisp architectural and organic shadow patterns: `venetian_blinds`, `dappled_foliage`, `window_panes`, `geometric_slits`, `prism_fracture`.
* **Professional Studio Grip Modifiers (`--grip`)**: `beauty_dish_honeycomb` (20° directional beauty lighting), `butterfly_8x8_silk` (diffused ambient wrap), `snoot_grid` (pinpoint spotlighting), `floppy_negative_fill` (deep shadow sculpting).
* **Key-to-Fill Contrast Ratios (`--lighting-ratio`)**: `1:1` (high-key catalog), `2:1` (commercial editorial), `4:1` (classic studio portrait), `8:1` (dramatic chiaroscuro), `16:1` (extreme low-key).
* **Asymmetric Negative Copy-Space (`--copy-space`)**: `left_third`, `right_third`, `top_third`, `bottom_third`—strictly reserves calm, uncluttered background space for brand headlines, logos, and typographic copy.
* **Ad-Safe Safe-Zone Framing (`--ad-safe-zone`)**: `tiktok_reels_9_16` (keeps content clear of right-side icons and bottom captions), `instagram_feed_4_5`, `ecommerce_catalog_1_1`.
* **CLI Flag**: `--gobo venetian_blinds`, `--grip beauty_dish_honeycomb`, `--lighting-ratio 4:1`, `--copy-space left_third`, `--ad-safe-zone instagram_feed_4_5`

---

## 💎 GenAI Photography Mastery Suite (v3.4)

Five state-of-the-art additions bringing hyper-refined anatomical control, dimensional volumetric rendering, non-destructive policy compliance, fine-art prepress lab calibration, and 8K-class master resolution synthesis:

### 1. 🏋️ Body Morphology & Proportional Volume Calibration Engine
Solves anatomical ballooning, impossible insertions, and comic-book caricature exaggeration when requesting larger muscular or heavier body mass:
* **Proportional Scaling Rule**: All volume increases in target regions (`biceps`, `chest`, `gut`, `legs`, `waist`, etc.) are mathematically bound to existing skeletal frame dimensions, shoulder width, torso depth, limb length, and head size.
* **Calibrated Target Body Mass (`--weight-lb`)**: Injects exact calibrated weight (e.g. `230 lb`) to anchor realistic overall mass distribution.
* **Bilateral Asymmetry Preservation**: Prohibits mechanical mirroring, unnatural bilateral symmetry, and cloned muscle insertions.
* **Gravitational Physics & Seated Compression**: Enforces realistic abdominal soft-tissue projection, natural compression against seating or surfaces, and authentic skin fold kinematics.
* **Clothing Conformity**: Wardrobe conforms, stretches, and contours naturally over enlarged muscle or body mass without tearing, breaking seam geometry, or altering color patterns.
* **20+ Specialized Anti-Distortion Tokens**: Automatically injected into the negative shield whenever morphology is active (`extreme bodybuilding`, `cartoon proportions`, `balloon muscles`, `impossible muscle insertions`, `hyper-inflated limbs`, `grotesque exaggeration`, etc.).
* **CLI Flag**: `--body-volume "biceps:significant, chest:moderate" --weight-lb 230`

### 2. 🔮 4D Volumetric & Premium Material Engine
Renders subjects and objects with physical dimensional presence and tangible light interaction:
* **Dimensional Volumetric Depth (`--volumetric-4d`)**: Clear foreground-background separation, contour rim lighting, deep tonal separation, and tangible 3D/4D volumetric presence (strictly prohibiting temporal motion trails or surreal sci-fi blur).
* **Premium Surface Physics (`--material`)**:
  * `latex_gloss`: High-gloss reflective latex with authentic curvature highlights and specular roll-off.
  * `liquid_glass`: Transparent optical refractive glass with caustic light distribution.
  * `dielectric_acrylic`: Clear lucite/perspex with clean edge definition and internal refraction.
  * `polished_vinyl`: Reflective architectural PVC and polished synthetic sheen.
  * `anodized_aluminum`: Matte-metallic surface scattering with brushed directional highlights.
* **Studio Background Isolation (`--background-style`)**: `pure_black_blur` (opaque softly blurred black void for maximum subject pop), `minimalist_studio_grey`, `clean_high_key_white`.
* **Conditional Text Removal Engine (`--remove-text`)**: When letters, labels, or watermarks exist on reference crops, cleanly removes typography and fills the surface with authentic material physics.
* **CLI Flag**: `--volumetric-4d --material latex_gloss --background-style pure_black_blur --remove-text`

### 3. 🛡️ Policy-Safe Compliance Recovery Layer (`--policy-safe`)
Prevents non-compliant refusal loops and false-positive safety flags across hosted enterprise models (**ChatGPT DALL-E 3**, **Google Imagen 3**, **Midjourney v8.2**):
* **Non-Destructive Transformation**: Converts sensitive, form-fitting, or edgy creative concepts into elegant, dignified, tasteful fine-art editorial execution without losing camera physics, optical acutance, anatomy, or lighting geometry.
* **Safe Aesthetic Framing**: Injects safe platform styling into positive prompts while activating safety suppression in the negative shield (`provocative`, `inappropriate`, `revealing`, `gratuitous`).
* **Universal Model Support**: Active across all 7 target adapters (GPT Images, Imagen 3, Midjourney, Flux.1, SDXL, Raw Spec, and JSON Schema 3.4).
* **CLI Flag**: `--policy-safe`

### 4. 🖨️ Print-Calibrated Prepress & Exhibition Lab Matrix
Prepares generated imagery for fine-art exhibition, gallery prints, and high-Dmax print lab production:
* **Exact Mathematical Pixel Calculations (`inches_to_pixels`)**: Calculates exact raster dimensions at specified print density (e.g. 16" x 24" at 300 PPI = $4800 \times 7200\text{ px}$; 9" x 12" at 640 PPI = $5760 \times 7680\text{ px}$).
* **Fine-Art Paper Profiles (`--paper`)**:
  * `matte_cotton`: Hahnemühle Photo Rag 308g (100% cotton matte, zero specular glare, soft optical ink absorption, Dmax 1.65–1.75).
  * `baryta`: Canson Infinity Baryta Photographique II 310g (traditional silver-halide darkroom satin finish, museum grade, Dmax 2.60–2.75).
  * `luster`: Epson Ultra Premium Luster 260g (pebbled surface, commercial portrait standard, Dmax 2.10–2.25).
  * `glossy`: Ilford Galerie Smooth Gloss 310g (mirror finish, maximum dynamic contrast, Dmax 2.40–2.55).
  * `canvas`: Breathing Color Lyve Canvas 450g (textured weave, physical relief, painterly depth).
* **Rendering Intent**: Supports `relative_colorimetric` (with Black Point Compensation) and `perceptual` color reproduction.
* **CLI Flag**: `--paper baryta --print-size 16x24@300`

### 5. 🖥️ Master Resolution Engine & JSON Schema 3.4
* **New Aspect Ratios**:
  * **`5:5` (Square 16MP Full-Frame Master)**: Renders at $4000 \times 4000\text{ px}$ uncompressed.
  * **`9:12` (Vertical 44.2MP 8K-Class Exhibition Master)**: Renders at $5760 \times 7680\text{ px}$ uncompressed.
* **JSON Prompt Schema 3.4 Upgrade**: Automatically emits `schema_version: "3.4"` with dedicated structured blocks: `body_morphology_volume_engine`, `volumetric_material_engine`, `prepress_matrix`, and `policy_compliance_layer`.
* **Two-Stage Quality Inspection**: Standardized checklist for 100% and 200% zoom validation of iris detail, fingernail lunula, textile weave, and text sharpness.

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

## Hardware Profile Library (20 Elite Camera Systems)

The compiler includes calibrated optical profiles across stacked full-frame, medium format, large format, 35mm rangefinders, cinema cameras, and analog film:

### 🧠 Intelligent Auto Camera Router (`profile="auto"`)
When `profile="auto"` is specified (default in ComfyUI), the compiler inspects your scene intent and automatically routes it to the optimal hardware profile:
* **Motion-Blur Crowds & Editorial Contrast** $\rightarrow$ `leica_sl2` (47.3MP full-frame CMOS, Summilux-SL 50mm $f/2.8$, slow shutter motion trails, tack-sharp still subject)
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
9. **FUJIFILM GFX100RF Fixed-Lens 102MP Medium Format (`fujifilm_gfx100rf`)**:
   * *Sensor*: $43.8 \times 32.9\,\text{mm}$ 102MP high-speed CMOS II HS, native $11648 \times 8736$ resolution.
   * *Optics*: Fixed Fujinon 35mm f/4 lens (stopped down to f/5.6–f/8 optical sweet spot), 0.84x magnification, edge-to-edge MTF sharpness.
   * *Physics*: Integrated leaf shutter, zero rolling shutter artifacts, ultra-low vibration, Reala Ace / Classic Chrome color science, 16-bit raw tonal latitude.
10. **Linhof Master Technika 4x5 Large Format (`linhof_technika_4x5`)**:
    * *Sensor*: $102 \times 127\,\text{mm}$ (4x5 inch) sheet film.
    * *Optics*: Schneider Apo-Symmar 150mm f/5.6 L, Rodenstock Grandagon-N 90mm f/4.5.
    * *Physics*: Scheimpflug optical plane alignment, zero vertical keystoning, Kodak Ektar 100 resolution.

### Rangefinders, Reportage, Motion Blur & Micro-Science
11. **Leica SL2 Full-Frame Mirrorless (`leica_sl2`)**:
    * *Sensor*: $36.0 \times 24.0\,\text{mm}$ 47.3MP CMOS full-frame sensor, Maestro III processor, Dual Base ISO 50/400.
    * *Optics*: Leica Summilux-SL 50mm f/1.4 ASPH stopped down to $f/2.8$ sweet spot, APO-Summicron-SL 35mm f/2 ASPH, APO-Summicron-SL 75mm f/2 ASPH.
    * *Physics*: Slow shutter motion-blur aesthetic ($1/4\text{--}1/8\,\text{s}$ equivalent), smooth wrapping crowd motion blur trails around stationary tack-sharp subject, restrained indie-cinema monochrome tonal curve, gentle highlight roll-off, clean midtones, zero ghost faces or melted bodies.
12. **Leica SL3-P Mirrorless Maestro IV (`leica_sl3_p`)**:
    * *Sensor*: $36.0 \times 24.0\,\text{mm}$ 44.9MP BSI CMOS, Maestro IV processor with L-Mount optics.
    * *Optics*: Leica APO-Summicron-SL 50mm f/2 ASPH, APO-Summicron-SL 75mm f/2 ASPH.
    * *Physics*: Benchmark apochromatic acutance, zero color fringing, prestige documentary reportage.
13. **Panasonic LUMIX S1RII Micro-Science Master (`panasonic_lumix_s1rii`)**:
    * *Sensor*: $35.9 \times 23.9\,\text{mm}$ 44.3MP CMOS with Dual Native ISO (100/640).
    * *Optics*: Lumix S PRO 50mm f/1.4 (Certified by Leica), Lumix S 100mm f/2.8 Macro.
    * *Physics*: 1:1 macro reproduction ratio, micro-relief diffraction suppression, scientific fidelity.
14. **Leica M11 60MP Rangefinder (`leica_m11`)**:
    * *Sensor*: Full-frame 35mm BSI CMOS, zero optical low-pass filter (no AA filter).
    * *Optics*: Leica Summilux-M 35mm f/1.4 ASPH FLE II, Noctilux-M 50mm f/0.95, APO-Summicron 50mm f/2.
    * *Physics*: German aspherical acutance, extreme optical micro-contrast, street reportage realism.
15. **Sony Alpha A7R V 61MP High-Resolution (`sony_a7rv`)**:
    * *Sensor*: Full-frame 61MP Exmor R BSI CMOS.
    * *Optics*: Sony FE 50mm f/1.2 GM, FE 85mm f/1.4 GM II, FE 135mm f/1.8 GM.
    * *Physics*: Modern commercial resolution, razor-sharp G-Master optical acutance.

### Cinema Production & Venice Color Science
16. **Sony FX Cinema Line Full-Frame (`sony_fx_series`)**:
    * *Format*: $35.6 \times 23.8\,\text{mm}$ full-frame cinema 4K Exmor R BSI CMOS, 15+ stops dynamic range.
    * *Optics*: Sony FE 50mm f/1.2 GM stopped down to $f/2.8$ cinematic sweet spot, FE 24-70mm f/2.8 GM II, FE 85mm f/1.4 GM II.
    * *Physics*: Venice color science highlight rolloff, $180^\circ$ cinema shutter angle ($1/48\,\text{s}$ cadence), Dual Base ISO 800/12800, 10-bit 4:2:2 All-Intra S-Log3/S-Gamut3.Cine.
17. **ARRI Alexa 35 Cinema Large-Sensor (`arri_alexa_35`)**:
    * *Format*: Super 35 Native 4K ALEV 4 sensor, Cooke S4/i 50mm T2.0 Prime, ARRI LogC4.

### Analog Film Classics
18. **Hasselblad 500C/M 6x6 Analog Medium Format (`hasselblad_500cm`)**:
    * *Format*: $56 \times 56\,\text{mm}$ square 120 film gate, Carl Zeiss Planar T* 80mm f/2.8 CF.
19. **Pentax 67 II 6x7 Medium Format Film (`pentax_67ii`)**:
    * *Format*: $56 \times 70\,\text{mm}$ oversized negative, SMC Pentax 67 105mm f/2.4 Reference Lens.
20. **Leica M6 Classic 35mm Analog Rangefinder (`leica_m6_analog`)**:
    * *Format*: 35mm silver halide film gate, Leica Summicron-M 50mm f/2 Dual-Range, Kodak Tri-X 400.

---

## 💡 Master Photographic Lighting Presets
Apply physical lighting recipes via `--lighting-preset` or in the Studio UI:
* **`flat_overcast`**: Soft diffused overcast daylight acting as a massive natural softbox, low contrast, gentle highlight roll-off without specular blowouts, perfectly balanced for long blur trails.
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
* **`slow_shutter_crowd_motion`**: Slow shutter motion-blur aesthetic; stationary subject completely still and tack-sharp at eye level while commuters flow in multi-directional motion blur trails (left-to-right, right-to-left, diagonal); zero ghost faces, zero duplicated people, zero melted bodies.
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
  * **102MP Upscaler Lock Modal**: Interactive hardware restoration console with staged Lanczos scaling and 1-click JSON audit copy.
  * **Embedded REST API**: `/api/compile`, `/api/upscale-102mp`, `/api/profiles`, `/api/health` with full CORS support for external frontends.

---

## 🔬 PIL Conservative 102MP Restoration and Upscale Lock

Profile: **`PLATINUM_NO_DRIFT`** (v1.0.0)

A zero-hallucination, reference-faithful hardware-locked restoration and 102MP upscaler built with a pure **`PIL_ONLY`** architecture (strictly prohibiting generative deep learning models, OpenCV, PyTorch, diffusion models, or external hallucination APIs).

### Mathematical & Engineering Guarantees:
* **Exact Rational Aspect Ratio Lock**: Reduces width and height via Greatest Common Divisor ($w_0 / \gcd(w_0, h_0)$) and selects optimal scaling multiplier $k$ to guarantee $w_{\text{out}} \cdot h_0 == h_{\text{out}} \cdot w_0$ (0.000% aspect ratio drift).
* **102 Megapixel Target**: Hits $\approx 102,000,000$ pixels within a strict $\le 1.5\%$ tolerance window (e.g., 4:3 $\rightarrow$ `11660x8745` [101.97MP], 3:2 $\rightarrow$ `12369x8246` [101.99MP], 1:1 $\rightarrow$ `10100x10100` [102.01MP], 16:9 $\rightarrow$ `13472x7578` [102.09MP], 9:11 $\rightarrow$ `9135x11165` [101.99MP]).
* **Staged Conservative Lanczos Resampling**: Executes staged geometric resampling enforcing a maximum linear growth limit of $\le 2.0\times$ per pass to eliminate ringing and sampling distortion.
* **Neutral Micro-Softening & Tonal Cohesion**: Applies conservative Gaussian softening (radius 0.60, blend 0.08) and mild tonal flattening ($\le 0.12$) to suppress JPEG block artifacts and digital noise without altering facial anatomy.
* **Anchored Refinement & Single-Pass UnsharpMask**: Anchored contrast ($1.015\times$) and color ($1.010\times$) with single-pass low-radius UnsharpMask ($r=0.75, p=42, th=5$).
* **Alpha Channel Separation**: Decouples RGBA transparency before scaling, resamples alpha independently via Lanczos, and re-attaches to prevent dark edge fringing.
* **Mandatory Post-Save Verification & 18-Field Audit**: Decodes the written file from disk, verifies byte integrity, validates dimensions, and generates a structured 18-field JSON report.

### CLI Usage:
```bash
# Dedicated entrypoint:
optical-upscaler path/to/my_photo.jpg --format JPEG

# Or via the compiler CLI:
python3 -m optical_compiler --upscale-102mp path/to/my_photo.png --upscale-format PNG
```

### Python API Usage:
```python
from optical_compiler import restore_and_upscale_102mp, calculate_exact_ratio_102mp_dimensions

# Compute exact dimensions
w_out, h_out, total_px, within_tol = calculate_exact_ratio_102mp_dimensions(4000, 3000)
print(f"Target dimensions: {w_out}x{h_out} ({total_px / 1e6:.2f} MP)")

# Run complete 102MP restoration
report = restore_and_upscale_102mp(
    input_path="portrait.jpg",
    output_format="JPEG", # or "PNG", "TIFF"
)
print("102MP Audit Report:", report)
```

### ComfyUI Node:
Includes native node **`🔬 PIL Conservative 102MP Upscaler Lock`** (`OpticalConservative102MPUpscaler`) producing output paths and 18-field telemetry for high-resolution post-processing pipelines.

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
  * `camera_rig`: Select from all 19 camera systems or `auto` (Sony a1 II, Fujifilm GFX100RF, Phase One IQ4, Leica, Hasselblad, ARRI, etc.).
  * `model_target`: `gpt_images`, `imagen`, `midjourney`, `flux`, `sdxl`, `json`, `raw_spec`.
  * `reference_mode`: `disabled`, `transform_adapt`, `restore_upscale`, `outpaint_full_body`, `depixelate_gfx100rf`.
  * `content_type`: `photograph`, `portrait`, `product_photo`, `document_scan`, `poster_or_flyer`, `meme_or_infographic`, `ui_or_screenshot`, `mixed_content`.
  * `human_skin_realism`: `enabled` / `disabled` (prioritizes skin realism over sharpening, bans synthetic pore stamps).
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

### 4. Mode D: Universal De-Pixelate & 102MP Upscale Restoration v3.1
De-pixelate a low-resolution reference image using GFX100RF 102MP signature lock and human skin realism override:
```bash
python3 -m optical_compiler "Restore low-res photo" \
  --depixelate \
  --reference path/to/pixelated_face.jpg \
  --content-type portrait \
  --target gpt_images \
  -c
```

For document scans, infographics, or UI screenshots (enforcing flat copy reproduction with suppressed optical DoF and grain):
```bash
python3 -m optical_compiler "Historical document archive" \
  --depixelate \
  --reference path/to/scanned_map.png \
  --content-type document_scan \
  --target json \
  -c
```

### 5. Mode E: Editorial Calm vs Chaos (Leica SL2 Motion Blur & Identity Lock)
Compile a reference-locked black-and-white portrait with surrounding slow-shutter motion-blurred crowd trails:
```bash
python3 -m optical_compiler "Editorial portrait of a solitary person standing calm and still amid rush-hour chaos" \
  --profile leica_sl2 \
  --reference path/to/person.jpg \
  --ref-mode identity_lock \
  --lighting-preset flat_overcast \
  --capture-mode slow_shutter_crowd_motion \
  --camera-angle "chest-level frontal angle" \
  --crowd-action "hundreds of commuters rushing past in all directions creating smooth motion-blur trails" \
  --bw \
  --ar 4:5 \
  --target gpt_images \
  -c
```

### 6. Mode F: Commercial Packshot (100% SKU Approval Gate & Product-Reference Crop)
Compile a forensic commercial packaging prompt locking cap closure geometry, label kerning, parting seams, material finish, and SKU Pantone color:
```bash
python3 -m optical_compiler "Luxury cosmetic serum bottle on polished dark slate pedestal with natural micro-water droplets" \
  --product-lock \
  --product-crop path/to/serum_bottle_crop.png \
  --cap-geometry "matte black anodized aluminum dropper cap with 48-ridge knurling collar and flush seal" \
  --sku-color "Amber pharmaceutical glass (#8B4513) with Pantone 116 C gold foil" \
  --label-kerning "crisp micro-typography, precise character tracking, zero hallucinated micro-text" \
  --material-finish "heavy-base borosilicate glass, anti-reflective coating, tactile uncoated paper label" \
  --seams "flawless circular base without mold flash, hairline parting seam along shoulder" \
  --target gpt_images \
  -c
```

### 7. Biomechanical Hand Precision Gate (5-Point Grip Lock)
Compile a scene requiring complex hand interaction with strict metacarpal proportions and micro-vascular contact tissue blanching:
```bash
python3 -m optical_compiler "Master horologist delicately placing a tourbillon balance wheel with titanium tweezers" \
  --hand-lock \
  --grip-type precision_pinch \
  --hand-details "translucent nail beds with pale lunula, micro contact blanching on fingertips, zero clipping" \
  --target flux \
  -c
```

### 8. Cinema Anamorphic Optics & Flare Engine (2.0x Squeeze & Cyan Streak Flares)
Compile a cinematic wide frame with ARRI Alexa 35, Cooke Anamorphic glass, vertical oval bokeh, and chromatic streak flares:
```bash
python3 -m optical_compiler "Neon-drenched cyberpunk detective gazing through rain-slicked windshield at midnight" \
  --anamorphic \
  --squeeze 2.0x \
  --streak-flare cyan_blue \
  --iris-blades 14_blade_circular \
  --target midjourney \
  -c
```

### 9. Commercial Advertising Suite (Gobo Cookies, Grip, & Copy-Space Safe-Zone)
Compile a billboard-ready advertising layout with architectural window gobo shadows, 4:1 key-to-fill ratio, and left-third negative space:
```bash
python3 -m optical_compiler "Elegantly sculpted perfume bottle standing on polished travertine marble" \
  --gobo venetian_blinds \
  --grip beauty_dish_honeycomb \
  --lighting-ratio 4:1 \
  --copy-space left_third \
  --ad-safe-zone instagram_feed_4_5 \
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
