"""ComfyUI custom node interface for Optical Camera Compiler."""

from __future__ import annotations

from typing import Any

from .compiler import compile_scene
from .models import ReferenceImageInput, ReferenceMode, SceneInput

RIG_NAMES = [
    "Sony a1 II Stacked Full-Frame (ILCE-1M2)",
    "Phase One XF IQ4 150MP Trichromatic",
    "Canon EOS R5 Mark II Stacked Full-Frame",
    "Nikon Z 9 Stacked Flagship Full-Frame",
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
    "Sony a1 II Stacked Full-Frame (ILCE-1M2)": "sony_a1_ii",
    "Phase One XF IQ4 150MP Trichromatic": "phase_one_iq4",
    "Canon EOS R5 Mark II Stacked Full-Frame": "canon_eos_r5_ii",
    "Nikon Z 9 Stacked Flagship Full-Frame": "nikon_z9",
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
                "model_target": (
                    ["gpt_images", "imagen", "midjourney", "flux", "sdxl"],
                    {"default": "gpt_images"},
                ),
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
                    ["native", "9:11", "4:5", "3:2", "4:3", "5:4", "16:9", "1:1", "21:9", "9:16"],
                    {"default": "9:11"},
                ),
                "reference_mode": (
                    ["disabled", "transform_adapt", "restore_upscale", "outpaint_full_body"],
                    {"default": "disabled"},
                ),
                "fidelity_lock": (
                    "FLOAT",
                    {"default": 0.85, "min": 0.10, "max": 1.0, "step": 0.05, "round": 0.01},
                ),
                "anti_drift_biometrics": (["enabled", "disabled"], {"default": "enabled"}),
                "brutal_sharpness_protocol": (["enabled", "disabled"], {"default": "enabled"}),
                "suppress_text_branding": (["enabled", "disabled"], {"default": "enabled"}),
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
        aspect_ratio: str = "9:11",
        reference_mode: str = "disabled",
        fidelity_lock: float = 0.85,
        anti_drift_biometrics: str = "enabled",
        brutal_sharpness_protocol: str = "enabled",
        suppress_text_branding: str = "enabled",
        append_negative_shield: str = "yes",
    ) -> tuple[str, str, str]:
        profile_id = RIG_NAME_TO_ID.get(camera_rig, "sony_a1_ii")

        ref_input = None
        if reference_mode in ("transform_adapt", "restore_upscale", "outpaint_full_body"):
            mode_map = {
                "transform_adapt": ReferenceMode.TRANSFORM_ADAPT,
                "restore_upscale": ReferenceMode.RESTORE_UPSCALE,
                "outpaint_full_body": ReferenceMode.OUTPAINT_FULL_BODY,
            }
            ref_mode = mode_map.get(reference_mode, ReferenceMode.NONE)
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

        ar_val = "9:11" if aspect_ratio == "native" else aspect_ratio

        scene = SceneInput(
            subject=subject.strip(),
            environment=environment.strip() if environment.strip() else None,
            lighting=lighting_override.strip() if lighting_override.strip() else None,
            aspect_ratio=ar_val,
            reference=ref_input,
            sharpness_protocol=(brutal_sharpness_protocol == "enabled"),
            suppress_text_branding=(suppress_text_branding == "enabled"),
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
