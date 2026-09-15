"""Adapter for Adobe Firefly Image 5 and Image 4 Ultra commercial photography."""

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


class FireflyAdapter(BaseAdapter):
    """Compiles prompts into structured photographic prose optimized for Adobe Firefly."""

    target_engine = TargetEngine.FIREFLY

    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        optics = profile.sensor_and_optics
        lighting = profile.lighting_and_exposure
        micro = profile.micro_detail_and_physics
        ref = scene.reference

        is_outpaint = ref and ref.mode == ReferenceMode.OUTPAINT_FULL_BODY
        is_product_lock = (ref and ref.mode == ReferenceMode.PRODUCT_LOCK) or scene.has_product_lock
        is_identity_lock = ref and ref.mode == ReferenceMode.IDENTITY_LOCK

        elements: List[str] = []

        # 1. Platform Policy & Style Classification
        elements.append("Style: Authentic Professional Color Photograph.")

        if scene.is_policy_safe:
            elements.append(
                "Dignified, tasteful editorial photographic execution adhering to commercial safety standards with fully clothed subject and realistic human anatomy."
            )

        # 2. Framing & Subject
        if is_outpaint:
            elements.append(
                f"Full-length head-to-toe editorial portrait of {scene.subject}, standing grounded with visible footwear, maintaining the original face, hair, and wardrobe texture from the reference input."
            )
        elif is_product_lock:
            elements.append(
                f"Commercial studio product photograph of {scene.subject}, featuring exact commercial SKU proportions, material surfaces, and pristine packaging details."
            )
            if scene.material_finish:
                elements.append(f"Material finish: {scene.material_finish}.")
            if scene.sku_color:
                elements.append(f"Color fidelity: {scene.sku_color}.")
        elif is_identity_lock:
            elements.append(
                f"Documentary photographic portrait of {scene.subject}, strictly maintaining facial identity, natural bone structure, and authentic expression."
            )
        else:
            framing_str = scene.framing or "Eye-level editorial portrait"
            elements.append(f"{framing_str} of {scene.subject}.")

        # 3. Environment & Styling
        if scene.environment:
            elements.append(f"Setting: {scene.environment}.")
        if scene.wardrobe:
            elements.append(f"Attire: {scene.wardrobe}.")
        if scene.mood:
            elements.append(f"Mood: {scene.mood}.")

        # 4. Camera & Optical Physics
        aperture = scene.aperture or optics.aperture_sweet_spot
        lens = scene.lens or optics.lens
        camera = optics.camera_system

        elements.append(
            f"Shot on {camera} with {lens} at {aperture}. "
            f"Natural optical depth of field with sharp near-plane focus and creamy background bokeh."
        )

        # 5. Hand Precision Gate
        if scene.has_hand_lock:
            elements.append(
                "Anatomically correct hands with exactly five distinct fingers, natural joint creases, and realistic fingernail cuticles."
            )

        # 6. Lighting & Atmosphere
        lighting_desc = scene.lighting or f"{lighting.primary_lighting}. {lighting.light_transport}."
        elements.append(f"Lighting: {lighting_desc}, with soft shadow transitions and natural specular highlights.")

        # 7. Skin & Texture Realism (Anti-AI smoothing)
        if scene.human_skin_realism:
            elements.append(
                "Natural human skin realism: visible fine pores, subtle skin texture, micro-details, and authentic subsurface scattering without artificial smoothing or airbrushing."
            )
        else:
            elements.append(
                "Crisp unretouched textures, realistic fabric weave, natural skin tones, and uncompressed optical clarity."
            )

        # 8. Aspect ratio & Compositional hints
        if scene.copy_space:
            elements.append(f"Commercial layout with reserved negative copy space along the {scene.copy_space.value}.")

        positive_prompt = " ".join(elements)

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=positive_prompt,
            negative_prompt="",  # Adobe Firefly does not support negative prompts
            parameters={
                "engine": "Adobe Firefly Image 5 / Image 4 Ultra",
                "aspect_ratio": scene.aspect_ratio,
                "content_type": "Photo",
                "photo_settings": {
                    "aperture": aperture,
                    "shutter": optics.shutter,
                    "camera_angle": "Eye level",
                },
            },
            metadata={
                "model_family": "adobe_firefly",
                "recommended_model": "Firefly Image 5",
                "commercial_safe": True,
            },
        )
