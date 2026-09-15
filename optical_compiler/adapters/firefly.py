"""Adapter for Adobe Firefly Image 5 and Image 4 Ultra commercial photography."""

from __future__ import annotations

from typing import List, Optional, Tuple

from ..models import (
    CameraProfile,
    CompiledPayload,
    ReferenceMode,
    SceneInput,
    TargetEngine,
)
from .base import BaseAdapter


class FireflyAdapter(BaseAdapter):
    """Compiles prompts into structured photographic prose optimized for Adobe Firefly.

    Enforces Adobe Firefly's strict 1,024-character limit with intelligent progressive
    condensation and a failsafe sentence-boundary truncation shield.
    """

    target_engine = TargetEngine.FIREFLY
    MAX_CHAR_LIMIT = 1024
    SAFE_TARGET_BUDGET = 990

    @classmethod
    def enforce_firefly_limit(cls, text: str, max_chars: int = 1024) -> str:
        """Strictly enforce the 1,024-character ceiling, truncating cleanly on sentence or word boundaries."""
        clean_text = " ".join(text.strip().split())
        if len(clean_text) <= max_chars:
            return clean_text

        # Truncate at maximum allowable characters
        cutoff = clean_text[:max_chars]

        # Attempt 1: Break cleanly at the last complete sentence boundary (. )
        last_sentence_end = cutoff.rfind(". ")
        if last_sentence_end > max_chars * 0.55:
            return cutoff[: last_sentence_end + 1].strip()

        # Attempt 2: Break at the last period if it ends at the cutoff
        last_period = cutoff.rfind(".")
        if last_period > max_chars * 0.60:
            return cutoff[: last_period + 1].strip()

        # Attempt 3: Break at the last word boundary and close with a period
        last_space = cutoff.rfind(" ")
        if last_space > 0:
            trimmed = cutoff[:last_space].rstrip(" ,;:!?-")
            return f"{trimmed}."

        # Attempt 4: Absolute character boundary
        return cutoff.rstrip(" ,;:!?-") + "."

    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        optics = profile.sensor_and_optics
        lighting = profile.lighting_and_exposure
        ref = scene.reference

        is_outpaint = ref and ref.mode == ReferenceMode.OUTPAINT_FULL_BODY
        is_product_lock = (ref and ref.mode == ReferenceMode.PRODUCT_LOCK) or scene.has_product_lock
        is_identity_lock = ref and ref.mode == ReferenceMode.IDENTITY_LOCK

        # 1. Platform Policy & Style
        style_clause = "Style: Authentic Professional Color Photograph."
        policy_clause = (
            "Tasteful editorial photographic execution adhering to commercial safety standards."
            if scene.is_policy_safe
            else None
        )

        # 2. Framing & Subject
        if is_outpaint:
            subject_clause = (
                f"Full-length head-to-toe editorial portrait of {scene.subject}, standing grounded with visible footwear, "
                f"maintaining face, hair, and wardrobe texture from reference."
            )
        elif is_product_lock:
            parts = [f"Commercial studio product photograph of {scene.subject}"]
            if scene.material_finish:
                parts.append(f"finish: {scene.material_finish}")
            if scene.sku_color:
                parts.append(f"color: {scene.sku_color}")
            subject_clause = ", ".join(parts) + "."
        elif is_identity_lock:
            subject_clause = (
                f"Documentary photographic portrait of {scene.subject}, strictly maintaining facial identity and bone structure."
            )
        else:
            framing_str = scene.framing or "Eye-level editorial portrait"
            subject_clause = f"{framing_str} of {scene.subject}."

        # 3. Setting & Styling
        setting_clause = f"Setting: {scene.environment}." if scene.environment else None
        attire_clause = f"Attire: {scene.wardrobe}." if scene.wardrobe else None
        mood_clause = f"Mood: {scene.mood}." if scene.mood else None

        # 4. Camera & Optical Physics
        # Strip long hardware marketing parentheticals to conserve budget
        clean_camera = optics.camera_system.split("(")[0].strip()
        aperture = scene.aperture or optics.aperture_sweet_spot
        lens = scene.lens or optics.lens

        optics_clause = (
            f"Shot on {clean_camera} with {lens} at {aperture}. "
            f"Natural optical depth of field with sharp focus and creamy background bokeh."
        )

        # 5. Hand Precision Gate
        hand_clause = (
            "Anatomically correct hands with exactly five distinct fingers, natural joint creases."
            if scene.has_hand_lock
            else None
        )

        # 6. Lighting & Atmosphere
        lighting_raw = scene.lighting or f"{lighting.primary_lighting}. {lighting.light_transport}."
        lighting_clean = " ".join(lighting_raw.strip().split())
        lighting_clause = f"Lighting: {lighting_clean}, with soft shadow transitions."

        # 7. Skin & Texture Realism (Anti-AI smoothing)
        if scene.human_skin_realism:
            skin_clause = (
                "Natural human skin realism: visible fine pores, subtle skin texture, and authentic subsurface scattering without airbrushing."
            )
        else:
            skin_clause = "Crisp unretouched textures, realistic fabric weave, natural skin tones, optical clarity."

        # 8. Copy-Space
        copy_clause = (
            f"Commercial layout with reserved negative copy space along the {scene.copy_space.value}."
            if scene.copy_space
            else None
        )

        # Prioritized Assembly:
        # Priority tiers from highest (must keep) to lowest (first to drop if over budget)
        tier_essential = [style_clause, subject_clause, optics_clause]
        tier_high = [lighting_clause, setting_clause]
        tier_medium = [skin_clause, hand_clause]
        tier_standard = [attire_clause, mood_clause, policy_clause, copy_clause]

        # Start with all active clauses
        all_clauses = [
            style_clause,
            policy_clause,
            subject_clause,
            setting_clause,
            attire_clause,
            mood_clause,
            optics_clause,
            hand_clause,
            lighting_clause,
            skin_clause,
            copy_clause,
        ]
        active_clauses = [c for c in all_clauses if c]

        candidate = " ".join(active_clauses)

        # If candidate exceeds safe budget, progressively shed lower-priority clauses
        if len(candidate) > self.SAFE_TARGET_BUDGET:
            # Step 1: Drop policy & copy space
            shed_list = [c for c in active_clauses if c not in (policy_clause, copy_clause)]
            candidate = " ".join(shed_list)

        if len(candidate) > self.SAFE_TARGET_BUDGET:
            # Step 2: Drop mood
            shed_list = [c for c in shed_list if c != mood_clause]
            candidate = " ".join(shed_list)

        if len(candidate) > self.SAFE_TARGET_BUDGET:
            # Step 3: Drop attire
            shed_list = [c for c in shed_list if c != attire_clause]
            candidate = " ".join(shed_list)

        if len(candidate) > self.SAFE_TARGET_BUDGET:
            # Step 4: Condense lighting clause
            condensed_lighting = f"Lighting: {lighting.primary_lighting}."
            shed_list = [
                condensed_lighting if c == lighting_clause else c
                for c in shed_list
            ]
            candidate = " ".join(shed_list)

        if len(candidate) > self.SAFE_TARGET_BUDGET:
            # Step 5: Condense optics clause
            condensed_optics = f"Shot on {clean_camera}, {lens} at {aperture}, shallow depth of field."
            shed_list = [
                condensed_optics if c == optics_clause else c
                for c in shed_list
            ]
            candidate = " ".join(shed_list)

        # Final Ironclad Boundary Enforcement: Strictly guarantee <= 1,024 characters
        positive_prompt = self.enforce_firefly_limit(candidate, max_chars=self.MAX_CHAR_LIMIT)

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
                "character_limit": self.MAX_CHAR_LIMIT,
                "character_count": len(positive_prompt),
                "character_budget_safe": len(positive_prompt) <= self.MAX_CHAR_LIMIT,
            },
            metadata={
                "model_family": "adobe_firefly",
                "recommended_model": "Firefly Image 5",
                "commercial_safe": True,
                "char_limit": self.MAX_CHAR_LIMIT,
                "char_count": len(positive_prompt),
            },
        )

