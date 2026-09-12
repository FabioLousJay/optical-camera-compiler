"""Portrait Fidelity Engineering Protocol (PFEP v1.0) Module.

Provides canonical diagnostic stress probe definitions, compact prompt packs,
project workspace scaffolding, and 8-axis renderer scorecard evaluation.
"""

from pathlib import Path
from typing import Optional, Union

from .models import RendererScorecard, StressProbe

PROMPT_TEMPLATES: dict[str, str] = {
    "01_MASTER_PORTRAIT_LOCK.txt": """MASTER PORTRAIT LOCK (BASELINE ANCHOR)

Identity & Structure:
Using the provided image as the base. Preserve identity exactly. Facial structure, skull geometry, jawline, cheekbones, eye shape, nose, mouth, hairline, beard pattern, skin texture, pores, wrinkles, asymmetries, and age markers must remain unchanged. No beautification. No identity drift. No facial reinterpretation.
Wardrobe, glasses, and accessories remain identical. Materials, fit, and color unchanged.

Camera & Framing:
Camera height, distance, and perspective locked. Medium portrait framing preserved. Natural perspective. No lens exaggeration.

Focus & Rendering Discipline:
Focus locked on the near eye. Iris and eyelashes critically sharp. Zero motion blur.
Natural human skin rendering. Visible pores and micro texture. High micro-contrast. Crisp edge acuity. No haze. No diffusion.

Lighting:
Flash-dominated exposure to freeze micro motion.
Key light 35 to 45 degrees off axis, slightly above eye line.
Minimal fill.
Strong negative fill on the shadow side for deep tonal separation.
Optional ultra-low-power rim light strictly for edge separation. No glow.
Editorial contrast. Clean specular highlights. Controlled highlight roll-off.

Camera Module (Choose one per run):
Option A: Shot on Sony a1 II (ILCE-1M2), FE 85mm f/5.6, 1/400s flash sync, ISO 100.
Option B: Shot on Phase One XF + IQ4 150MP, Schneider Kreuznach 80mm LS f/2.8 Blue Ring, f/8, ISO 50, strobe exposure.

Negative Constraints:
soft focus, blur, motion blur, haze, diffusion, dreamy glow, plastic skin, oversmoothed skin, beauty filter, CGI, synthetic rendering, low detail, wide angle, fisheye, distorted perspective, warped anatomy, duplicated body parts, inconsistent clothing.
""",
    "02_FULL_BODY_OUTPAINT_LENS_HONEST.txt": """FULL-BODY OUTPAINT: LENS-HONEST EXTENSION

Using the provided image as the base. Preserve identity and upper body exactly.
Extend the image downward to reveal the full body, head-to-toe. Maintain the same camera position, camera height, distance, and lens compression as the original image.
No camera pull-back. No perspective shift. No wide-angle reinterpretation.

Body proportions must be anatomically consistent with the subject. Natural stance. Realistic weight distribution.
Wardrobe must remain consistent. Same clothing materials, cuts, colors, and fit extended naturally to the full body. Shoes must match the outfit logically.

Optical & Lighting Discipline:
Perspective compression must match an 85mm full-frame or 80mm medium-format lens.
Lighting direction, contrast ratio, and shadow density remain consistent from head to toe.

Negative Constraints:
wide angle, perspective shift, camera pull-back, stretched limbs, elongated legs, narrow shoulders, warped proportions, inconsistent lighting, background scaling errors, cartoon anatomy.
""",
    "03_STRESS_HARD_KEY_LIGHTING.txt": """LIGHTING STRESS TEST: HARD KEY VARIANT

Using the provided image as the base. Preserve identity exactly.
Flash-dominated exposure with a harder key light.
Key light positioned 50 to 60 degrees off axis, slightly above eye line.
Fill reduced to near zero.
Aggressive negative fill on the shadow side.
Contrast ratio increased. Shadows are deep but not crushed.
Skin pores, epidermal micro-ridges, and fine vellus texture must remain visible in both highlights and shadows. No haze or smoothing.
Specularity controlled; no blown highlights or clipped skin.

Negative Constraints:
beauty lighting, soft light, fill glow, skin smoothing, cinematic haze, stylized contrast, crushed blacks, clipped highlights.
""",
    "04_STRESS_CROSS_POLARIZED_SKIN.txt": """CROSS-POLARIZED SKIN: TECHNICAL PROMPT

Using the provided image as the base. Preserve identity exactly.
Simulate cross-polarized studio lighting.
Specular reflections extinguished. Surface glare minimized.
Skin rendering must rely on subsurface structure, pores, wrinkles, and tonal variation.
No smoothing to compensate for loss of specular highlights.
Skin must not appear flat, plastic, or waxy.
Micro-contrast preserved without shine.

Negative Constraints:
beauty lighting, oily skin sheen, plastic texture, flat skin, airbrushed surface.
""",
    "05_STRESS_GLASSES_REFLECTION_CONTROL.txt": """GLASSES REFLECTION: HARD KEY CONTROL

Using the provided image as the base. Preserve identity exactly. Glasses must remain identical.
Hard key light positioned 50 to 60 degrees off axis, slightly above eye line. Minimal fill, strong negative fill.
Glasses reflections must be physically plausible.
Eyes and pupils must remain clearly visible through lenses.
No blown white rectangles. No duplicated light sources. No floating highlights. No opaque lenses. No glow or flare.

Negative Constraints:
opaque glare, blown reflections, white rectangles, floating glare, flash flare, distorted pupils.
""",
    "06_STRESS_SEATED_COMPRESSION.txt": """SEATED VARIANT: COMPRESSION LOCK

Using the provided image as the base. Preserve identity exactly.
Subject is seated. Natural seated posture. Neutral body language.
Camera height, camera distance, and lens compression must remain identical to the standing reference.
Camera does not move upward or backward. No virtual zoom. No perspective shift.
Torso, legs, and chair proportions must obey the same optical compression as an 85mm full-frame or 80mm medium-format lens.
Lighting and focus unchanged.

Negative Constraints:
perspective shift, leg elongation, compressed torso, virtual zoom, camera elevation drift.
""",
    "07_STRESS_STANDING_COMPRESSION.txt": """STANDING VARIANT: COMPRESSION LOCK

Using the provided image as the base. Preserve identity exactly.
Subject is standing upright. Balanced weight distribution. Natural stance.
Camera height, distance, and optical compression unchanged from seated reference.
Perspective and spatial compression locked identically.
Lighting, focus, and rendering discipline unchanged.

Negative Constraints:
perspective distortion, focal length shift, stretched limbs, camera pullback.
""",
    "08_STRESS_BACKGROUND_SCALE.txt": """BACKGROUND SCALE INVARIANCE: LOCKED OPTICS

Using the provided image as the base. Preserve identity exactly.
Extend the visible environment slightly beyond the original framing.
The subject remains the exact same size in frame.
Camera height, camera distance, and focal length are locked.
Background elements must scale correctly relative to the subject.
No background shrinkage, no depth compression changes, no parallax artifacts.

Negative Constraints:
subject shrinking relative to background, background scale drift, wide-angle creep, field of view widening.
""",
    "09_STRESS_HAIR_SPECULAR_BREAKUP.txt": """HAIR SPECULAR BREAKUP: HARD KEY

Using the provided image as the base. Preserve identity exactly.
Hard key light positioned 55 to 65 degrees off axis, slightly above eye line.
Hair rendering must demonstrate realistic specular breakup.
Individual strand response and directional sheen consistent with light angle.
No continuous highlight bands, plastic gloss, or helmet-like reflections.
Beard and scalp hair behave consistently with organic strand density.

Negative Constraints:
helmet hair, uniform plastic shine, continuous highlight band, clumping, CGI hair sheen.
""",
    "10_STRESS_SHADOW_SKIN_COLOR.txt": """SHADOW-SIDE SKIN COLOR: TONAL INTEGRITY TEST

Using the provided image as the base. Preserve identity exactly.
Strong negative fill on the unlit shadow side.
Shadow-side skin must retain natural color information, warm undertones, and subtle chroma.
No gray desaturation. No green, blue, or magenta cast.
No crushed blacks. Micro-texture and pores remain visible in shadows.

Negative Constraints:
gray shadow skin, muddy desaturation, green color cast, blue contamination, crushed black shadows.
""",
}

