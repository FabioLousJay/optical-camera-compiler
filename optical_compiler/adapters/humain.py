"""Adapter for HUMAIN Image 1 hyper-realistic human portraiture."""

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


class HumainAdapter(BaseAdapter):
    """Compiles prompts into hyper-detailed biometric prose optimized for HUMAIN Image 1."""

    target_engine = TargetEngine.HUMAIN

    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        optics = profile.sensor_and_optics
        lighting = profile.lighting_and_exposure
        micro = profile.micro_detail_and_physics
        shield = profile.negative_embeddings
        ref = scene.reference

        is_outpaint = ref and ref.mode == ReferenceMode.OUTPAINT_FULL_BODY
        is_product_lock = (ref and ref.mode == ReferenceMode.PRODUCT_LOCK) or scene.has_product_lock
        is_identity_lock = ref and ref.mode == ReferenceMode.IDENTITY_LOCK

        clauses: List[str] = []

        # 1. Subject & Biometric Focus
        clauses.append("Forensic human portrait photography.")

        if scene.is_policy_safe:
            clauses.append(
                "Dignified, ethical fine art photographic portrait with fully clothed subject and authentic human anatomy."
            )

        if is_outpaint:
            clauses.append(
                f"Full-length human figure extension of {scene.subject}, maintaining exact facial bone structure, skin complexion, hair texture, and attire from reference image downward to feet."
            )
        elif is_identity_lock:
            clauses.append(
                f"Strict identity-locked portrait of {scene.subject}, matching unique facial architecture, natural skin tone variation, and authentic expression."
            )
        else:
            framing = scene.framing or "Intimate headshot portrait"
            clauses.append(f"{framing} of {scene.subject}.")

        # 2. Styling, Expression & Setting
        if scene.environment:
            clauses.append(f"Context: {scene.environment}.")
        if scene.wardrobe:
            clauses.append(f"Clothing: {scene.wardrobe}, showing natural fabric tension and seams.")
        if scene.mood:
            clauses.append(f"Expression: {scene.mood}, with genuine eye contact.")

        # 3. Epidermal Micro-Physics & Subsurface Scattering (The HUMAIN Core)
        clauses.append(
            "Skin micro-topography: authentic human epidermis with visible individual pores, subtle cellular texture, delicate vellus facial hair, "
            "and natural dermal subsurface scattering. No plastic smoothing, no airbrushing, no waxy specular sheen, and no synthetic beautification."
        )

        # 4. Ocular & Facial Precision
        clauses.append(
            "Eyes: crisp iris fibril detail with natural depth, authentic corneal wetness, precise catchlights, and distinct eyelashes originating from eyelid margins."
        )

        # 5. Hand Biomechanics (5-Point Precision Gate)
        if scene.has_hand_lock:
            clauses.append(
                "Hands: strictly five anatomically correct articulating fingers per hand, authentic skin folds at knuckles, realistic tendon lines, and visible nail lunula."
            )

        # 6. Camera Optics & Lighting
        camera = optics.camera_system
        lens = scene.lens or optics.lens
        aperture = scene.aperture or optics.aperture_sweet_spot
        lighting_desc = scene.lighting or f"{lighting.primary_lighting}. {lighting.light_transport}."

        clauses.append(
            f"Shot on {camera} using {lens} at {aperture}. Focus locked on the nearest eye with micro-fine sharpness. "
            f"Lighting: {lighting_desc}, revealing true organic skin depth without harsh digital clipping."
        )

        positive_prompt = " ".join(clauses)

        # Negative tokens targeting uncanny valley artifacts
        neg_tokens = [
            "plastic skin", "doll skin", "wax figure", "uncanny valley", "smooth skin filter", "airbrushed face",
            "CGI rendering", "3D model", "deformed eyes", "cross-eyed", "extra fingers", "missing fingers",
            "fused fingers", "mutated hands", "bad anatomy", "over-sharpened halos", "fake pores", "pore stamping"
        ]
        if scene.suppress_text_branding:
            neg_tokens.extend(["watermark", "text", "logo", "caption"])

        negative_prompt = ", ".join(neg_tokens)

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            parameters={
                "engine": "HUMAIN Image 1",
                "aspect_ratio": scene.aspect_ratio,
                "focus_lock": "Near-eye pupil and eyelashes",
                "dermal_physics": "Subsurface scattering + organic micro-texture",
            },
            metadata={
                "model_family": "humain",
                "model_name": "HUMAIN Image 1",
                "portrait_specialized": True,
            },
        )
