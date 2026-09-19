"""Adapter for Black Forest Labs FLUX1.1 [pro] Ultra Raw (raw=true)."""

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


class FluxRawAdapter(BaseAdapter):
    """Compiles prompts optimized for FLUX1.1 [pro] Ultra Raw mode (raw=true)."""

    target_engine = TargetEngine.FLUX_RAW

    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        optics = profile.sensor_and_optics
        lighting = profile.lighting_and_exposure
        micro = profile.micro_detail_and_physics
        shield = profile.negative_embeddings
        ref = scene.reference

        is_outpaint = ref and ref.mode == ReferenceMode.OUTPAINT_FULL_BODY
        is_product_lock = (ref and ref.mode == ReferenceMode.PRODUCT_LOCK) or scene.has_product_lock
        is_identity_lock = ref and ref.mode == ReferenceMode.IDENTITY_LOCK

        sentences: List[str] = []

        # 1. Subject & Scene Opening (Candid / Documentary / Physical)
        if scene.is_policy_safe:
            sentences.append(
                "Policy-Safe Compliance: Dignified editorial photographic capture adhering to platform standards with fully clothed subject."
            )

        if is_outpaint:
            sentences.append(
                f"Full-body photograph extending downward from the reference photo of {scene.subject}, showing complete head-to-toe figure with shoes firmly on the ground, matching the exact facial geometry, hair, and clothing fabric from the source."
            )
        elif is_product_lock:
            sentences.append(
                f"Unretouched raw commercial studio photograph of {scene.subject}, matching reference SKU dimensions, packaging geometry, seam lines, and true material reflectivity."
            )
            if scene.sku_color:
                sentences.append(f"Product color matching {scene.sku_color}.")
            if scene.material_finish:
                sentences.append(f"Surface finish: {scene.material_finish}.")
        elif is_identity_lock:
            sentences.append(
                f"Documentary raw photograph of {scene.subject}, preserving authentic facial architecture, natural skin tones, and un-posed expression."
            )
        else:
            framing = scene.framing or "A natural photograph"
            is_portrait = any(k in f"{scene.framing} {scene.subject}".lower() for k in (
                "portrait", "headshot", "close-up", "male", "female", "man", "woman", "person",
                "model", "dancer", "worker", "craftsman", "people", "two", "face", "beauty", "editorial"
            )) and not is_product_lock
            has_explicit_rear = any(k in (scene.camera_angle or "").lower() for k in ("behind", "rear", "from back", "back view"))
            gaze_clause = ", facing camera with direct eye contact, natural un-posed expression and posture" if (is_portrait and not has_explicit_rear) else ""
            sentences.append(f"{framing} of {scene.subject}{gaze_clause}.")

        # 2. Environmental & Atmospheric Setting
        env_details: List[str] = []
        if scene.environment:
            env_details.append(f"in {scene.environment}")
        if scene.wardrobe:
            env_details.append(f"wearing {scene.wardrobe}")
        if scene.mood:
            env_details.append(f"with a {scene.mood} demeanor")
        if env_details:
            sentences.append("The subject is " + ", ".join(env_details) + ".")

        # 3. Camera Rig & Physical Optical Attributes
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
            dof_clause = "shallow optical depth of field with creamy background blur and subject isolation"
        else:
            dof_clause = "deep optical sweet-spot depth of field with sharp edge-to-edge clarity throughout"

        sentences.append(
            f"Shot on {clean_camera} equipped with {clean_lens} at {aperture}. "
            f"True optical depth of field featuring {dof_clause}, natural focus falloff, subtle peripheral vignetting, and authentic lens aberrations."
        )

        # 4. Lighting & Exposure
        lighting_setup = scene.lighting or f"{lighting.primary_lighting}. {lighting.light_transport}."
        sentences.append(
            f"Lit with {lighting_setup}, featuring realistic directional light transport, honest shadow roll-off, and zero artificial HDR tone-mapping."
        )

        # 5. Raw Sensor Characteristics & Forensic Texture Fidelity
        sentences.append(
            "Captured in 16-bit raw mode without digital smoothing or computational beauty filters. "
            "Natural epidermal skin topography with visible micro-pores, fine vellus facial hairs, organic dermal blemishes, and accurate subsurface scattering. "
            "Fabric weaves, textures, and material surfaces exhibit tangible micro-relief with uncompressed acutance."
        )

        # 6. Hand Biomechanics
        if scene.has_hand_lock:
            sentences.append(
                "Hands are rendered with strict anatomical fidelity: natural tendon lines, five distinct articulating fingers with realistic cuticles, and accurate skin folding at knuckles."
            )

        # 7. Negative Shield for Flux (injected into negative prompt channel)
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

        # Additional Raw specific anti-smoothing tokens
        neg_tokens.extend([
            "synthetic skin", "plastic skin", "airbrushed", "denoise blur", "AI smoothing", "waxy skin",
            "CGI render", "illustration", "beautified filter", "over-sharpened halos", "fake HDR"
        ])

        positive_prompt = " ".join(sentences)
        negative_prompt = ", ".join(dict.fromkeys(neg_tokens))

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            parameters={
                "engine": "FLUX1.1 [pro] Ultra Raw",
                "raw": True,
                "aspect_ratio": scene.aspect_ratio,
                "output_format": "4MP Ultra Raw Native",
            },
            metadata={
                "model_family": "bfl_flux",
                "model_name": "FLUX1.1 [pro] Ultra Raw",
                "raw_mode": True,
                "commercial_ready": True,
            },
        )