RUN_LOG_TEMPLATE: str = """# PFEP Run Log: run_001

## Run Metadata
- **Date**: YYYY-MM-DD
- **Model / Engine**: 
- **Prompt Reference**: 01_prompts/01_MASTER_PORTRAIT_LOCK.txt
- **Camera Module**: Sony a1 II (85mm f/5.6) / Phase One IQ4 150MP (80mm f/8)
- **Variable Changed**: Baseline initialization (one variable only)

## Generated Outputs
- `output_01.png`
- `output_02.png`
- `output_03.png`
- `output_04.png`

## 8-Axis Renderer Scorecard (0-2 each, max 16)
- **Identity** (HARD GATE: must be 2): 
- **Focus**: 
- **Skin Texture**: 
- **Lighting Honesty**: 
- **Glasses**: 
- **Hair**: 
- **Geometry**: 
- **Background Scale**: 
- **Total Score**: /16
- **Status**: PENDING

## Evaluation Notes
- **Best Output**: output_XX
- **Rationale**: 
- **Failure Modes Observed**: 
- **Next Single-Variable Action**: 
"""

PFEP_README_CONTENT: str = """# Portrait Fidelity Engineering Protocol (PFEP v1.0)
## Multi-Stage Photorealistic Evaluation & Convergence Architecture

### Core Engineering Principles
1. **Stability Over Peak Beauty**: An image that reproduces reliably is more valuable than one unreproducible outlier.
2. **Identity Is a Hard Gate**: If identity is lost (`identity < 2`), the run fails regardless of sharpness or lighting.
3. **Optics Before Decoration**: Geometry and perspective compression errors cannot be corrected by color grading.
4. **Material Realism Is Local**: Evaluate skin, hair, glasses, and background independently.
5. **One Variable at a Time**: Never change multiple variables in a single iteration.

### Recommended Workspace Layout
```text
pfep_workspace/
├── 00_inputs/        # Base reference images
├── 01_prompts/       # 10 canonical PFEP diagnostic prompts
├── 02_runs/          # Sequential run directories with notes.md
│   └── run_001/
├── 03_selected/      # Extracted regional anchors (face, hair, glasses, body, bg)
└── 04_converged/     # Final production outputs
```

### The 8-Axis Renderer Scorecard
| Axis | 0 | 1 | 2 |
| :--- | :--- | :--- | :--- |
| **Identity** | Drift | Minor Deviation | Locked (Gate) |
| **Focus** | Soft | Acceptable | Tack Sharp |
| **Skin Texture** | Plastic | Mixed | Natural Pores |
| **Lighting Honesty**| Fake | Passable | Physically Coherent |
| **Glasses** | Broken | Acceptable | Plausible |
| **Hair** | Helmet-like | Mixed | Strand Breakup |
| **Geometry** | Warped | Minor Errors | Correct |
| **Background Scale**| Drifting | Minor Drift | Invariant |

Pass criteria: **Identity == 2** AND **Total Score >= 12 / 16**.
"""


