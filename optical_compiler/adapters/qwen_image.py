"""Adapter for Alibaba Qwen-Image-2.1 / Qwen-Image-2.1-Turbo (7B Single-Stream DiT + Qwen3-VL-8B)."""

from __future__ import annotations

from typing import List

from ..models import (
    CameraProfile,
    CompiledPayload,
    ReferenceMode,
    SceneInput,
    TargetEngine,
)
from .base import BaseAdapter

# Official Qwen-Image-2.1 / Turbo aspect ratio presets (High-Acuity 1.3MP Native Sweet Spot, exact multiples of 64)
QWEN_ASPECT_RESOLUTIONS: dict[str, tuple[int, int]] = {
    "1:1": (1152, 1152),
    "4:3": (1280, 960),
    "3:4": (960, 1280),
    "4:5": (1024, 1280),
    "5:4": (1280, 1024),
    "3:2": (1344, 896),
    "2:3": (896, 1344),
    "16:9": (1472, 832),
    "9:16": (832, 1472),
    "21:9": (1664, 704),
}


class QwenImageAdapter(BaseAdapter):
    """Compiles prompts optimized for Qwen-Image-2.1 & Qwen-Image-2.1-Turbo (Unsloth GGUF / Diffusers)."""

    target_engine = TargetEngine.QWEN_IMAGE

    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        optics = profile.sensor_and_optics
        lighting = profile.lighting_and_exposure
        shield = profile.negative_embeddings
        ref = scene.reference

        is_outpaint = ref and ref.mode == ReferenceMode.OUTPAINT_FULL_BODY
        is_product_lock = (ref and ref.mode == ReferenceMode.PRODUCT_LOCK) or scene.has_product_lock
        is_identity_lock = ref and ref.mode == ReferenceMode.IDENTITY_LOCK

        sentences: List[str] = []

        if scene.is_policy_safe:
            sentences.append(
                "Policy-Safe Compliance: Dignified editorial photographic capture adhering to platform standards with fully clothed subject."
            )

        # 1. Primary Visual Directive for Qwen3-VL-8B Text Encoder
        if is_outpaint:
            sentences.append(
                f"Create a photorealistic full-body photograph extending downward from the input reference image of {scene.subject}, "
                "showing the complete head-to-toe figure with natural ground contact while preserving exact facial geometry, hair, and wardrobe fabric."
            )
        elif is_product_lock:
            sentences.append(
                f"Photorealistic commercial studio product photograph of {scene.subject}, preserving exact reference SKU proportions, "
                "packaging geometry, seam lines, and authentic material specular response."
            )
            if scene.sku_color:
                sentences.append(f"Exact color calibration matching {scene.sku_color}.")
            if scene.material_finish:
                sentences.append(f"Surface material finish: {scene.material_finish}.")
            if scene.label_kerning:
                sentences.append(
                    f"Typography & Label Rule: Render exact crisp lettering reading \"{scene.label_kerning}\" with uniform kerning and zero character warping."
                )
        elif is_identity_lock:
            sentences.append(
                f"Photorealistic editorial portrait photograph of {scene.subject} from the reference image, locking exact facial bone structure, "
                "eye geometry, skin tone, and authentic expression."
            )
        else:
            is_portrait = any(
                k in f"{scene.framing} {scene.subject}".lower()
                for k in (
                    "portrait",
                    "headshot",
                    "close-up",
                    "male",
                    "female",
                    "man",
                    "woman",
                    "person",
                    "model",
                    "dancer",
                    "worker",
                    "craftsman",
                    "people",
                    "face",
                    "beauty",
                    "editorial",
                )
            ) and not is_product_lock
            has_explicit_rear = any(
                k in (scene.camera_angle or "").lower()
                for k in ("behind", "rear", "from back", "back view")
            )
            gaze_clause = (
                ", facing the camera with natural eye contact and authentic un-posed expression"
                if (is_portrait and not has_explicit_rear)
                else ""
            )
            subj_clean = scene.subject.strip().rstrip(".")
            if scene.framing:
                lead = f"{scene.framing} of {subj_clean}"
            elif subj_clean.lower().startswith(
                ("a ", "an ", "the ", "portrait", "editorial", "commercial", "photograph", "close-up", "macro", "wide")
            ):
                lead = f"Photorealistic {subj_clean[0].lower() + subj_clean[1:]}" if not subj_clean.lower().startswith("photorealistic") else subj_clean
            else:
                lead = f"Photorealistic editorial photograph of {subj_clean}"
            sentences.append(f"{lead}{gaze_clause}.")

        # 2. Scene Environment, Wardrobe, and Atmosphere
        env_clauses: List[str] = []
        if scene.environment:
            env_clauses.append(f"set in {scene.environment}")
        if scene.wardrobe:
            env_clauses.append(f"wearing {scene.wardrobe}")
        if scene.mood:
            env_clauses.append(f"conveying a {scene.mood} atmosphere")
        if env_clauses:
            sentences.append("The scene is " + ", ".join(env_clauses) + ".")

        # 3. Physical Camera Body, Lens, and Aperture Physics
        clean_camera = optics.camera_system.split("(")[0].strip()
        clean_lens = (scene.lens or optics.lens).split("(")[0].strip()
        aperture = scene.aperture or optics.aperture_sweet_spot

        f_num = 5.6
        try:
            if "f/" in aperture:
                f_num = float(aperture.replace("f/", "").split()[0])
            elif "T" in aperture:
                f_num = float(aperture.replace("T", "").split()[0])
        except Exception:
            f_num = 5.6

        if f_num <= 2.8:
            dof_clause = "shallow optical depth of field with smooth circular bokeh falloff and crisp subject separation"
        else:
            dof_clause = "deep optical sweet-spot depth of field with corner-to-corner MTF sharpness"

        sentences.append(
            f"Captured on {clean_camera} with {clean_lens} at {aperture} ({optics.iso_base}, {optics.dynamic_range}). "
            f"Exhibits {dof_clause}, zero digital oversharpening halos, and natural optical vignette."
        )

        # 4. Lighting Geometry & Tonal Roll-Off
        lighting_setup = scene.lighting or f"{lighting.primary_lighting}. {lighting.light_transport}"
        sentences.append(
            f"Lighting: {lighting_setup}, with physically accurate specular highlights, natural shadow roll-off, and true color fidelity."
        )

        # 5. Epidermal & Material Micro-Texture Protocol
        sentences.append(
            "Unretouched 16-bit optical sensor rendering: authentic human skin micro-relief with resolved pores, fine vellus hair, "
            "and realistic subsurface scattering without plastic smoothing or waxy AI artifacts. Fabric weave and surface materials show crisp physical texture."
        )

        if scene.has_hand_lock:
            sentences.append(
                "Anatomical hand lock: five distinct articulating fingers per hand with accurate knuckle folds, tendon lines, and natural grip geometry."
            )

        neg_tokens = shield.all_tokens(
            include_anti_drift=bool(ref),
            include_branding=scene.suppress_text_branding and not is_product_lock,
            include_compression=True,
            include_outpaint=is_outpaint,
            include_skin_realism=scene.human_skin_realism,
            include_product_drift=is_product_lock,
            include_hand_drift=scene.has_hand_lock,
            include_body_distortion=scene.has_body_morphology,
        )
        neg_tokens.extend(
            [
                "plastic skin",
                "waxy face",
                "airbrushed",
                "CGI",
                "3d render",
                "over-sharpened edge halos",
                "distorted anatomy",
                "gibberish text",
            ]
        )

        positive_prompt = " ".join(sentences)
        negative_prompt = ", ".join(dict.fromkeys(neg_tokens))
        w_px, h_px = QWEN_ASPECT_RESOLUTIONS.get(scene.aspect_ratio, (1024, 1024))

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            parameters={
                "engine": "Qwen-Image-2.1-Turbo (Unsloth Q8_0 GGUF / Apple Metal)",
                "diffusion_model": "qwen-image-2.1-turbo-Q8_0.gguf",
                "llm": "Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf",
                "vae": "qwen_image_2.1_vae_bf16.safetensors",
                "steps": 8,
                "cfg_scale": 1.0,
                "sampling_method": "euler",
                "sigmas": "qwen-image-2.1-turbo",
                "width": w_px,
                "height": h_px,
                "aspect_ratio": scene.aspect_ratio,
            },
            metadata={
                "model_family": "qwen_image_2_1",
                "model_name": "Qwen-Image-2.1 (7B DiT + Qwen3-VL-8B)",
                "quantization": "Unsloth Dynamic 2.0 Q8_0 (INT8)",
                "local_metal_ready": True,
            },
        )
