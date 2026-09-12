"""ComfyUI custom node interface for Optical Camera Compiler."""

from __future__ import annotations

from typing import Any

from .compiler import compile_scene
from .models import ContentType, ReferenceImageInput, ReferenceMode, SceneInput

RIG_NAMES = [
    "Auto (Intelligent Camera Router)",
    "Sony a1 II Stacked Full-Frame (ILCE-1M2)",
    "Phase One XF IQ4 150MP Trichromatic",
    "Hasselblad X2D II 100C Medium Format (HNCS)",
    "FUJIFILM GFX100RF Rangefinder Large Format (102MP)",
    "Canon EOS R1 Stacked Flagship (Action / Sports)",
    "Canon EOS R5 Mark II Stacked Full-Frame",
    "Nikon Z 9 Stacked Flagship Full-Frame",
    "Leica SL3-P Full-Frame Mirrorless (Maestro IV)",
    "Panasonic LUMIX S1RII High-Resolution Mirrorless",
    "Sony FX Cinema Line Full-Frame (Venice S-Log3)",
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
    "Auto (Intelligent Camera Router)": "auto",
    "Sony a1 II Stacked Full-Frame (ILCE-1M2)": "sony_a1_ii",
    "Phase One XF IQ4 150MP Trichromatic": "phase_one_iq4",
    "Hasselblad X2D II 100C Medium Format (HNCS)": "hasselblad_x2d_ii_100c",
    "FUJIFILM GFX100RF Rangefinder Large Format (102MP)": "fujifilm_gfx100rf",
    "Canon EOS R1 Stacked Flagship (Action / Sports)": "canon_eos_r1",
    "Canon EOS R5 Mark II Stacked Full-Frame": "canon_eos_r5_ii",
    "Nikon Z 9 Stacked Flagship Full-Frame": "nikon_z9",
    "Leica SL3-P Full-Frame Mirrorless (Maestro IV)": "leica_sl3_p",
    "Panasonic LUMIX S1RII High-Resolution Mirrorless": "panasonic_lumix_s1rii",
    "Sony FX Cinema Line Full-Frame (Venice S-Log3)": "sony_fx_series",
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
                    ["gpt_images", "imagen", "midjourney", "flux", "sdxl", "raw", "json"],
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
                    [
                        "disabled",
                        "transform_adapt",
                        "restore_upscale",
                        "depixelate_gfx100rf",
                        "outpaint_full_body",
                    ],
                    {"default": "disabled"},
                ),
                "content_type": (
                    [
                        "photograph",
                        "portrait",
                        "product_photo",
                        "document_scan",
                        "poster_or_flyer",
                        "meme_or_infographic",
                        "ui_or_screenshot",
                        "mixed_content",
                    ],
                    {"default": "photograph"},
                ),
                "human_skin_realism": (["enabled", "disabled"], {"default": "enabled"}),
                "fidelity_lock": (
                    "FLOAT",
                    {"default": 0.85, "min": 0.10, "max": 1.0, "step": 0.05, "round": 0.01},
                ),
                "capture_mode": (
                    [
                        "default",
                        "static_max_detail",
                        "portrait_max_detail",
                        "action_max_detail",
                        "macro_max_detail",
                        "landscape_architecture_max_detail",
                    ],
                    {"default": "default"},
                ),
                "lighting_preset": (
                    [
                        "none",
                        "golden_hour",
                        "blue_hour",
                        "studio_soft",
                        "studio_hard",
                        "flash_freeze",
                        "overcast",
                        "dramatic",
                        "neon",
                    ],
                    {"default": "none"},
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
        content_type: str = "photograph",
        human_skin_realism: str = "enabled",
        fidelity_lock: float = 0.85,
        capture_mode: str = "default",
        lighting_preset: str = "none",
        anti_drift_biometrics: str = "enabled",
        brutal_sharpness_protocol: str = "enabled",
        suppress_text_branding: str = "enabled",
        append_negative_shield: str = "yes",
    ) -> tuple[str, str, str]:
        profile_id = RIG_NAME_TO_ID.get(camera_rig, "auto")

        ref_input = None
        if reference_mode in ("transform_adapt", "restore_upscale", "depixelate_gfx100rf", "outpaint_full_body"):
            mode_map = {
                "transform_adapt": ReferenceMode.TRANSFORM_ADAPT,
                "restore_upscale": ReferenceMode.RESTORE_UPSCALE,
                "depixelate_gfx100rf": ReferenceMode.DEPIXELATE_GFX100RF,
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
        cm_val = None if capture_mode == "default" else capture_mode
        lp_val = None if lighting_preset == "none" else lighting_preset

        try:
            ct_enum = ContentType(content_type)
        except (ValueError, KeyError):
            ct_enum = ContentType.PHOTOGRAPH

        scene = SceneInput(
            subject=subject.strip(),
            environment=environment.strip() if environment.strip() else None,
            lighting=lighting_override.strip() if lighting_override.strip() else None,
            aspect_ratio=ar_val,
            reference=ref_input,
            capture_mode=cm_val,
            lighting_preset=lp_val,
            sharpness_protocol=(brutal_sharpness_protocol == "enabled"),
            suppress_text_branding=(suppress_text_branding == "enabled"),
            human_skin_realism=(human_skin_realism == "enabled"),
            content_type=ct_enum,
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


class OpticalConservative102MPUpscalerNode:
    """ComfyUI node executing the PIL Conservative 102MP Restoration and Upscale Lock (PLATINUM_NO_DRIFT)."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "image_path": ("STRING", {"default": ""}),
            },
            "optional": {
                "output_path": ("STRING", {"default": ""}),
                "format": (["auto", "jpeg", "png", "tiff"], {"default": "auto"}),
                "cleanup_enabled": (["enabled", "disabled"], {"default": "enabled"}),
                "sharpening_enabled": (["enabled", "disabled"], {"default": "enabled"}),
                "human_skin_realism": (["enabled", "disabled"], {"default": "enabled"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "FLOAT")
    RETURN_NAMES = ("output_path", "report_json", "output_width", "output_height", "output_megapixels")
    FUNCTION = "execute_102mp_upscale"
    CATEGORY = "image/upscaling"

    def execute_102mp_upscale(
        self,
        image_path: str,
        output_path: str = "",
        format: str = "auto",
        cleanup_enabled: str = "enabled",
        sharpening_enabled: str = "enabled",
        human_skin_realism: str = "enabled",
    ) -> tuple[str, str, int, int, float]:
        import json
        from .restoration import restore_and_upscale_102mp, RestorationConfig

        cfg = RestorationConfig(
            cleanup_enabled=(cleanup_enabled == "enabled"),
            sharpening_enabled=(sharpening_enabled == "enabled"),
            human_skin_realism=(human_skin_realism == "enabled"),
        )
        out_fmt = None if format == "auto" else format.upper()
        out_p = output_path.strip() if output_path.strip() else None

        report = restore_and_upscale_102mp(
            input_path=image_path.strip(),
            output_path=out_p,
            config=cfg,
            output_format=out_fmt,
        )

        return (
            report["output_path"],
            json.dumps(report, indent=2),
            int(report["output_width"]),
            int(report["output_height"]),
            float(report["output_megapixels"]),
        )


NODE_CLASS_MAPPINGS = {
    "OpticalCameraCompiler": OpticalCameraCompilerNode,
    "OpticalConservative102MPUpscaler": OpticalConservative102MPUpscalerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OpticalCameraCompiler": "📷 Optical Camera Compiler",
    "OpticalConservative102MPUpscaler": "🔬 PIL Conservative 102MP Upscaler Lock",
}