def init_pfep_project(target_dir: Union[str, Path]) -> list[Path]:
    """Scaffold a full PFEP v1.0 project directory with prompts, run logs, and documentation.

    Args:
        target_dir: Directory where the PFEP structure should be initialized.

    Returns:
        List of created file paths.
    """
    base = Path(target_dir).resolve()
    created_files: list[Path] = []

    # 1. Create subdirectories
    dirs = [
        base / "00_inputs",
        base / "01_prompts",
        base / "02_runs" / "run_001",
        base / "03_selected",
        base / "04_converged",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # 2. Write PFEP README
    readme_path = base / "PFEP_README.md"
    readme_path.write_text(PFEP_README_CONTENT, encoding="utf-8")
    created_files.append(readme_path)

    # 3. Write 00_inputs README
    inputs_readme = base / "00_inputs" / "README.md"
    inputs_readme.write_text(
        "# 00_inputs\n\nPlace your canonical base portrait reference images here (e.g., `base.jpg`).\n",
        encoding="utf-8",
    )
    created_files.append(inputs_readme)

    # 4. Write all 10 compact prompt files
    for filename, content in PROMPT_TEMPLATES.items():
        p = base / "01_prompts" / filename
        p.write_text(content, encoding="utf-8")
        created_files.append(p)

    # 5. Write sample run log
    run_log = base / "02_runs" / "run_001" / "notes.md"
    run_log.write_text(RUN_LOG_TEMPLATE, encoding="utf-8")
    created_files.append(run_log)

    # 6. Write 03_selected README
    selected_readme = base / "03_selected" / "README.md"
    selected_readme.write_text(
        "# 03_selected\n\nSave your regional anchor selections here:\n"
        "- `face_anchor.png`\n"
        "- `hair_anchor.png`\n"
        "- `glasses_anchor.png`\n"
        "- `body_anchor.png`\n"
        "- `background_anchor.png`\n",
        encoding="utf-8",
    )
    created_files.append(selected_readme)

    # 7. Write 04_converged README
    converged_readme = base / "04_converged" / "README.md"
    converged_readme.write_text(
        "# 04_converged\n\nSave your final production outputs here (e.g. `final_v01.png`).\n",
        encoding="utf-8",
    )
    created_files.append(converged_readme)

    return created_files
