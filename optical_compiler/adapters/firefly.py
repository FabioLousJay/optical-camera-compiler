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

        # 1. Subject, Gaze & Staging
        is_portrait = any(k in f"{scene.framing} {scene.subject}".lower() for k in (
            "portrait", "headshot", "close-up", "male", "female", "man", "woman", "person",
            "model", "dancer", "worker", "craftsman", "people", "two", "face", "beauty", "editorial"
        )) and not is_product_lock

        has_explicit_rear = any(k in (scene.camera_angle or "").lower() for k in ("behind", "rear", "from back", "back view"))
        gaze_str = ", facing camera with direct eye contact, natural dignified expression and posture" if (is_portrait and not has_explicit_rear) else ""

        if is_outpaint:
            subject_sentence = (
                f"Full-length head-to-toe editorial portrait of {scene.subject}, standing grounded with visible footwear, "
                f"maintaining face, hair, and wardrobe texture from reference."
            )
        elif is_product_lock:
            parts = [f"Commercial studio product photograph of {scene.subject}"]
            if scene.material_finish:
                parts.append(f"finish: {scene.material_finish}")
            if scene.sku_color:
                parts.append(f"color: {scene.sku_color}")
            subject_sentence = ", ".join(parts) + "."
        elif is_identity_lock:
            subject_sentence = (
                f"Documentary photographic portrait of {scene.subject}{gaze_str}, strictly maintaining facial identity and bone structure."
            )
        else:
            framing_str = scene.framing or "Editorial photographic portrait"
            env_str = f", set in {scene.environment}" if scene.environment else ""
            attire_str = f", wearing {scene.wardrobe}" if scene.wardrobe else ""
            mood_str = f", {scene.mood}" if scene.mood else ""
            morph_str = f", realistic heavyset plus-size build with authentic weight distribution {scene.weight_lb}lbs" if (scene.has_body_morphology and scene.weight_lb) else ""
            subject_sentence = f"{framing_str} of {scene.subject}{gaze_str}{morph_str}{env_str}{attire_str}{mood_str}."

        # 2. Camera, Optics & Concrete Depth of Field
        clean_camera = optics.camera_system.split("(")[0].strip()
        aperture = scene.aperture or optics.aperture_sweet_spot
        lens = (scene.lens or optics.lens).split("(")[0].strip()

        f_num = 5.6
        try:
            if "f/" in aperture:
                f_num = float(aperture.replace("f/", "").split()[0])
            elif "T" in aperture:
                f_num = float(aperture.replace("T", "").split()[0])
        except Exception:
            f_num = 5.6

        depth_phrase = (
            "shallow optical depth of field with sharp subject focus and creamy background bokeh"
            if f_num <= 2.8
            else "natural optical depth of field with sharp edge-to-edge optical sweet-spot clarity"
        )

        lighting_raw = scene.lighting or f"{lighting.primary_lighting}"
        lighting_clean = " ".join(lighting_raw.strip().split()).rstrip(".")

        optics_sentence = f"Shot on {clean_camera} with {lens} at {aperture}, illuminated by {lighting_clean}, featuring {depth_phrase}."

        # 3. Micro-Texture, Skin Realism & Acutance
        hand_phrase = " Anatomically correct hands with exactly five distinct fingers, natural joint creases." if scene.has_hand_lock else ""

        if scene.human_skin_realism:
            texture_sentence = (
                f"Tack-sharp focus on near eye, natural human skin realism with visible fine pores, authentic subsurface scattering, "
                f"realistic uncompressed fabric weave, natural color grading.{hand_phrase}"
            )
        else:
            texture_sentence = (
                f"Tack-sharp focus on near eye, crisp unretouched micro-textures, authentic fabric weave, "
                f"clean optical acutance, natural commercial color grading.{hand_phrase}"
            )

        copy_clause = (
            f"Commercial layout with reserved negative copy space along the {scene.copy_space.value}."
            if scene.copy_space
            else None
        )

        # Prioritized Assembly
        candidates = [subject_sentence, optics_sentence, texture_sentence]
        if copy_clause:
            candidates.append(copy_clause)

        candidate_text = " ".join(candidates)

        # Progressive condensation if budget exceeded
        if len(candidate_text) > self.SAFE_TARGET_BUDGET and copy_clause:
            candidates.remove(copy_clause)
            candidate_text = " ".join(candidates)

        if len(candidate_text) > self.SAFE_TARGET_BUDGET:
            # Condense optics sentence
            optics_condensed = f"Shot on {clean_camera}, {lens} at {aperture}, {depth_phrase}."
            candidates = [subject_sentence, optics_condensed, texture_sentence]
            candidate_text = " ".join(candidates)

        if len(candidate_text) > self.SAFE_TARGET_BUDGET:
            # Condense texture sentence
            texture_condensed = "Tack-sharp focus on near eye, authentic skin texture with visible micro-pores, natural color grading."
            candidates = [subject_sentence, optics_condensed, texture_condensed]
            candidate_text = " ".join(candidates)

        # Final ironclad boundary enforcement: strictly <= 1024 chars
        positive_prompt = self.enforce_firefly_limit(candidate_text, max_chars=self.MAX_CHAR_LIMIT)

        # Clean, effective negative prompt for Adobe Firefly's "Exclude from image" box
        negative_prompt = (
            "illustration, 3d render, cartoon, painting, drawing, anime, plastic skin, airbrushed, "
            "oversmoothed, blurry, digital distortion, watermark, text, signature"
        )

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
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
                "exclude_from_image": negative_prompt,
            },
            metadata={
                "model_family": "adobe_firefly",
                "recommended_model": "Firefly Image 5",
                "commercial_safe": True,
                "char_limit": self.MAX_CHAR_LIMIT,
                "char_count": len(positive_prompt),
            },
        )

