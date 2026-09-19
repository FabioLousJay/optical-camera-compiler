# Optical Camera Compiler 📷⚡

[![CI](https://github.com/FabioLousJay/optical-camera-compiler/actions/workflows/ci.yml/badge.svg)](https://github.com/FabioLousJay/optical-camera-compiler/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Version: 3.9.3](https://img.shields.io/badge/version-3.9.3-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 255 Passing](https://img.shields.io/badge/tests-255%20passing-brightgreen.svg)](tests/)
[![ComfyUI: Supported](https://img.shields.io/badge/ComfyUI-Custom%20Node-blueviolet.svg)](#comfyui-custom-node-integration)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20runtime-success.svg)](pyproject.toml)
[![Targets](https://img.shields.io/badge/engines-GPT%20Images%20%7C%20Gemini%20%7C%20Midjourney%20%7C%20Flux%20%7C%20SDXL%20%7C%20JSON-orange.svg)](#supported-target-adapters)

> **Deterministic Hardware-Level Optical Simulation for Zero-Artifact Photorealism**

The **Optical Camera Compiler** bridges the gap between artistic creative intent and modern AI image models (**ChatGPT / GPT Images**, **Google Gemini / Imagen 3**, **Midjourney v8.2**, **Flux.1**, **Adobe Firefly**, **SDXL**, **Runway**, **HUMAIN**). Instead of using buzzwords like *"photorealistic, 8k, masterpiece"*, which trigger synthetic 3D-render, airbrushing, and stock-photo biases, this compiler compiles descriptive intent into physical laws of optics, sensor silicon, lighting transport, and rigorous anti-drift shields.

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

## 🌟 New in v3.9.3: AI Rig Advisor ("Your Prompt") & 3-Tier Multi-Rig Recommendation Engine

When creating prompts in the Web Studio, photographers and creators no longer need to know all 33+ camera bodies and lenses. Positioned **directly before "Camera Style"** in the top Scenario Bar is the **"Your Prompt" (AI Rig Advisor)**.

### Core Capabilities:
1. **Intelligent Scene Intent Extraction**:
   Automatically analyzes scene genre (portrait, street, architecture, wildlife, sports/action, macro, cinema, landscape, documentary), extracted subject entities, lighting cues, depth/scale, and motion dynamics.
2. **Top 3 Diverse Optical Recommendations**:
   - **🥇 1st Best (Primary Optical Master)**: Highest optical MTF sharpness and resolving authority tailored to the genre.
   - **🥈 2nd Best (Distinct Aesthetic)**: Distinct alternative medium (e.g. analog film stock, classic rangefinder, or tonal master).
   - **🥉 3rd Best (High-Character / Creative Rig)**: Expressive optical character (e.g. large format bellows, cinema anamorphic with streak flare, or high-speed freeze).
3. **Automated Anti-Drift & Anti-Hallucination Quality Gate**:
   - **Anti-Drift Verification**: 100% preservation of all user subjects, entities, and actions.
   - **Strict Zero-Artist Compliance**: Automated scan against 100+ famous artists, photographers, and directors to guarantee zero artist-name hallucination.
   - **Physical Optics Validation**: Validates real-world lens, aperture, shutter speed, and sensor format combinations from `LENS_CATALOG`.
   - **Negative Shield Defense**: Verifies non-toxic negative prompt constraints to protect Midjourney and Firefly from degraded geometry.
4. **One-Click "⚡ Apply & Compile" in Web Studio**:
   Populates all studio dials and immediately compiles prompts across all 8 models simultaneously.

### Python SDK & CLI:
```python
from optical_compiler import recommend_rigs

recs = recommend_rigs("A master watchmaker assembling gears under raking afternoon light")
for r in recs:
    print(f"[{r.tier_name}] {r.camera_name} // {r.lens}")
    print(f"Quality Gate: {r.quality_gate.summary}")
```

```bash
optical-compiler recommend "A cheetah sprinting across the savannah at sunset"
```


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

## Reference Image Pipeline (Modes A, B, C, D, E, F, G, H, & I)

Attach any reference image from your **local hardware** (drag & drop or file select) into the compiler to unlock nine production workflows:

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

### 🏔️ Mode G: Professional 4X Reconstruction Lock Protocol v3.6 (`recon_4x` / `--recon-4x`)
Delivers defensible, museum-grade 4X super-resolution upscaling and reconstruction for luxury landscape photography, fine art, and synthetic photography (synthography):
* **Exact 4X Linear Expansion ($W_{\text{out}} = 4W_0, H_{\text{out}} = 4H_0$)**: Exactly 16X pixel area expansion. Resolves the critical industry failure mode where "upscalers" simply interpolate and enlarge file size without adding genuine photographic microstructure.
* **Super-Resolution Decision Matrix (`--sr-backend`)**:
  * `realesrnet_x4plus` (*Master Baseline / Default*): Maximum source structural fidelity, zero hallucinated micro-geometry.
  * `swinir_m_x4`: Transformer-based real-world SR with balanced acutance and controlled micro-detail.
  * `realesrgan_x4v3` (*with `-dn 0.15`*): Low denoising strength prevents loss of delicate surface textures.
  * `hat_s_x4`: Hierarchical Attention Transformer for structural edge definition.
  * *Explicit Rejection of SUPIR / Diffusion Upscalers*: Diffusion restoration models (SUPIR, etc.) are strictly prohibited due to generative hallucination, terrain alteration, and structural drift.
* **Frequency Separation & Sky / Atmospheric Haze Protection (`--protect-sky` / `--no-protect-sky`)**: Generates an adaptive luminance difference mask that excludes smooth gradients (sky, clouds, fog, horizon haze) from high-frequency sharpening and micro-noise injection, preventing halos and artificial sky grain.
* **Selective Detail Blend (`--sr-blend 0.20`)**: Blends 15%–30% of high-frequency texture strictly into structured surfaces (rock strata, tree foliage, fabric weave).
* **Anti-Model Stacking Law**: Prohibits compounding generative errors by running one super-resolution pass sequentially onto another.
* **Cryptographic Provenance & Audit Reports**: Generates deterministic SHA-256 hashes, `PROVENANCE.json`, and `RECONSTRUCTION_REPORT.md` alongside lossless master outputs (PNG, TIFF, JPEG).
* **CLI Execution**:
  ```bash
  optical-compiler "Sandstone ridges at sunset" --recon-4x inputs/landscape.png --sr-backend swinir_m_x4 --sr-denoise 0.15 --sr-blend 0.20
  ```

### 💎 Mode H: Universal High-Resolution PNG Output Lock v1.0 & 4× Upscale Workflow (`universal_png_lock` / `--png-lock` / `optical-png-lock`)
Eliminates synthetic palette reduction, indexed-color quantization, and compression damage by locking generators and post-processors into true full-color uncompressed RGB raster pipelines:
* **Zero Forced Palette Reduction**: Strictly prohibits 8-bit palette degradation, color quantization, color simplification, muddy gradient banding, posterization, and watercolor-like smearing.
* **Master High-Resolution Enforcements**: Directs models toward ultra-high pixel grids (`11648 x 6552`, `7680 x 4320`) with crisp micro-detail, clear edge separation, and full tonal dynamic range.
* **Uncompressed Full-Color Raster Export**: Pure RGB PNG output saved with `compress_level=0` and `optimize=False`, targeting minimum uncompressed file footprints ($\ge 12\,\text{MB}$ raster baseline; never sacrificing visual acutance to hit a target).
* **Mandatory 6-Step 4× Upscale Pipeline**:
  1. Generate or edit the base visual.
  2. Inspect output dimensions and color space.
  3. Apply 4× pixel upscale post-process (Lanczos resampling + subtle acuity restoration: `ImageFilter.UnsharpMask(radius=1.1, percent=85, threshold=3)`).
  4. Export as uncompressed full-color RGB PNG (`compress_level=0`, `optimize=False`).
  5. Provide final downloadable file.
  6. Standard delivery confirmation callout:
     ```text
     Done ✅ 4× full-color PNG upscale: [width] × [height] px, RGB PNG, [file size] MB.
     ```
* **Strict Correction Verbiage**: Automatically deploys failure-recovery prompts if a generator attempts to bypass the locked delivery:
  > *"You missed the locked delivery workflow. Apply the internal 4× full-color RGB PNG upscale now, export the final PNG, and report the final pixel dimensions, color mode, and file size."*
* **Layered Negative Shield Suppression**: Hard suppresses `forced palette reduction`, `indexed-color PNG`, `palette quantization`, `color simplification`, `mushy surfaces`, `watercolor-like smearing`, `fake oversharpening halos`, `muddy gradients`, `posterization`, `lossy PNG compression`, `flattened textures`, and `compression damage`.

### 🔍 Mode I: Universal De-Pixelate + Upscale Restoration Protocol v2.0 (`depixelate_v2` / `--depixelate-v2` / `--depix-v2`)
Reference-guided image restoration and resolution enhancement removing pixelation, compression damage, aliasing, and mosquito noise while preserving authentic identity, typography, structured layouts, and scene integrity:
* **Reference as Absolute Source of Truth**: Preserves exact subject identity, layout, colors, lighting logic, and materials without reimagining, restyling, or rewriting the scene.
* **4-Step Content-Specific Repair Chains**:
  * `photograph` / `portrait`: Geometry & anatomy stabilization $\rightarrow$ Texture recovery $\rightarrow$ Dynamic range restoration $\rightarrow$ Micro-contrast refinement.
  * `product_photo`: Geometry lock $\rightarrow$ Edge crispness $\rightarrow$ Material finish/sheen $\rightarrow$ Label/specular clarity.
  * `document_scan` / `ui_or_screenshot`: Grid/layout registration $\rightarrow$ OCR stroke reconstruction $\rightarrow$ High-contrast binarization $\rightarrow$ Artifact removal.
  * `poster_or_flyer` / `meme_or_infographic`: Composition boundaries $\rightarrow$ Typography legibility $\rightarrow$ Graphic element sharpening $\rightarrow$ Color block de-noising.
* **Text Preservation & OCR Safety Protocol**:
  * Text content, capitalization, spelling, font weight, and placement must match the reference exactly.
  * Prohibits hallucinating new text, translating, rewriting, or substituting decorative glyphs.
  * Blurry or illegible text must be sharpened into its most probable actual characters; if unresolvable, rendered as authentic low-contrast unreadable text rather than invented nonsense words.
* **Structured Graphics Preservation**:
  * Straight lines remain straight and parallel; circles, rounded rects, and geometric curves remain smooth and non-wobbly.
  * Vector-like shapes, icons, and UI elements render with crisp boundaries, clean fills, and zero bleeding.
* **Confidence-Based Detail Reconstruction (`evidence_proportional`)**:
  * High-confidence areas: reconstruct full realistic micro-detail.
  * Medium-confidence areas: plausible detail consistent with surroundings.
  * Low-confidence / severely degraded areas: smooth conservative transitions, never hallucinate specific objects, faces, logos, or words.
* **Layered Anti-Restyling Negative Shield**: Hard negative tokens suppress `restyling`, `rewriting`, `reimagining`, `stylization`, `hallucinated text`, `hallucinated logos`, `AI gloss`, `plastic sheen`, `over-smoothing`, `geometric wobble`, and `cartoonish illustration`.
* **Hardware Profile Auto-Routing**:
  * Monochrome / B&W scenes $\rightarrow$ **Leica Q3 Monochrom** (60.3MP zero-CFA sensor + Summilux 28mm f/1.7 ASPH).
  * Flat graphics, document scans, UI screenshots, infographics, posters $\rightarrow$ **Sony Alpha 7R V** (61MP BSI CMOS + Sony 55mm f/1.8 Sonnar T* FE ZA).
* **CLI Execution**:
  ```bash
  python3 -m optical_compiler "Historical portrait with JPEG compression damage" \
    --depixelate-v2 \
    --ref-img vintage_scan.jpg \
    --target gpt_images \
    -c
  ```

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

### 6. 🔒 Closed-Loop Resolution Engine & Provenance Lab (v3.5)
* **Non-Negotiable File Size Enforcement (`--min-mb [MB]`)**:
  Enforces hard raster payload constraints (e.g. `--min-mb 8.0`) so that AI upscalers and export engines cannot silently deliver undersized outputs.
* **Iterative Square-Root Sizing Heuristic**:
  $$\text{linear multiplier} \approx \sqrt{\frac{\text{target MB}}{\text{current MB}}}$$
  Automatically re-samples raster dimensions across iterative passes until the exact byte threshold is satisfied.
* **Practical Export Profiles (`--export-profile` / `-ep`)**:
  * **Profile A**: $4000 \times 6000\text{ px}$ ($24\text{ MP}$), mobile-manageable high-resolution output.
  * **Profile B**: $5000 \times 7500\text{ px}$ ($37.5\text{ MP}$), large print & desktop output.
  * **Profile C**: $6000 \times 9000\text{ px}$ ($54\text{ MP}$), archival museum-grade master.
* **Cryptographic SHA-256 Provenance & Audit Reports**:
  Every closed-loop export generates an `EXPORT_REPORT.md` and `PROVENANCE.json` containing:
  * Exact source & output pixel dimensions and target PPI
  * Encoded byte counts & file size in MB
  * Cryptographic SHA-256 digest (`sha256_file`)
  * Programmatic assertion status and execution runtime
* **Controlled Micro-Noise Entropy Experiment (`add_micro_noise` / `--add-micro-noise`)**:
  Injects subtle single-channel high-frequency entropy explicitly treated and documented as an entropy experiment for lossless PNG compression benchmarking (not artificial optical detail).
* **Automated CI Workflow**: `.github/workflows/export.yml` provides GitHub Actions pipeline with `workflow_dispatch` for automated validation and artifact publishing.

### 7. 🎯 Portrait Fidelity Engineering Protocol (PFEP v1.0) & 10 Stress Probes
* **10 Canonical Diagnostic Probes (`--probe` / `-k`)**:
  1. `master_portrait_lock`: Baseline reference anchor for identity, optics, and lighting.
  2. `outpaint_lens_honest`: Full-body outpaint under locked camera height, distance, and 85mm compression.
  3. `stress_hard_key`: Harsh 50–60° key light with near-zero fill and deep negative fill to test pore retention in shadows.
  4. `stress_cross_polarized`: Cross-polarized studio lighting emulation; suppresses specular glare to test subsurface melanin and blood micro-chroma.
  5. `stress_glasses_reflections`: Multi-element lens reflection realism; eyes and pupils visible through spectacles without opaque white rectangles.
  6. `stress_seated_compression`: Seated posture compression lock; tests for improper camera height shifts or perspective stretching.
  7. `stress_standing_compression`: Standing upright compression lock; enforces identical spatial compression to seated variant.
  8. `stress_background_scale`: Background scale invariance under locked optics; prevents FOV widening or background shrinkage.
  9. `stress_hair_specular`: 55–65° directional rim/key lighting; tests anisotropic specular response across individual hair fibers (no helmet hair).
  10. `stress_shadow_color`: Shadow-side skin color accuracy; tests for organic warm undertones and eliminates synthetic gray/cyan contamination.
* **8-Axis Renderer Scorecard (`RendererScorecard`) with Identity Hard Gate**:
  * Evaluates: Identity, Focus, Skin Texture, Lighting Honesty, Glasses, Hair, Geometry, Background Scale (0–2 per axis, max 16).
  * **Hard Gating Rule**: Identity MUST be 2 (`identity == 2`) and total score $\ge 12$ to pass. Identity drift is non-recoverable.
* **Automated Project Scaffolding (`--init-pfep [DIR]`)**:
  Generates complete PFEP directory structure: `00_inputs/`, `01_prompts/` (with all 10 compact prompt files), `02_runs/run_001/notes.md`, `03_selected/`, `04_converged/`, and `PFEP_README.md`.
* **Gallery Exhibition Systems**:
  * **Lighting Environment Compensation (`--cct`, `--lux`, `--cri`, `--wall-surround`)**: Simulates reflective gallery display conditions (Kelvin CCT, illuminance lux, TM-30/CRI, surround reflectance).
  * **Series Cohesion Matrix (`--anchor-id`, `--gallery-zone`)**: Synchronizes midtone density, shadow depth, and highlight roll-off across multi-room gallery installations.

---

## 📷 Medium Format Tri-Signature Architecture & Universal Master Override

The compiler provides three distinctly characterized Medium Format photographic signatures anchored in verified manufacturer hardware specifications and explicit rendering emulation logic (rather than raw spec sheets or prompt theater).

| Module | Camera System & Lens | Verified Hardware Anchors | Photographic Signature | Emulation Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Module A** | **Phase One XF + IQ4 150MP** + Schneider Kreuznach 110mm LS f/2.8 Blue Ring | 151MP BSI CMOS (53.4 × 40.0mm), 14,204 × 10,652, 3.76µm pixel pitch, 16-bit Opticolor+, ISO 50, 15 stops DR, f/5.6–f/8 sweet spot | **Maximum Resolving Authority** | Resolving authority on skin micro-relief, fine vellus hair, beard follicles, and fabric weave; dense neutral blacks with retained shadow detail; crisp edge MTF acutance without digital oversharpening. |
| **Module B** | **Hasselblad X2D II 100C** + Hasselblad XCD 2.5/90V | 100MP BSI CMOS (43.8 × 32.9mm), 11,656 × 8,742, 3.76µm pixel pitch, 16-bit color, native ISO 50, 15.3 stops DR, 71mm FF equiv, 1/4000s leaf shutter sync | **HNCS HDR Tonal Realism** | Hasselblad Natural Colour Solution (HNCS); luminous highlight roll-off without digital clipping; color retention in deep shadows without noise; smooth skin gradation (skin never the sharpest texture in frame). |
| **Module C** | **Fujifilm GFX100 II** + Fujinon GF110mmF2 R LM WR | 102MP GFX CMOS II HS (43.8 × 32.9mm), 14/16-bit RAW, ISO 80–12,800 (ISO 40 ext), 8-stop IBIS, 87mm FF equiv, 14 elements in 9 groups w/ 4 ED elements | **Portrait Precision & Compression** | Classic 87mm portrait perspective compression; natural facial volume preservation without 2D flattening; proportional extremities (hands and feet do not enlarge toward camera); tack-sharp eye focus. |

### 🛡️ Universal Master Override (`UNIVERSAL_MEDIUM_FORMAT_PORTRAIT_OVERRIDE`)

When working with medium-format portraits, generative AI engines frequently over-sharpen skin, crush shadows to create fake contrast, or introduce anatomical drift. The Universal Master Override enforces non-negotiable physical rules:

1. **Resolution Rule**: Generate genuine-looking high-frequency detail only where optics, focal depth, subject distance, and lighting physically support it.
2. **Skin Realism Rule**: Skin realism strictly overrides sharpening. Skin must remain softer than eyes, hair, clothing, jewelry, and text.
3. **Hair Resolution Rule**: Hair may resolve more sharply than skin only when within the true optical focal plane.
4. **HDR & Tonal Rule**: HDR means expanded recoverable dynamic range, not halos, flat shadows, or tone-mapped skin.
5. **Black Point Rule**: Dense neutral blacks with readable low-frequency texture; no lifted muddy grays or artificial shadow crushing.
6. **Sharpness Hierarchy Rule**: Eyes, eyelashes, eyebrows, hair, beard, jewelry, fabric edges, and text carry stronger high-frequency contrast than skin.
7. **Optical Depth Rule**: Progressive optical depth of field transition; no artificial computational segmentation-mask blur.
8. **Detail Plausibility Rule**: Zero hallucinated microscopic detail unsupported by distance or focal plane.
9. **Anatomy & Identity Lock Rule**: Zero changes to anatomy, age, facial geometry, body proportions, or limb scales.

### 🧪 3-Way Side-by-Side Comparison Harness (`compile_abc_harness`)

Evaluate all three medium format signatures simultaneously on identical scene prompts across any supported engine:

```python
from optical_compiler import compile_abc_harness

harness = compile_abc_harness(
    "Editorial three-quarter portrait of an artisan examining raw materials in natural studio light",
    target="gpt_images",
    universal_override=True,
)

print(harness["module_a"].positive_prompt)  # Phase One 151MP Resolving Authority
print(harness["module_b"].positive_prompt)  # Hasselblad 100MP HNCS Tonal Realism
print(harness["module_c"].positive_prompt)  # Fujifilm GFX100 II 87mm Portrait Precision
```

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
   * *Sensor*: $36.0 \times 24.0\,\text{mm}$ 45.0MP back-illuminated stacked CMOS, 8K 60p RAW video capture.
   * *Optics*: Canon RF 85mm F1.2L USM at $f/5.6$ sweet spot, RF 100mm f/2.8L Macro IS USM, RF 50mm F1.2L USM, RF 135mm F1.8L IS USM.
   * *Physics*: Accelerated capture architecture, 8K 60p motion resolution, organic skin tonal gradation, dual-pixel micro-contrast.
4. **Canon EOS R6 Mark III All-Rounder Full-Frame (`canon_eos_r6_iii`)**:
   * *Sensor*: $36.0 \times 24.0\,\text{mm}$ 32.5MP full-frame CMOS, 7K 60p oversampled video capture.
   * *Optics*: Canon RF 24-70mm F2.8L IS USM at $f/4.0$ sweet spot, RF 70-200mm F2.8L IS USM, RF 50mm F1.2L USM, RF 85mm F1.2L USM.
   * *Physics*: Top-of-the-class all-rounder, pairing 32.5MP resolution with next-generation deep-learning autofocus tracking and rich highlight retention.
5. **Nikon Z 5 II All-Rounder Full-Frame (`nikon_z5_ii`)**:
   * *Sensor*: $35.9 \times 23.9\,\text{mm}$ 24.0MP full-frame CMOS, 4K 60p video capture.
   * *Optics*: NIKKOR Z 24-70mm f/4 S at $f/5.6$ sweet spot, Z 50mm f/1.8 S, Z 24-120mm f/4 S, Z 85mm f/1.8 S.
   * *Physics*: Fantastic all-rounder for a variety of photographers, fully-articulating touchscreen flexibility, organic dermal micro-relief, and exceptional value.
6. **Nikon Z 9 Stacked Flagship Full-Frame (`nikon_z9`)**:
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
16. **Leica Q3 Monochrom Fixed-Lens Full-Frame (`leica_q3_monochrom`)**:
    * *Sensor*: $36.0 \times 24.0\,\text{mm}$ 60.3MP BSI CMOS monochrome sensor (zero Color Filter Array / no Bayer matrix, no OLPF), Maestro IV processor, Base ISO 125.
    * *Optics*: Fixed Leica Summilux 28mm f/1.7 ASPH with integrated macro ring down to 17cm, digital crop modes (28/35/50/75/90mm).
    * *Physics*: Pure luminance capture with zero demosaicing interpolation, extreme optical micro-contrast, true tonal graduation from deep obsidian black to brilliant specular white, uncompressed 14-bit DNG raw.

### Cinema Production & Venice Color Science
17. **Sony FX Cinema Line Full-Frame (`sony_fx_series`)**:
    * *Format*: $35.6 \times 23.8\,\text{mm}$ full-frame cinema 4K Exmor R BSI CMOS, 15+ stops dynamic range.
    * *Optics*: Sony FE 50mm f/1.2 GM stopped down to $f/2.8$ cinematic sweet spot, FE 24-70mm f/2.8 GM II, FE 85mm f/1.4 GM II.
    * *Physics*: Venice color science highlight rolloff, $180^\circ$ cinema shutter angle ($1/48\,\text{s}$ cadence), Dual Base ISO 800/12800, 10-bit 4:2:2 All-Intra S-Log3/S-Gamut3.Cine.
18. **ARRI Alexa 35 Cinema Large-Sensor (`arri_alexa_35`)**:
    * *Format*: Super 35 Native 4K ALEV 4 sensor, Cooke S4/i 50mm T2.0 Prime, ARRI LogC4.

### Analog Film Classics
19. **Hasselblad 500C/M 6x6 Analog Medium Format (`hasselblad_500cm`)**:
    * *Format*: $56 \times 56\,\text{mm}$ square 120 film gate, Carl Zeiss Planar T* 80mm f/2.8 CF.
20. **Pentax 67 II 6x7 Medium Format Film (`pentax_67ii`)**:
    * *Format*: $56 \times 70\,\text{mm}$ oversized negative, SMC Pentax 67 105mm f/2.4 Reference Lens.
21. **Leica M6 Classic 35mm Analog Rangefinder (`leica_m6_analog`)**:
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
* **Add Node ➔ prompt/optical ➔ 📷 Optical Camera Compiler**
  * `positive_prompt` ➔ Pipe directly into `CLIP Text Encode (Prompt)`
  * `negative_prompt` ➔ Pipe into `CLIP Text Encode (Negative)`
  * `unified_payload` ➔ Full prompt with negative shield for single-prompt nodes (GPT / Flux.1 / Midjourney)
  * Controls: `camera_rig` (19 systems or `auto`), `model_target`, `reference_mode` (`disabled`, `transform_adapt`, `restore_upscale`, `outpaint_full_body`, `depixelate_gfx100rf`, `product_lock`, `reconstruction_lock_4x`, `universal_png_lock`), `content_type`, `human_skin_realism`, `aspect_ratio`.
* **Add Node ➔ upscale/optical ➔ 🔬 Optical 4X Reconstruction Lock**
  * Dedicated high-fidelity image super-resolution execution node.
  * Inputs: `image_path`, `backend` (`realesrnet_x4plus`, `swinir_m_x4`, `realesrgan_x4v3`, `hat_s_x4`), `denoise_strength`, `blend_ratio`, `protect_sky_haze`, `output_format`.
  * Outputs: `output_image_path`, `reconstruction_report_md`.
* **Add Node ➔ upscale/optical ➔ 💎 4X Full-Color PNG Output Lock Upscaler**
  * Native 4× full-color uncompressed RGB PNG upscale node (`Optical4XFullColorPNGUpscaleNode`).
  * Inputs: `image_path`, `unsharp_radius` (default 1.1), `unsharp_percent` (default 85), `unsharp_threshold` (default 3), `compress_level` (default 0), `target_min_mb` (default 12.0), `output_path`.
  * Outputs: `output_image_path`, `upscale_report_md`, `delivery_callout`.
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

### 10. Mode H: Universal High-Resolution PNG Output Lock & Standalone 4X Upscaler
Compile a prompt with full-color uncompressed PNG output lock and negative palette suppression:
```bash
python3 -m optical_compiler "Architectural interior of a minimalist brutalist villa" \
  --png-lock \
  --target gpt_images \
  -c
```

Or execute the standalone 4× full-color RGB PNG upscale workflow directly on any existing render or photo:
```bash
# Using the dedicated entrypoint
optical-png-lock input_render.png

# Or via the compiler CLI flag
python3 -m optical_compiler --png-upscale-4x input_render.png
```
Outputs an uncompressed 4× upscale ($4W \times 4H$), writes `PNG_UPSCALE_REPORT.md` and `PROVENANCE.json`, and delivers the standard confirmation callout:
```text
Done ✅ 4× full-color PNG upscale: 4096 × 4096 px, RGB PNG, 48.00 MB.
```

### 11. Studio Web API: PNG Lock Upscale Endpoint
Run the optical compiler local studio:
```bash
python3 -m optical_compiler.web --port 8000
```
POST to `/api/png-lock-upscale`:
```json
{
  "image_path": "path/to/image.png",
  "unsharp_radius": 1.1,
  "unsharp_percent": 85,
  "unsharp_threshold": 3,
  "compress_level": 0,
  "target_min_mb": 12.0
}
```
Returns `{ "status": "success", "report": { ... }, "delivery_callout": "Done ✅ ..." }`.

### 12. Mode I: Universal De-Pixelate + Upscale Restoration v2.0
Compile a prompt for reference-guided restoration and resolution enhancement:
```bash
# Monochrome restoration with automatic Leica Q3 Monochrom routing
python3 -m optical_compiler "Restoration of a damaged vintage archive negative" \
  --depixelate-v2 \
  --ref-img vintage_scan.jpg \
  --target gpt_images \
  -c

# Flat graphic reproduction with automatic Sony Alpha 7R V routing
python3 -m optical_compiler "High-resolution restoration of a vintage promotional poster" \
  --depixelate-v2 \
  --content-type poster_or_flyer \
  --ref-img poster_lowres.png \
  --target imagen \
  -c

# Custom approved camera and lens selection
python3 -m optical_compiler "De-pixelate damaged product packaging photo" \
  --depixelate-v2 \
  --depix-camera "Sony Alpha 7R V" \
  --depix-lens "Sony 55mm f/1.8 Sonnar T FE ZA" \
  --ref-img product_blurry.jpg \
  --target midjourney \
  -c
```

### 13. Web Studio Console: Organized Camera Style & Ambient Style Dropdowns
The Web Studio interactive console (`python3 -m optical_compiler.web --port 8000`) features categorized dual dropdowns for modular prompt engineering:
* **📷 Camera Style Dropdown (38 Hardware Rigs & Curated Presets)**:
  * **Medium Format Rigs**: Phase One XF IQ4 150MP, Hasselblad H6D-100c, Hasselblad X2D II 100C, Fujifilm GFX 100 II, FUJIFILM GFX100RF, Contax 645 (Zeiss Planar 80mm f/2), Mamiya RZ67 (140mm Macro).
  * **Leica & Film Look**: Leica M11 60MP (FLE II, Noctilux-M 50mm f/0.95 & 75mm f/1.25, APO-Summicron-M 50mm & 90mm f/2, Summilux-M 35mm ASPH II), Leica M6 Analog, Leica Q3 Monochrom (60MP monochrome, native ISO 100-200,000, 28/35/50/75/90mm crops), Leica SL2, Leica SL3-P Flagship (APO-Summicron-SL 50mm & 90mm f/2 ASPH), Nikon FM2 (Nikkor 105mm f/2.5 AI-S, Kodachrome 64).
  * **Wildlife & Action Systems**: Nikon Z 9 Stacked Flagship (NIKKOR Z 135mm f/1.8 Plena & Arctic Fox 400mm f/2.8), Canon EOS R1 (24-70mm & Track and Field 400mm f/2.8).
  * **Cinema & Panoramic Optics**: ARRI Alexa 35 (Cooke Look & 2.0x Anamorphic Scope), ARRI Alexa 265 (65mm Sensor, 15 Stops DR), IMAX MSM 9802 (15-Perf 65mm Motion Picture Film, Kodak Double-X 5222), Sony VENICE 2 Full-Frame (Venice S-Cinetone Noir), Hasselblad XPan (24x65mm Panoramic 2.7:1).
  * **Analog Sheet Film & Historic Formats**: Linhof Master Technika 4x5, Deardorff 8x10 (Schneider Symmar-S 360mm, Tri-X 320 Seamless), Antique View 8x10 (Wet-Plate Collodion on Glass, Brass Petzval), Pentax 67 II (105mm f/2.4), Hasselblad 500C/M, Polaroid 20x24 (Schneider 600mm, Polacolor Life-Size Contact).
  * **Iconic Compacts & Street**: Contax T2 (Zeiss Sonnar 38mm f/2.8 T*, Direct On-Camera Flash), Ricoh GR IV (25.7MP APS-C, GR 18.3mm f/2.8, 28mm Snap Street).
  * **Aerial Systems**: DJI Mavic 4 Pro (100MP 4/3 Hasselblad Sensor, 28mm-Equiv Nadir Aerial).
  * **Skin, Eyes & Hyperreal Macro Rigs**: Canon EOS R5 Mark II (RF 100mm f/2.8L Macro @ f/8.0, Micro-Pore Dermal Lock), Phase One IQ4 150MP (Schneider 120mm f/4 Macro @ f/8.0, Zero-Smoothing Forensic Dermal Lock).
* **🌤️ Ambient Style Dropdown**:
  * **Cities & Urban Streetscapes**: Parisian Saint-Germain, Tokyo Shinjuku neon alleys, New York SoHo lofts, London Mayfair mews, Milan Brera porticos, Kyoto Gion twilight, Berlin Mitte concrete.
  * **Luxury Hospitality**: Amalfi Coast villa terraces, Manhattan modernist penthouses, Parisian Grand Palace lobbies, Kyoto luxury ryokans, Saint-Moritz alpine chalets, intimate speakeasy cocktail lounges.
  * **Coastal & Maritime**: Mediterranean white cliffsides, Atlantic ocean sand dunes, Nordic fjords, Polynesian tropical lagoons, Big Sur marine layer bluffs.
  * **Rural Landscapes & Wild Terroir**: Tuscan Chianti vineyards, Pacific Northwest pine forests, Cotswolds cottage gardens, Mojave sandstone plateaus, Scottish Highland moors.
  * **Commercial Studio & Exhibition**: Cosmetic packshots with water droplets, Haute Couture infinity coves with Para 220, Carrara sculptor ateliers, watchmaker micro-benches, museum rotundas, Venetian gobo hero shots.
  * **Mastery Protocols**: 4D liquid glass & latex, heavyweight body morphology, Baryta fine art prepress, Universal De-Pixelate v2.0 OCR safety, pure monochromatic luminance.
* **↺ Clear / Build Your Own**: One-click action wiping all parameters and resetting dropdowns to let users construct custom prompts completely from scratch.

### 14. Global City Roster & Geographic Architectural Vibes
The Web Studio Section 02 (`Scene & Styling`) separates geographic location from architectural atmosphere into **two dedicated, coordinated dropdowns**:
* **🌍 Country / City Dropdown (130+ Global Hubs in 7 Regional Optgroups)**:
  * **United States (18 cities)**: New York City, Los Angeles, Chicago, San Francisco, Miami, Seattle, Boston, Austin, New Orleans, Las Vegas, Nashville, Philadelphia, Washington D.C., Denver, Portland, Atlanta, Honolulu, Santa Fe.
  * **Canada (11 cities)**: Toronto, Vancouver, Montreal, Quebec City, Calgary, Ottawa, Victoria, Banff, Halifax, Edmonton, Winnipeg.
  * **Brazil (12 cities)**: Rio de Janeiro, São Paulo, Salvador da Bahia, Brasília, Curitiba, Florianópolis, Belo Horizonte, Manaus, Recife, Paraty, Ouro Preto, Fortaleza.
  * **Europe (34 cities)**: Paris, London, Milan, Rome, Florence, Venice, Berlin, Amsterdam, Barcelona, Madrid, Lisbon, Porto, Vienna, Prague, Budapest, Edinburgh, Dublin, Copenhagen, Stockholm, Oslo, Helsinki, Reykjavik, Zurich, Geneva, Munich, Athens, Santorini, Dubrovnik, Warsaw, Brussels, Bruges, Monaco, Seville, Krakow.
  * **Asia (22 cities)**: Tokyo, Kyoto, Osaka, Seoul, Busan, Singapore, Bangkok, Chiang Mai, Mumbai, New Delhi, Hong Kong, Taipei, Shanghai, Beijing, Ho Chi Minh City, Hanoi, Kuala Lumpur, Jakarta, Bali (Ubud), Manila, Colombo, Kathmandu.
  * **Oceania (12 cities)**: Sydney, Melbourne, Brisbane, Perth, Adelaide, Hobart, Gold Coast, Auckland, Wellington, Queenstown, Christchurch, Suva (Fiji).
  * **The Orient (22 cities)**: Istanbul, Dubai, Abu Dhabi, Doha, Muscat, Riyadh, AlUla, Cairo, Alexandria, Luxor, Marrakech, Casablanca, Fes, Beirut, Amman, Petra, Jerusalem, Samarkand, Bukhara, Isfahan, Baku, Tbilisi.
* **🏛️ Geographic Vibe Dropdown (25+ Curated Architectural & Environmental Archetypes)**:
  * **Historic & Classical Architecture**: Haussmannian Limestone, Cast-Iron SoHo, Refined Georgian Brick, Classical Marble Porticos, Medieval Fortress Stone, Baroque Colonial Stucco & Azulejos, Gothic Sandstone Spires.
  * **Modern, Industrial & Urban Atmosphere**: Modernist Glass Skyscrapers, Industrial Red-Brick Warehouses, Brutalist Concrete Monoliths, Art Deco Brass & Terrazzo, Sprawling Megacity Flyovers, Rain-Slicked Narrow Neon Alleys, Steamy Urban Noir Sodium Vapor.
  * **Regional, Coastal & Environmental Archetypes**: Mediterranean Whitewash & Azure Horizon, Tuscan Terracotta & Cypress Avenues, Traditional Cedar Timber Lattice, Desert Sandstone Oasis & Adobe, Tropical Oceanfront Palms, Active Maritime Wharves, High Alpine Schist & Timber, Nordic Minimalist Granite & Pine, Subtropical Courtyards & Tiered Fountains, Foggy River Embankment Viaducts, Oriental Zellij Geometric Mosaics.
* **⚡ Decoupled Combinatorial Prompting**: Easily pair any city with diverse architectural aesthetics (e.g. *Tokyo + Narrow Neon Alleys* vs. *Tokyo + Traditional Cedar Lattice* vs. *Tokyo + Modernist Glass Skyscrapers*) with automatic prompt replacement without text clutter.

### 15. Next-Gen Photorealistic Model Targets
The compiler provides dedicated target adapters engineered for the industry's highest-fidelity realism engines:
* **🔴 Adobe Firefly Image 5 & 4 Ultra (`--target firefly` / `adobe_firefly`)**:
  * Commercially safe, unretouched commercial studio and editorial photography.
  * **Strict 1,024-Character Limit Lock**: Mathematically guarantees output never exceeds Adobe Firefly's hard 1,024-character model limit (`len(prompt) <= 1024`), completely eliminating platform rejection errors.
  * **Intelligent Progressive Condensation**: Automatically prioritizes essential optical physics, camera hardware, and skin micro-pores while shedding lower-priority filler phrases on verbose scenes.
  * Formatted without negative prompt clutter, emphasizing camera angle, authentic depth of field, natural lighting, and skin micro-pores.
* **⚡ FLUX1.1 [pro] Ultra Raw (`--target flux_raw` / `flux_ultra_raw`)**:
  * Optimized for Black Forest Labs' native `raw=true` parameter.
  * Unfiltered 16-bit raw sensor fidelity, authentic lens aberrations, organic high-ISO noise pattern, and micro-blemishes instead of synthetic AI smoothing.
* **🎬 Runway Gen-4 Image (`--target runway` / `runway_gen4`)**:
  * Cinematic motion picture production stills.
  * Anamorphic lens optics (2.0x squeeze, oval bokeh, streak flares), Kodak Vision3 500T emulsion grading, and volumetric set lighting.
* **👤 HUMAIN Image 1 (`--target humain` / `humain_image_1`)**:
  * Forensic human portraiture and biometric realism.
  * Subsurface dermal light transport, authentic ocular wetness, iris fibril depth, and 5-point hand biomechanical articulation to escape the uncanny valley.

### 16. Expanded 33-Camera Hardware Engine & Skin Lighting Modifiers

#### 🔬 12 New Ground-Truth Hardware Profiles
1. **IMAX MSM 9802 (`imax_msm_9802`)**: 15-perf 65mm horizontal motion picture camera, Kodak Double-X 5222 panchromatic negative, monumental 70x48.5mm negative area, natural silver halide grain, zero digital compression.
2. **ARRI Alexa 265 (`arri_alexa_265`)**: 65mm digital cinema sensor (54.12x25.58mm), 15 stops dynamic range, EI 160–6400, ARRI Prime 65 lenses, LogC4 wide color gamut.
3. **Nikon FM2 (`nikon_fm2`)**: Fully mechanical 35mm SLR, 1/4000s honeycomb titanium shutter, Nikkor 105mm f/2.5 AI-S portrait prime, classic Kodachrome 64 slide film color saturation.
4. **Contax 645 (`contax_645`)**: 6x4.5 medium format system, legendary Carl Zeiss Planar T* 80mm f/2, Fujifilm Pro 400H overexposed +1 stop for luminous pastel skin tones.
5. **Hasselblad XPan (`hasselblad_xpan`)**: Dual-format panoramic 35mm rangefinder, 24x65mm negative (2.7:1 aspect ratio), Hasselblad 45mm f/4 prime with flat field sharpness.
6. **Deardorff 8x10 (`deardorff_8x10`)**: Classical mahogany 8x10 field camera, Schneider Symmar-S 360mm f/6.8, Kodak Tri-X 320 sheet film, pure white seamless backdrop, contact print tonal graduation.
7. **Antique View 8x10 Wet Plate (`antique_view_8x10`)**: 19th-century view camera, wet-plate collodion emulsion on black glass ambrotype, uncoated brass Petzval portrait optic with swirling radial astigmatism and chemical pour marks.
8. **Contax T2 (`contax_t2`)**: Premium titanium 35mm compact, Carl Zeiss Sonnar 38mm f/2.8 T*, harsh direct on-camera xenon flash with rapid inverse-square falloff and raw celebrity party intimacy.
9. **Ricoh GR IV (`ricoh_gr_iv`)**: 25.7MP APS-C high-end compact, fixed GR 18.3mm f/2.8 (28mm equivalent), deep zone-focus snap street photography with high-contrast monochrome and gritty micro-acutance.
10. **DJI Mavic 4 Pro (`dji_mavic_4_pro`)**: Professional aerial platform, 100MP 4/3 Hasselblad CMOS sensor, 28mm equivalent nadir top-down orientation, orthogonal plane focus, HNCS color science.
11. **Mamiya RZ67 Professional (`mamiya_rz67`)**: 6x7 medium format SLR with revolving back, Mamiya-Sekor Z 140mm f/4.5 Macro M, Kodak Portra 800, twin vertical Kino Flo daylight banks creating dual catchlights.
12. **Polaroid 20x24 (`polaroid_20x24`)**: Monumental 235-pound instant camera, Schneider Kreuznach 600mm f/11 optic, Polacolor 20x24 peel-apart film producing life-size 1:1 contact portraits with full dermal topography.

#### 💡 Skin & Texture Lighting Modifiers (`--skin-lighting`)
Enables physical control over skin micro-relief, epidermal surface reflectance, and hair fiber transmission:
* **`raking_hard_key`**: High-contrast, extreme side-grazing hard key light angled at 80–85° to cast micro-shadows across skin relief, accentuating epidermal pores, vellus hair, and tactile skin topography.
* **`cross_polarized_flash`**: Polarized illumination paired with an orthogonal cross-polarizing filter on the lens. Completely cancels 100% of specular skin reflections and oily shine, revealing deep dermal pigmentation, vascular structure, and genuine bare skin color.
  * *Physical Conflict Resolution*: Automatically disables raking specular highlights and suppresses oil/sweat shine in the prompt.
* **`hard_backlight_rim`**: High-intensity directional rim light placed directly behind the subject, producing razor-sharp silhouette separation, edge-lighting individual hair strands, and illuminating edge translucent fibers.

#### ⚖️ Strict Prompting Integrity Guarantee
All prompts adhere strictly to hardware-level physics and optical design:
* **Zero Artist / Director Names**: Never contains photographer, artist, director, or film title names in prompts. All visual aesthetics are achieved deterministically through optical mechanics, sensor physics, and lighting geometry.
* **Thin-Lens Calculated Depth of Field**: Depth of field values are mathematically derived ($CoC = \text{sensor diagonal} / 1500$) rather than guessed.
* **Forensic Dermal Integrity**: Macro profiles prohibit synthetic airbrushing, wax smoothing, and computational skin filters.

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
