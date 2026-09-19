"""Adapter for Runway Gen-4 Image cinematic generation."""

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


class RunwayAdapter(BaseAdapter):
    """Compiles prompts into cinematic production stills optimized for Runway Gen-4 Image."""

    target_engine = TargetEngine.RUNWAY

    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        optics = profile.sensor_and_optics
        lighting = profile.lighting_and_exposure
        micro = profile.micro_detail_and_physics
        shield = profile.negative_embeddings
        ref = scene.reference

        is_outpaint = ref and ref.mode == ReferenceMode.OUTPAINT_FULL_BODY
        is_product_lock = (ref and ref.mode == ReferenceMode.PRODUCT_LOCK) or scene.has_product_lock
        is_identity_lock = ref and ref.mode == ReferenceMode.IDENTITY_LOCK

        parts: List[str] = []

        # 1. Cinematic Header & Scene Staging
        parts.append("Cinematic motion picture still.")

        if scene.is_policy_safe:
            parts.append(
                "Dignified cinematic direction adhering to platform safety guidelines with fully clothed subjects."
            )

        if is_outpaint:
            parts.append(
                f"Full-body cinematic master shot of {scene.subject}, extending the frame down to ground level with shoes visible, preserving character facial identity, costume, and lighting logic from the source reference."
            )
        elif is_product_lock:
            parts.append(
                f"High-end commercial hero shot of {scene.subject}, locked to reference product SKU geometry, packaging typography, and exact material finish."
            )
        elif is_identity_lock:
            parts.append(
                f"Close-up character portrait of {scene.subject}, maintaining authentic facial structure, natural skin undertones, and dramatic eye reflection."
            )
        else:
            framing = scene.framing or "Medium cinematic shot"
            is_portrait = any(k in f"{scene.framing} {scene.subject}".lower() for k in (
                "portrait", "headshot", "close-up", "male", "female", "man", "woman", "person",
                "model", "dancer", "worker", "craftsman", "people", "two", "face", "beauty", "editorial"
            )) and not is_product_lock
            has_explicit_rear = any(k in (scene.camera_angle or "").lower() for k in ("behind", "rear", "from back", "back view"))
            gaze_clause = ", facing camera with direct eye contact, natural cinematic posture" if (is_portrait and not has_explicit_rear) else ""
            parts.append(f"{framing} of {scene.subject}{gaze_clause}.")

        # 2. Environment & Mise-en-scène
        if scene.environment:
            parts.append(f"Production location: {scene.environment}.")
        if scene.wardrobe:
            parts.append(f"Costume design: {scene.wardrobe}.")
        if scene.mood:
            parts.append(f"Dramatic tone: {scene.mood}.")

        # 3. Cinema Camera Rig & Optical Simulation
        camera = optics.camera_system.split("(")[0].strip()
        lens = (scene.lens or optics.lens).split("(")[0].strip()
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
            dof_text = "Shallow depth of field with creamy background bokeh, natural optical falloff, and smooth cinematic focus transition."
        else:
            dof_text = "Deep cinematic depth of field with sharp edge-to-edge optical acutance and clear environmental focus throughout."

        if scene.is_anamorphic:
            squeeze = scene.anamorphic_squeeze.value if scene.anamorphic_squeeze else "2.0x"
            flare = scene.streak_flare.value if scene.streak_flare else "subtle horizontal streak flares"
            parts.append(
                f"Shot on cinema camera {camera} with {lens} {squeeze} anamorphic optics at {aperture}. "
                f"Cylindrical lens characteristics: vertical 2:1 elliptical oval background bokeh, gentle barrel distortion, and {flare}."
            )
        else:
            parts.append(
                f"Shot on cinema camera {camera} with prime cinema lens {lens} at {aperture}. {dof_text}"
            )

        # 4. Cinematic Lighting & Volumetrics
        lighting_desc = scene.lighting or f"{lighting.primary_lighting}. {lighting.light_transport}."
        parts.append(
            f"Cinematography lighting: {lighting_desc}, with atmospheric volume, delicate edge separation, and filmic shadow roll-off."
        )

        # 5. Film Stock & Color Grade
        film = scene.film_stock or "35mm motion picture stock, Kodak Vision3 color timing"
        parts.append(
            f"Emulsion: {film}, rich cinematic contrast, organic fine film grain, natural skin tone reproduction, no digital artifacts."
        )

        if scene.has_hand_lock:
            parts.append("Hand anatomy is cleanly defined with realistic proportions, natural finger posture, and no deformities.")

        positive_prompt = " ".join(parts)

        # Negative tokens for cinematic clean output
        neg_tokens = [
            "CGI look", "video game graphic", "plastic skin", "airbrushed", "cartoon", "oversaturated",
            "blurry", "extra fingers", "mutated hands", "distorted face", "watermark", "text overlay"
        ]
        if scene.suppress_text_branding:
            neg_tokens.extend(["logo", "branding", "commercial watermark", "subtitles"])

        negative_prompt = ", ".join(neg_tokens)

        aspect = scene.aspect_ratio or "16:9"

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            parameters={
                "engine": "Runway Gen-4 Image",
                "aspect_ratio": aspect,
                "motion_picture_grade": film,
                "camera": camera,
                "lens": lens,
            },
            metadata={
                "model_family": "runway",
                "model_name": "Runway Gen-4 Image",
                "cinematic_grade": True,
            },
        )
