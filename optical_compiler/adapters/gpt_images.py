"""GPT Images (ChatGPT / GPT-4o / DALL-E 3) Adapter.

Implements the Master Execution Prompt protocol specifically optimized for GPT models,
enforcing exact camera optics, lighting geometry, subject stability, and hard constraints.
"""

from __future__ import annotations

from typing import Any

from ..models import (
    CameraProfile,
    CompiledPayload,
    ReferenceMode,
    SceneInput,
    TargetEngine,
)
from .base import BaseAdapter


class GPTImagesAdapter(BaseAdapter):
    """Adapter producing structured Master Execution Prompts for GPT-based image generation."""

    @property
    def target_engine(self) -> TargetEngine:
        return TargetEngine.GPT_IMAGES

    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        sections = []

        # 1. Base instruction / Subject block
        is_ref = bool(scene.reference and scene.reference.mode != ReferenceMode.NONE)
        ref_mode = scene.reference.mode if (scene.reference and scene.reference.mode) else ReferenceMode.NONE

        if ref_mode == ReferenceMode.OUTPAINT_FULL_BODY:
            base_instr = (
                "Base instruction: Using the provided medium-shot photo as the base. "
                "Outpaint and extend the frame downward into a full-body portrait. "
                "Preserve the subject's face, identity, expression, hair, and skin texture exactly as in the input image. "
                "Keep the same wardrobe, colors, fabric texture, and wrinkles. "
                "Maintain the same camera height and perspective. No wide-angle distortion. "
                "Full body head-to-toe visible including shoes."
            )
            sections.append(base_instr)
        elif ref_mode == ReferenceMode.DEPIXELATE_GFX100RF:
            base_instr = (
                "Base instruction (Universal De-Pixelate + Upscale Restoration v3.1 – GFX100RF Signature Lock): "
                "Use the attached image as the mandatory single source of truth. Restore and upscale the attached image "
                "by removing pixelation, blockiness, compression damage, aliasing, mosquito noise, and low-resolution softness "
                "while strictly preserving the source image's true identity, composition, proportions, colors, materials, "
                "lighting logic, text content, and scene integrity. The final output must read as a high-resolution "
                "Fujifilm GFX100RF capture of the same scene, not a reimagined, rewritten, beautified, stylized, or regenerated version. "
                "Do not add, remove, beautify, stylize, paraphrase, rewrite, redesign, or reinterpret any element. "
                f"Subject: {scene.subject}."
            )
            sections.append(base_instr)
        elif ref_mode == ReferenceMode.IDENTITY_LOCK:
            base_instr = (
                "Base instruction (Identity-Locked Editorial Portrait): "
                "Subject must strictly follow the anatomical structure, facial geometry, body proportions, mass, "
                "hair pattern, beard pattern (if present), and physical presence from the attached reference image. "
                "Strictly prohibits gender reinterpretation, age alteration, body type modification, body slimming, "
                "body reshaping, facial restructuring, jawline softening, feature feminization or masculinization, "
                "weight redistribution, and skin smoothing beyond realism. "
                f"Subject: {scene.subject}."
            )
            if scene.wardrobe:
                base_instr += f" Wardrobe: {scene.wardrobe}."
            if scene.environment:
                base_instr += f" Environment: {scene.environment}."
            sections.append(base_instr)
        elif ref_mode == ReferenceMode.RESTORE_UPSCALE:
            base_instr = (
                f"Base instruction: Using the provided image as the base. "
                f"Preserve identity exactly. Facial structure, bone geometry, hairline, skin texture, pores, "
                f"wrinkles, and micro-asymmetries must remain unchanged. No beautification. No identity drift. "
                f"Wardrobe, glasses, and all accessories remain identical. No substitutions. No reinterpretation. "
                f"Camera height and perspective locked. Head angle and crop preserved. "
                f"Subject: {scene.subject}."
            )
            sections.append(base_instr)
        elif ref_mode == ReferenceMode.TRANSFORM_ADAPT:
            base_instr = (
                f"Base instruction: Photographic adaptation with biometric character lock. "
                f"Preserve the subject's exact facial structure, bone geometry, gaze, and identity from the reference image. "
                f"Adapt the scene according to: {scene.subject}. "
                + (f"Environment: {scene.environment}. " if scene.environment else "")
                + (f"Wardrobe: {scene.wardrobe}. " if scene.wardrobe else "")
            )
            sections.append(base_instr)
        else:
            base_instr = f"Subject: {scene.subject}."
            if scene.environment:
                base_instr += f" Environment: {scene.environment}."
            if scene.wardrobe:
                base_instr += f" Wardrobe: {scene.wardrobe}."
            if scene.framing:
                base_instr += f" Framing: {scene.framing}."
            sections.append(base_instr)

        # Camera angle & framing block
        if scene.camera_angle:
            angle_block = f"Camera angle & perspective: {scene.camera_angle}. Framing: {scene.framing or 'Subject centered'}."
            sections.append(angle_block)

        # Crowd action and motion physics
        if scene.crowd_action:
            crowd_block = (
                f"Crowd action and motion physics: {scene.crowd_action}. "
                "Motion blur wraps around the still subject without deforming subject anatomy. "
                "Zero readable faces in blurred crowd, zero duplicated people, zero melted bodies, zero uniform smear wall."
            )
            sections.append(crowd_block)

        # 2. Human skin realism override protocol
        if scene.human_skin_realism or ref_mode == ReferenceMode.DEPIXELATE_GFX100RF:
            skin_override_block = (
                "Human skin realism override protocol: For any visible human skin, human skin realism overrides "
                "micro-detail recovery, perceived resolution, sharpening, and texture reconstruction. "
                "Skin must remain softer than eyes, hair, clothing, jewelry, teeth, text, hard edges, and architecture. "
                "Skin must never become the sharpest texture in the image. Remove AI-generated swirls, decorative micro-patterns, "
                "engraved texture, embossed texture, pore stamping, worm-like texture, lace-like texture, metallic texture, and synthetic skin grain. "
                "Preserve natural uneven skin texture, age-appropriate wrinkles, folds, pores, freckles, moles, age spots, beard texture, stubble, "
                "under-eye texture, neck texture, and hand texture where visible. Do not invent pores or wrinkles unsupported by the source. "
                "Skin tonal transitions must remain smooth and photographic, never carved, crunchy, metallic, or HDR-like."
            )
            sections.append(skin_override_block)

        # 3. Content type reproduction directive
        if scene.content_type and scene.content_type.is_flat_reproduction:
            repro_block = (
                f"Content type reproduction directive ({scene.content_type.value}): "
                "Render as flat reproduction capture. Suppress optical depth-of-field falloff, suppress vignetting, "
                "and suppress film grain texture inappropriate for copy-stand or reproduction context."
            )
            sections.append(repro_block)

        # 4. Text and structured graphics preservation protocol
        if scene.text_preservation or ref_mode == ReferenceMode.DEPIXELATE_GFX100RF:
            text_block = (
                "Text and structured content preservation: All visible text must be preserved exactly as in the source image. "
                "Do not paraphrase, rewrite, correct grammar, fix punctuation, or reinterpret text. "
                "Maintain original line breaks, font style, stroke weight, alignment, hierarchy, and placement. "
                "Preserve all arrows, connectors, boxes, icons, and diagram relationships exactly."
            )
            sections.append(text_block)

        # 5. Focus discipline & Surface rendering
        is_slow_shutter = (
            scene.capture_mode == "slow_shutter_crowd_motion"
            or (hasattr(scene.capture_mode, "value") and scene.capture_mode.value == "slow_shutter_crowd_motion")
            or bool(scene.crowd_action)
            or (profile.profile_id == "leica_sl2" and "motion" in scene.subject.lower())
        )
        if is_slow_shutter:
            focus_block = (
                "Focus discipline: Focus locked on the near eye. Iris and eyelashes tack sharp. "
                "Visible facial pores and authentic skin texture. Subject stands completely still, centered, with tack-sharp presence. "
                "Absolute zero subject motion blur. Camera steady relative to subject; blur originates solely from surrounding crowd motion."
            )
        else:
            focus_block = (
                "Focus discipline: Focus locked on the near eye. Iris and eyelashes tack sharp. "
                "Absolute zero motion blur."
            )
            if scene.sharpness_protocol:
                focus_block += (
                    " Subject stability cues: seated, feet planted, exhale and hold 1 second, capture during the hold. "
                    "Chin slightly forward and down for stabilized head position and defined jawline."
                )
        sections.append(focus_block)

        surface_directives = ". ".join(profile.micro_detail_and_physics.surface_rendering)
        surface_block = (
            "Surface rendering: Natural human skin with visible pores and micro texture. "
            + (
                "Human skin realism prioritized over artificial clarity. Natural organic skin softer than hard edges, eyes, hair, and textiles. "
                if (scene.human_skin_realism and ref_mode == ReferenceMode.DEPIXELATE_GFX100RF)
                else ""
            )
            + f"{surface_directives}. "
            + "Accurate dermal subsurface scattering without waxy specularities or artificial blur. "
            + "High micro-contrast on hair, fabric, eyes, and environment. Crisp edges. No haze. No diffusion."
        )
        sections.append(surface_block)

        # 6. Lighting Geometry & Light Transport
        lighting_block = (
            f"Lighting geometry: {scene.lighting or profile.lighting_and_exposure.primary_lighting}. "
            f"Directional key light positioned 35–45° off-axis, slightly above eye line for micro-contrast. "
            f"Minimal fill. Strong black flag negative fill on the shadow side for deep tonal separation. "
            f"Optional very low-power rim light only for edge separation (no glow, no second key). "
            f"Background kept controlled to prevent spill. Contrast is editorial, not cinematic."
        )
        sections.append(lighting_block)

        # Color tone / Monochrome
        if scene.is_monochrome:
            mono_block = (
                "Color tone: Restrained black-and-white, inspired by indie-cinema monochrome; "
                "gentle highlight roll-off; clean midtones; no HDR; fine, subtle, consistent organic film grain."
            )
            sections.append(mono_block)

        # 7. Camera Hardware & Lens Module
        cam = profile.sensor_and_optics
        color_desc = f" Color science: {cam.dynamic_range}." if cam.dynamic_range else ""
        camera_block = (
            f"Camera hardware: Shot on {cam.camera_system}. "
            f"Lens: {cam.lens} set to {cam.aperture_sweet_spot}. "
            f"Sensor: {cam.sensor_dimensions}, {cam.sensor_type}. "
            f"Exposure: {cam.shutter}, base {cam.iso_base}.{color_desc} "
            f"Clean rectilinear projection with zero perspective distortion."
        )
        sections.append(camera_block)

        # 8. Output Resolution Target & File Quality
        if ref_mode == ReferenceMode.DEPIXELATE_GFX100RF:
            res = scene.output_resolution or "102MP Medium Format (11648 x 8736 native GFX100RF resolution, scaled to source aspect ratio)"
        else:
            res = scene.output_resolution or self._resolve_default_resolution(scene.aspect_ratio)
        res_block = (
            f"Output specification: {res}. "
            f"Uncompressed 16-bit raw tonal latitude, maximum acutance without JPEG compression artifacts, "
            f"zero chroma subsampling (4:4:4)."
        )
        sections.append(res_block)

        # 9. Negative constraints embedded in natural language
        neg_tokens = profile.negative_embeddings.all_tokens(
            include_anti_drift=is_ref,
            include_branding=scene.suppress_text_branding,
            include_compression=True,
            include_outpaint=(ref_mode == ReferenceMode.OUTPAINT_FULL_BODY),
            include_skin_realism=scene.human_skin_realism,
        )
        if scene.custom_negatives:
            neg_tokens.extend(scene.custom_negatives)

        hard_neg = (
            "Hard negative constraints (MUST ELIMINATE): "
            + ", ".join(neg_tokens)
            + "."
        )
        sections.append(hard_neg)

        positive_prompt = "\n\n".join(sections)
        negative_prompt = ", ".join(neg_tokens)

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            parameters={
                "aspect_ratio": scene.aspect_ratio,
                "resolution": res,
                "camera": cam.camera_system,
                "lens": cam.lens,
                "aperture": cam.aperture_sweet_spot,
                "shutter": cam.shutter,
                "iso": cam.iso_base,
            },
            metadata={
                "profile_id": profile.profile_id,
                "protocol": "Brutally Sharp Portrait Prompt Kit (Page 17 Master Execution)",
            },
        )

    def _resolve_default_resolution(self, aspect_ratio: str) -> str:
        """Map aspect ratio to exact uncompressed resolution string."""
        mapping = {
            "9:11": "12MP PNG, vertical 9:11 aspect ratio (3132 x 3828)",
            "4:5": "12MP PNG, vertical 4:5 aspect ratio (3100 x 3875)",
            "3:2": "12MP PNG, vertical 3:2 aspect ratio (4248 x 2832)",
            "4:3": "12MP PNG, vertical 4:3 aspect ratio (4000 x 3000)",
            "5:4": "12MP PNG, vertical 5:4 aspect ratio (3875 x 3100)",
            "16:9": "8K UHD (7680 x 4320, 16:9 aspect ratio, 33.2 MP uncompressed)",
            "1:1": "12MP PNG, square 1:1 aspect ratio (3464 x 3464)",
            "21:9": "Ultra-wide 21:9 uncompressed raster (5040 x 2160)",
            "9:16": "Vertical 9:16 high-resolution format (2160 x 3840)",
        }
        return mapping.get(aspect_ratio, f"12MP PNG, {aspect_ratio} aspect ratio")
