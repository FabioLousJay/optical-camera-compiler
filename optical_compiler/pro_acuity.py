"""Universal Professional Acuity Shield.

Applied centrally by `OpticalCompiler.compile` to *every* camera profile, lens, and target engine:
  - Merges the professional anti-softness / anti-anatomy-drift negative token set into
    `negative_prompt` for all engines.
  - Appends an equivalent *positively phrased* acuity directive to the positive prompt for engines
    whose negative channel is weak or inert (e.g. Qwen-Image-2.1-Turbo runs at `cfg_scale=1.0`,
    where a negative prompt is mathematically ignored by classifier-free guidance).
  - Drops `wide angle` / `fisheye` negatives automatically when the selected lens itself is an
    ultra-wide or fisheye optic, so the prompt never contradicts the chosen hardware.
"""

from __future__ import annotations

import re
from typing import Any

PRO_ACUITY_NEGATIVES: tuple[str, ...] = (
    "soft focus",
    "blur",
    "motion blur",
    "haze",
    "diffusion",
    "oversmoothed skin",
    "beauty filter",
    "CGI",
    "plastic skin",
    "extra fingers",
    "extra limbs",
    "warped hands",
    "deformed anatomy",
    "inconsistent clothing",
    "wrong shoes",
    "distorted perspective",
    "wide angle",
    "fisheye",
)

WIDE_ANGLE_TOKENS: frozenset[str] = frozenset({"wide angle", "fisheye"})

PRO_ACUITY_POSITIVE_DIRECTIVE = (
    "Professional Acuity Lock: tack-sharp critical focus on the subject with crisp lens micro-contrast "
    "and clean atmosphere, refined natural skin with visible pores and fine vellus hair (no smoothing, "
    "no beauty filter), anatomically correct hands with five fingers each, consistent wardrobe and "
    "correct footwear, true rectilinear perspective."
)

# Engines whose prompt format is length-capped or encodes negatives inline in the positive prompt.
_SKIP_POSITIVE_DIRECTIVE = {"midjourney", "firefly"}
_MIDJOURNEY_EXCLUDED = frozenset({"deformed anatomy"})
_FIREFLY_NEGATIVE_LIMIT = 1024


def _lens_is_wide_or_fisheye(lens_text: str) -> bool:
    text = (lens_text or "").lower()
    if "fisheye" in text or "fish-eye" in text:
        return True
    # Detect focal lengths like "14mm", "16-35mm", "24 mm" — use the shortest focal length mentioned
    focals = [float(m) for m in re.findall(r"(\d{1,3}(?:\.\d)?)\s*(?:-\s*\d{1,3}\s*)?mm", text)]
    return bool(focals) and min(focals) < 28.0


def pro_acuity_negatives(lens_text: str = "") -> list[str]:
    """Return the universal negative token list, adapted to the selected lens."""
    wide = _lens_is_wide_or_fisheye(lens_text)
    return [t for t in PRO_ACUITY_NEGATIVES if not (wide and t in WIDE_ANGLE_TOKENS)]


def apply_pro_acuity_shield(payload: Any, lens_text: str = "") -> Any:
    """Merge the Professional Acuity Shield into a `CompiledPayload` in place and return it."""
    engine = getattr(payload.target_engine, "value", str(payload.target_engine)).lower()
    tokens = pro_acuity_negatives(lens_text)
    if engine == "midjourney":
        # Project rule: Midjourney `--no` must never carry anatomy nouns (they turn subjects away).
        tokens = [t for t in tokens if t not in _MIDJOURNEY_EXCLUDED]

    neg_text = payload.negative_prompt or ""
    is_structured_neg = neg_text.lstrip().startswith(("{", "["))
    added: list[str] = []
    if not is_structured_neg:
        existing = [t.strip() for t in neg_text.split(",") if t.strip()]
        seen = {t.lower() for t in existing}
        added = [t for t in tokens if t.lower() not in seen]
        merged = existing + added
        if engine == "firefly":
            # Adobe Firefly "Exclude from image" box is capped at 1,024 characters.
            while merged and len(", ".join(merged)) > _FIREFLY_NEGATIVE_LIMIT:
                merged.pop()
            added = [t for t in added if t in merged]
            payload.parameters["exclude_from_image"] = ", ".join(merged)
        payload.negative_prompt = ", ".join(merged)

    positive = payload.positive_prompt or ""
    is_structured_pos = positive.lstrip().startswith(("{", "["))
    if engine == "midjourney":
        # `--no` is the final Midjourney flag; extend it in place so the shield is actually enforced.
        if added and " --no " in positive:
            payload.positive_prompt = f"{positive.rstrip()}, {', '.join(added)}"
            if isinstance(payload.parameters.get("no"), list):
                payload.parameters["no"] = list(dict.fromkeys([*payload.parameters["no"], *added]))
    elif (
        engine not in _SKIP_POSITIVE_DIRECTIVE
        and not is_structured_pos
        and "Professional Acuity Lock" not in positive
    ):
        directive = PRO_ACUITY_POSITIVE_DIRECTIVE
        if _lens_is_wide_or_fisheye(lens_text):
            directive = directive.replace(", true rectilinear perspective.", ".")
        payload.positive_prompt = f"{positive.rstrip()} {directive}"

    payload.metadata["pro_acuity_shield"] = {
        "negatives_applied": tokens,
        "wide_lens_exemption": _lens_is_wide_or_fisheye(lens_text),
    }
    return payload
