from __future__ import annotations

from pathlib import Path
from typing import Any

from .compiler import compile_scene
from .models import (
    AdSafeZone,
    AnamorphicSqueeze,
    BackgroundStyle,
    ContentType,
    CopySpace,
    GoboPattern,
    GripModifier,
    GripType,
    IrisBladeCount,
    LightingEnvironmentSpec,
    LightingRatio,
    MaterialStyle,
    PaperProfile,
    ReconstructionLock4XSpec,
    ReferenceImageInput,
    ReferenceMode,
    SceneInput,
    SeriesCohesionSpec,
    StreakFlare,
    StressProbe,
    SuperResolutionBackend,
)

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
    "Leica SL2 Full-Frame (50mm Summilux f/2.8)",
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
    "Leica SL2 Full-Frame (50mm Summilux f/2.8)": "leica_sl2",
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
                    ["native", "9:11", "4:5", "3:2", "4:3", "5:4", "16:9", "1:1", "21:9", "9:16", "5:5", "9:12"],
                    {"default": "9:11"},
                ),
                "reference_mode": (
                    [
                        "disabled",
                        "transform_adapt",
                        "restore_upscale",
                        "identity_lock",
                        "product_lock",
                        "depixelate_gfx100rf",
                        "reconstruction_lock_4x",
                        "universal_png_lock",
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
                "product_crop": ("STRING", {"default": ""}),
                "sku_color": ("STRING", {"default": ""}),
                "cap_geometry": ("STRING", {"default": ""}),
                "label_kerning": ("STRING", {"default": ""}),
                "material_finish": ("STRING", {"default": ""}),
                "seam_geometry": ("STRING", {"default": ""}),
                "approval_gate_100pct": (["enabled", "disabled"], {"default": "enabled"}),
                "capture_mode": (
                    [
                        "default",
                        "static_max_detail",
                        "portrait_max_detail",
                        "action_max_detail",
                        "macro_max_detail",
                        "landscape_architecture_max_detail",
                        "slow_shutter_crowd_motion",
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
                        "flat_overcast",
                        "dramatic",
                        "neon",
                    ],
                    {"default": "none"},
                ),
                "anti_drift_biometrics": (["enabled", "disabled"], {"default": "enabled"}),
                "brutal_sharpness_protocol": (["enabled", "disabled"], {"default": "enabled"}),
                "suppress_text_branding": (["enabled", "disabled"], {"default": "enabled"}),
                "append_negative_shield": (["yes", "no"], {"default": "yes"}),
                "hand_lock": (["disabled", "enabled"], {"default": "disabled"}),
                "grip_type": (
                    ["default", "palm_support", "precision_pinch", "cylindrical_wrap", "relaxed_rest", "open_palm"],
                    {"default": "default"},
                ),
                "hand_details": ("STRING", {"default": ""}),
                "anamorphic": (["disabled", "enabled"], {"default": "disabled"}),
                "anamorphic_squeeze": (
                    ["default", "1.0x", "1.33x", "1.5x", "1.8x", "2.0x"],
                    {"default": "default"},
                ),
                "streak_flare": (
                    ["none", "cyan_blue", "warm_gold", "neutral_silver", "vintage_magenta"],
                    {"default": "none"},
                ),
                "iris_blades": (
                    ["default", "14_blade_circular", "9_blade_rounded", "8_blade_octagonal", "6_blade_hexagonal"],
                    {"default": "default"},
                ),
                "gobo": (
                    ["none", "venetian_blinds", "dappled_foliage", "window_panes", "geometric_slits", "prism_fracture"],
                    {"default": "none"},
                ),
                "grip_modifier": (
                    ["none", "beauty_dish_honeycomb", "butterfly_8x8_silk", "snoot_pinpoint", "solid_black_floppy"],
                    {"default": "none"},
                ),
                "lighting_ratio": (
                    ["default", "1:1", "2:1", "4:1", "8:1", "16:1"],
                    {"default": "default"},
                ),
                "copy_space": (
                    ["none", "left_third", "right_third", "top_third", "bottom_third"],
                    {"default": "none"},
                ),
                "ad_safe_zone": (
                    ["none", "tiktok_reels_9_16", "instagram_feed_4_5", "ecommerce_catalog_1_1"],
                    {"default": "none"},
                ),
                "body_volume": ("STRING", {"default": ""}),
                "weight_lb": ("INT", {"default": 0, "min": 0, "max": 500}),
                "material_style": (
                    ["none", "glossy_latex", "liquid_glass", "dielectric_acrylic", "brushed_titanium", "matte_silicone", "high_gloss_plastic", "metallic_flake", "translucent_resin", "volumetric_4d"],
                    {"default": "none"},
                ),
                "background_style": (
                    ["default", "opaque_black_blur", "pure_black_matte", "studio_cyclorama", "negative_void", "environmental_natural"],
                    {"default": "default"},
                ),
                "volumetric_4d": (["disabled", "enabled"], {"default": "disabled"}),
                "remove_text": (["disabled", "enabled"], {"default": "disabled"}),
                "paper_profile": (["none", "matte_cotton", "luster", "glossy", "baryta", "canvas"], {"default": "none"}),
                "policy_safe": (["disabled", "enabled"], {"default": "disabled"}),
                "stress_probe": (
                    [
                        "none",
                        "master_portrait_lock",
                        "outpaint_lens_honest",
                        "stress_hard_key",
                        "stress_cross_polarized",
                        "stress_glasses_reflections",
                        "stress_seated_compression",
                        "stress_standing_compression",
                        "stress_background_scale",
                        "stress_hair_specular",
                        "stress_shadow_color",
                    ],
                    {"default": "none"},
                ),
                "min_mb": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1000.0}),
                "cct_kelvin": ("INT", {"default": 0, "min": 0, "max": 20000}),
                "illuminance_lux": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "gallery_zone": ("STRING", {"default": ""}),
                "anchor_image_id": ("STRING", {"default": ""}),
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
        product_crop: str = "",
        sku_color: str = "",
        cap_geometry: str = "",
        label_kerning: str = "",
        material_finish: str = "",
        seam_geometry: str = "",
        approval_gate_100pct: str = "enabled",
        capture_mode: str = "default",
        lighting_preset: str = "none",
        anti_drift_biometrics: str = "enabled",
        brutal_sharpness_protocol: str = "enabled",
        suppress_text_branding: str = "enabled",
        append_negative_shield: str = "yes",
        hand_lock: str = "disabled",
        grip_type: str = "default",
        hand_details: str = "",
        anamorphic: str = "disabled",
        anamorphic_squeeze: str = "default",
        streak_flare: str = "none",
        iris_blades: str = "default",
        gobo: str = "none",
        grip_modifier: str = "none",
        lighting_ratio: str = "default",
        copy_space: str = "none",
        ad_safe_zone: str = "none",
        body_volume: str = "",
        weight_lb: int = 0,
        material_style: str = "none",
        background_style: str = "default",
        volumetric_4d: str = "disabled",
        remove_text: str = "disabled",
        paper_profile: str = "none",
        policy_safe: str = "disabled",
        stress_probe: str = "none",
        min_mb: float = 0.0,
        cct_kelvin: int = 0,
        illuminance_lux: int = 0,
        gallery_zone: str = "",
        anchor_image_id: str = "",
    ) -> tuple[str, str, str]:
        profile_id = RIG_NAME_TO_ID.get(camera_rig, "auto")

        ref_input = None
        ref_mode = ReferenceMode.NONE
        if reference_mode in (
            "transform_adapt",
            "restore_upscale",
            "identity_lock",
            "product_lock",
            "depixelate_gfx100rf",
            "outpaint_full_body",
            "reconstruction_lock_4x",
        ) or product_crop.strip():
            mode_map = {
                "transform_adapt": ReferenceMode.TRANSFORM_ADAPT,
                "restore_upscale": ReferenceMode.RESTORE_UPSCALE,
                "identity_lock": ReferenceMode.IDENTITY_LOCK,
                "product_lock": ReferenceMode.PRODUCT_LOCK,
                "depixelate_gfx100rf": ReferenceMode.DEPIXELATE_GFX100RF,
                "outpaint_full_body": ReferenceMode.OUTPAINT_FULL_BODY,
                "reconstruction_lock_4x": ReferenceMode.RECONSTRUCTION_LOCK_4X,
            }
            ref_mode = mode_map.get(reference_mode, ReferenceMode.PRODUCT_LOCK if product_crop.strip() else ReferenceMode.NONE)
            if ref_mode == ReferenceMode.PRODUCT_LOCK:
                elements = (
                    [
                        "cap closure geometry",
                        "label kerning and typography",
                        "manufacturing parting seams",
                        "material surface finish",
                        "exact SKU color",
                    ]
                    if anti_drift_biometrics == "enabled"
                    else []
                )
            else:
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
                filename=product_crop.strip() if product_crop.strip() else None,
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

        hl_val = (hand_lock == "enabled")
        gt_val = GripType.from_string(grip_type) if grip_type != "default" else None
        hd_val = hand_details.strip() if hand_details.strip() else None

        ana_val = (anamorphic == "enabled")
        sq_val = (
            AnamorphicSqueeze.from_string(anamorphic_squeeze)
            if anamorphic_squeeze != "default"
            else (AnamorphicSqueeze.SQUEEZE_2_0X if ana_val else None)
        )
        sf_val = StreakFlare.from_string(streak_flare) if streak_flare != "none" else None
        ib_val = IrisBladeCount.from_string(iris_blades) if iris_blades != "default" else None

        gobo_val = GoboPattern.from_string(gobo) if gobo != "none" else None
        grip_val = GripModifier.from_string(grip_modifier) if grip_modifier != "none" else None
        lr_val = LightingRatio.from_string(lighting_ratio) if lighting_ratio != "default" else None
        cs_val = CopySpace.from_string(copy_space) if copy_space != "none" else None
        asz_val = AdSafeZone.from_string(ad_safe_zone) if ad_safe_zone != "none" else None

        probe_enum = StressProbe.from_str(stress_probe) if stress_probe != "none" else StressProbe.NONE
        min_mb_val = float(min_mb) if min_mb > 0 else None

        le_spec = None
        if cct_kelvin > 0 or illuminance_lux > 0:
            le_spec = LightingEnvironmentSpec(
                cct_kelvin=cct_kelvin if cct_kelvin > 0 else 5000,
                illuminance_lux=illuminance_lux if illuminance_lux > 0 else 500,
            )

        sc_spec = None
        if gallery_zone.strip() or anchor_image_id.strip():
            sc_spec = SeriesCohesionSpec(
                anchor_image_id=anchor_image_id.strip() if anchor_image_id.strip() else None,
                gallery_zone=gallery_zone.strip() if gallery_zone.strip() else None,
            )

        recon_spec = None
        if ref_mode == ReferenceMode.RECONSTRUCTION_LOCK_4X:
            recon_spec = ReconstructionLock4XSpec(
                backend=SuperResolutionBackend.REAL_ESRNET_X4PLUS,
                denoise_strength=0.15,
                blend_ratio=0.20,
                protect_sky_haze=True,
            )

        scene = SceneInput(
            subject=subject.strip(),
            environment=environment.strip() if environment.strip() else None,
            lighting=lighting_override.strip() if lighting_override.strip() else None,
            aspect_ratio=ar_val,
            reference=ref_input,
            product_crop=product_crop.strip() if product_crop.strip() else None,
            sku_color=sku_color.strip() if sku_color.strip() else None,
            cap_geometry=cap_geometry.strip() if cap_geometry.strip() else None,
            label_kerning=label_kerning.strip() if label_kerning.strip() else None,
            material_finish=material_finish.strip() if material_finish.strip() else None,
            seam_geometry=seam_geometry.strip() if seam_geometry.strip() else None,
            approval_gate_100pct=(approval_gate_100pct == "enabled"),
            capture_mode=cm_val,
            lighting_preset=lp_val,
            sharpness_protocol=(brutal_sharpness_protocol == "enabled"),
            suppress_text_branding=(suppress_text_branding == "enabled"),
            human_skin_realism=(human_skin_realism == "enabled"),
            content_type=ct_enum,
            hand_lock=hl_val,
            grip_type=gt_val,
            hand_details=hd_val,
            anamorphic_squeeze=sq_val,
            streak_flare=sf_val,
            iris_blades=ib_val,
            gobo=gobo_val,
            grip_modifier=grip_val,
            lighting_ratio=lr_val,
            copy_space=cs_val,
            ad_safe_zone=asz_val,
            body_volume=body_volume.strip() if body_volume.strip() else None,
            weight_lb=weight_lb if weight_lb > 0 else None,
            material_style=MaterialStyle.from_str(material_style) if material_style != "none" else (MaterialStyle.VOLUMETRIC_4D if volumetric_4d == "enabled" else None),
            background_style=BackgroundStyle.from_str(background_style) if background_style != "default" else None,
            is_4d_volumetric=(volumetric_4d == "enabled"),
            remove_text_when_present=(remove_text == "enabled"),
            paper_profile=PaperProfile.from_str(paper_profile) if paper_profile != "none" else None,
            policy_safe=(policy_safe == "enabled"),
            stress_probe=probe_enum,
            min_file_mb=min_mb_val,
            lighting_environment=le_spec,
            series_cohesion=sc_spec,
            reconstruction_lock=recon_spec,
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


class OpticalClosedLoopExporterNode:
    """ComfyUI node executing Closed-Loop Resolution Engine with SHA-256 cryptographic provenance."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "image_path": ("STRING", {"default": ""}),
            },
            "optional": {
                "output_path": ("STRING", {"default": ""}),
                "target_width": ("INT", {"default": 0, "min": 0, "max": 20000}),
                "target_height": ("INT", {"default": 0, "min": 0, "max": 20000}),
                "width_in": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 200.0}),
                "height_in": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 200.0}),
                "ppi": ("INT", {"default": 300, "min": 72, "max": 1200}),
                "min_mb": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 500.0}),
                "output_format": (["PNG", "TIFF", "JPEG"], {"default": "PNG"}),
                "add_micro_noise": (["disabled", "enabled"], {"default": "disabled"}),
                "generate_report": (["enabled", "disabled"], {"default": "enabled"}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "FLOAT", "BOOLEAN")
    RETURN_NAMES = ("output_path", "sha256", "report_markdown", "file_mb", "passed_constraints")
    FUNCTION = "export_image"
    CATEGORY = "image/export"

    def export_image(
        self,
        image_path: str,
        output_path: str = "",
        target_width: int = 0,
        target_height: int = 0,
        width_in: float = 0.0,
        height_in: float = 0.0,
        ppi: int = 300,
        min_mb: float = 0.0,
        output_format: str = "PNG",
        add_micro_noise: str = "disabled",
        generate_report: str = "enabled",
    ) -> tuple[str, str, str, float, bool]:
        from .restoration import export_closed_loop

        in_p = image_path.strip()
        out_p = output_path.strip() if output_path.strip() else f"exports/export_{Path(in_p).stem}.{output_format.lower()}"
        tw = target_width if target_width > 0 else None
        th = target_height if target_height > 0 else None
        win = width_in if width_in > 0 else None
        hin = height_in if height_in > 0 else None
        min_mb_val = min_mb if min_mb > 0 else None

        run_report, _ = export_closed_loop(
            input_path=in_p,
            output_path=out_p,
            target_width=tw,
            target_height=th,
            width_in=win,
            height_in=hin,
            ppi=ppi,
            min_mb=min_mb_val,
            output_format=output_format,
            add_noise=(add_micro_noise == "enabled"),
            generate_report=(generate_report == "enabled"),
        )

        return (
            run_report.output_path,
            run_report.sha256,
            run_report.to_markdown(),
            run_report.file_size_mb,
            run_report.passed_constraints,
        )


class Optical4XReconstructionLockNode:
    """ComfyUI custom node for Professional 4X Reconstruction Lock Protocol."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        return {
            "required": {
                "image_path": ("STRING", {"default": "input_image.png"}),
                "backend": (
                    [
                        "realesrnet_x4plus (Structural Fidelity Master)",
                        "swinir_m_x4 (Balanced Transformer)",
                        "realesrgan_x4v3 (Controlled Detail -dn 0.15)",
                        "realesrgan_x4plus (Aggressive Perceptual Sharpness)",
                        "hat_s_x4 (Hybrid Attention Transformer)",
                        "pil_conservative (Zero Hallucination Lanczos)",
                    ],
                    {"default": "realesrnet_x4plus (Structural Fidelity Master)"},
                ),
                "denoise_strength": ("FLOAT", {"default": 0.15, "min": 0.0, "max": 1.0, "step": 0.01}),
                "blend_ratio": ("FLOAT", {"default": 0.20, "min": 0.0, "max": 1.0, "step": 0.01}),
                "protect_sky_haze": (["enabled", "disabled"], {"default": "enabled"}),
                "output_format": (["PNG", "TIFF", "JPEG"], {"default": "PNG"}),
            },
            "optional": {
                "output_path": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "FLOAT", "BOOLEAN")
    RETURN_NAMES = ("output_path", "sha256", "report_markdown", "file_mb", "validation_passed")
    FUNCTION = "reconstruct_4x"
    CATEGORY = "image/upscaling"

    def reconstruct_4x(
        self,
        image_path: str,
        backend: str = "realesrnet_x4plus (Structural Fidelity Master)",
        denoise_strength: float = 0.15,
        blend_ratio: float = 0.20,
        protect_sky_haze: str = "enabled",
        output_format: str = "PNG",
        output_path: str = "",
    ) -> tuple[str, str, str, float, bool]:
        from .restoration import execute_4x_reconstruction_lock

        in_p = image_path.strip()
        out_p = output_path.strip() if output_path.strip() else None
        backend_key = backend.split(" ")[0].strip()

        report, _ = execute_4x_reconstruction_lock(
            input_path=in_p,
            output_path=out_p,
            backend=backend_key,
            denoise_strength=denoise_strength,
            blend_ratio=blend_ratio,
            protect_sky_haze=(protect_sky_haze == "enabled"),
            output_format=output_format,
            generate_report=True,
        )

        return (
            report.output_path,
            report.sha256,
            report.to_markdown(),
            report.file_size_mb,
            report.validation_passed,
        )


class Optical4XFullColorPNGUpscaleNode:
    """ComfyUI node executing Universal High-Resolution PNG Output Lock v1.0 & 4X Upscale Workflow."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_path": ("STRING", {"default": "input_image.png"}),
                "unsharp_radius": ("FLOAT", {"default": 1.1, "min": 0.1, "max": 10.0, "step": 0.1}),
                "unsharp_percent": ("INT", {"default": 85, "min": 0, "max": 500, "step": 5}),
                "unsharp_threshold": ("INT", {"default": 3, "min": 0, "max": 50, "step": 1}),
                "compress_level": ("INT", {"default": 0, "min": 0, "max": 9, "step": 1}),
                "target_min_mb": ("FLOAT", {"default": 12.0, "min": 1.0, "max": 500.0, "step": 1.0}),
            },
            "optional": {
                "output_path": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "FLOAT", "STRING", "BOOLEAN")
    RETURN_NAMES = ("output_path", "sha256", "report_markdown", "file_mb", "delivery_string", "validation_passed")
    FUNCTION = "upscale_png_4x"
    CATEGORY = "image/upscaling"

    def upscale_png_4x(
        self,
        image_path: str,
        unsharp_radius: float = 1.1,
        unsharp_percent: int = 85,
        unsharp_threshold: int = 3,
        compress_level: int = 0,
        target_min_mb: float = 12.0,
        output_path: str = "",
    ) -> tuple[str, str, str, float, str, bool]:
        from .restoration import execute_4x_full_color_png_upscale

        in_p = image_path.strip()
        out_p = output_path.strip() if output_path.strip() else None

        report, _ = execute_4x_full_color_png_upscale(
            input_path=in_p,
            output_path=out_p,
            unsharp_radius=unsharp_radius,
            unsharp_percent=unsharp_percent,
            unsharp_threshold=unsharp_threshold,
            compress_level=compress_level,
            min_mb=target_min_mb,
            generate_report=True,
        )

        return (
            report.output_path,
            report.sha256,
            report.to_markdown(),
            report.file_size_mb,
            report.delivery_string,
            report.validation_passed,
        )


NODE_CLASS_MAPPINGS = {
    "OpticalCameraCompiler": OpticalCameraCompilerNode,
    "OpticalConservative102MPUpscaler": OpticalConservative102MPUpscalerNode,
    "OpticalClosedLoopExporter": OpticalClosedLoopExporterNode,
    "Optical4XReconstructionLock": Optical4XReconstructionLockNode,
    "Optical4XFullColorPNGUpscale": Optical4XFullColorPNGUpscaleNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OpticalCameraCompiler": "📷 Optical Camera Compiler",
    "OpticalConservative102MPUpscaler": "🔬 PIL Conservative 102MP Upscaler Lock",
    "OpticalClosedLoopExporter": "🔒 Closed-Loop Resolution Engine & Provenance",
    "Optical4XReconstructionLock": "🚀 4X Reconstruction Lock Engine",
    "Optical4XFullColorPNGUpscale": "💎 4X Full-Color PNG Output Lock Upscaler",
}
