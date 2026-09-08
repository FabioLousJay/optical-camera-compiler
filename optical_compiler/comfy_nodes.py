"""ComfyUI custom node interface for Optical Camera Compiler."""

from __future__ import annotations

from typing import Any

from .compiler import compile_scene
from .models import ReferenceImageInput, ReferenceMode, SceneInput

RIG_NAMES = [
    "Phase One XF IQ4 150MP Trichromatic",
    "Hasselblad H6D-100c Studio Medium Format",
    "Leica M11 Rangefinder 60MP",
    "Fujifilm GFX 100 II High-Speed Medium Format",
    "Sony A7R V High-Resolution BSI",
    "Arri Alexa 35 Cinema Production",
    "Pentax 67 II Analog Medium Format Film",
    "Hasselblad 500 C/M Square Analog Medium Format",
    "Leica M6 35mm Rangefinder Analog Film",
    "Linhof Master Technika 4x5 Large Format Sheet Film",
]

RIG_NAME_TO_ID = {
    "Phase One XF IQ4 150MP Trichromatic": "phase_one_iq4",
    "Hasselblad H6D-100c Studio Medium Format": "hasselblad_h6d",
    "Leica M11 Rangefinder 60MP": "leica_m11",
    "Fujifilm GFX 100 II High-Speed Medium Format": "fujifilm_gfx100ii",
    "Sony A7R V High-Resolution BSI": "sony_a7rv",
    "Arri Alexa 35 Cinema Production": "arri_alexa_35",
    "Pentax 67 II Analog Medium Format Film": "pentax_67ii",
    "Hasselblad 500 C/M Square Analog Medium Format": "hasselblad_500cm",
    "Leica M6 35mm Rangefinder Analog Film": "leica_m6_analog",
    "Linhof Master Technika 4x5 Large Format Sheet Film": "linhof_technika_4x5",
}


class OpticalCameraCompilerNode:
    """ComfyUI node compiling raw prompts into deterministic optical hardware payloads."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "camera_rig": (RIG_NAMES, {"default": RIG_NAMES[0]}),
                "model_target": (["flux", "imagen", "midjourney", "sdxl"], {"default": "flux"}),
                "subject": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "Studio editorial portrait of a woman with natural skin texture, serene gaze, soft high-fashion styling",
                    },
                ),
            },
            "optional": {
                "environment": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "Minimalist brutalist architectural interior, soft ambient daylight falloff",
                    },
                ),
                "lighting_override": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "",
                    },
                ),
                "aspect_ratio": (
                    ["native", "1:1", "4:5", "3:2", "16:9", "21:9", "9:16"],
                    {"default": "native"},
                ),
                "reference_mode": (
                    ["disabled", "transform_adapt", "restore_upscale"],
                    {"default": "disabled"},
                ),
                "fidelity_lock": (
                    "FLOAT",
                    {"default": 0.85, "min": 0.10, "max": 1.0, "step": 0.05, "round": 0.01},
                ),
                "anti_drift_biometrics": (["enabled", "disabled"], {"default": "enabled"}),
                "append_negative_shield": (["yes", "no"], {"default": "yes"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("positive_prompt", "negative_prompt", "unified_payload")
    FUNCTION = "compile_optical_prompt"
    CATEGORY = "prompt/optical"

    def compile_optical_prompt(
        self,
        camera_rig: str,
        model_target: str,
        subject: str,
        environment: str = "",
        lighting_override: str = "",
        aspect_ratio: str = "native",
        reference_mode: str = "disabled",
        fidelity_lock: float = 0.85,
        anti_drift_biometrics: str = "enabled",
        append_negative_shield: str = "yes",
    ) -> tuple[str, str, str]:
        profile_id = RIG_NAME_TO_ID.get(camera_rig, "phase_one_iq4")

        ref_input = None
        if reference_mode in ("transform_adapt", "restore_upscale"):
            ref_mode = (
                ReferenceMode.TRANSFORM_ADAPT
                if reference_mode == "transform_adapt"
                else ReferenceMode.RESTORE_UPSCALE
            )
            elements = (
                [
                    "facial geometry",
                    "eye structure and gaze",
                    "facial bone structure",
                    "biometric identity",
                    "anatomical proportions",
                ]
                if anti_drift_biometrics == "enabled"
                else []
            )
            ref_input = ReferenceImageInput(
                mode=ref_mode,
                fidelity_lock=float(fidelity_lock),
                preserved_elements=elements,
                denoise_strength=round(1.0 - float(fidelity_lock), 2),
            )

        ar_val = "4:5" if aspect_ratio == "native" else aspect_ratio

        scene = SceneInput(
            subject=subject.strip(),
            environment=environment.strip() if environment.strip() else None,
            lighting=lighting_override.strip() if lighting_override.strip() else None,
            aspect_ratio=ar_val,
            reference=ref_input,
        )

        result = compile_scene(
            scene=scene,
            profile_name_or_path=profile_id,
            target_model=model_target,
        )

        pos = result.positive_prompt
        neg = result.negative_prompt
        unified = result.unified_prompt if append_negative_shield == "yes" else pos

        return (pos, neg, unified)


NODE_CLASS_MAPPINGS = {
    "OpticalCameraCompiler": OpticalCameraCompilerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OpticalCameraCompiler": "📷 Optical Camera Compiler",
}
