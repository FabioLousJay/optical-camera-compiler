"""GPT Images (ChatGPT / GPT-4o / DALL-E 3) Adapter.

Implements the Master Execution Prompt protocol specifically optimized for GPT models,
enforcing exact camera optics, lighting geometry, subject stability, and hard constraints.
"""

from __future__ import annotations

from typing import Any

from ..models import (
    AdSafeZone,
    BackgroundStyle,
    CameraProfile,
    CompiledPayload,
    CopySpace,
    MaterialStyle,
    PaperProfile,
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

        # Policy-Safe Compliance Recovery Directive
        if scene.is_policy_safe:
            sections.append(
                "Policy-Safe Compliance Recovery Directive: Maintain an editorial, dignified, fine-art photographic execution strictly adhering to platform safety and ethical guidelines. All subjects are depicted fully clothed in realistic, tasteful, elegant attire. Strictly avoid gratuitous, suggestive, or non-compliant elements while fully preserving authentic camera physics, anatomy, lighting, material realism, and optical fidelity."
            )

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
        elif ref_mode == ReferenceMode.PRODUCT_LOCK or (ref_mode == ReferenceMode.NONE and scene.has_product_lock):
            base_instr = (
                "Base instruction (Commercial Product SKU Lock & Packaging Fidelity Protocol): "
                "The sellable commercial product depicted must match the product-reference crop with 100% engineering and aesthetic fidelity. "
                "Do not redesign, reinterpret, restyle, smooth, warp, or drift any aspect of the product geometry, closure, label, or branding. "
                f"Sellable Object / Subject: {scene.subject}."
            )
            if scene.environment:
                base_instr += f" Environment / Commercial Set: {scene.environment}."
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
        elif ref_mode == ReferenceMode.RECONSTRUCTION_LOCK_4X or scene.has_reconstruction_lock_4x:
            recon_spec = scene.reconstruction_lock
            backend_name = recon_spec.backend.value if recon_spec else "realesrnet_x4plus"
            denoise_val = recon_spec.denoise_strength if recon_spec else 0.15
            blend_val = recon_spec.blend_ratio if recon_spec else 0.20
            base_instr = (
                "Base instruction (Professional 4X Reconstruction Lock Protocol): "
                "Strict 4X linear raster reconstruction ($W_{out}=4W_0$, $H_{out}=4H_0$, 16X pixel area). "
                "Strict source-lock fidelity: preserve exact composition, geography, geology, rock strata, camera angle, and color relationships. "
                "Zero generative hallucination or terrain redesign (diffusion hallucination strictly prohibited). "
                f"Super-resolution reconstruction backend: {backend_name} (denoise strength: {denoise_val}, selective high-frequency blend: {blend_val}). "
                "Sky and atmospheric haze protection: zero noise injection or sharpening artifacts in smooth gradients, clouds, or atmospheric depth. "
                "Anti-model stacking enforced. "
                f"Subject: {scene.subject}."
            )
            if scene.environment:
                base_instr += f" Environment: {scene.environment}."
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

        # Commercial Advertising Copy-Space and Ad-Safe Framing
        if scene.has_copy_space:
            copy_lines = []
            if scene.copy_space and scene.copy_space != CopySpace.NONE:
                cs_desc = scene.copy_space.value.replace("_", " ")
                copy_lines.append(
                    f"Commercial Copy-Space: Asymmetric negative space strictly reserved in {cs_desc} of the frame. "
                    "Background in this zone must remain uncluttered, serene, and calm to accommodate advertising headline typography."
                )
            if scene.ad_safe_zone and scene.ad_safe_zone != AdSafeZone.NONE:
                sz_desc = scene.ad_safe_zone.value.replace("_", " ")
                copy_lines.append(
                    f"Advertising Safe-Zone ({sz_desc}): All vital subject matter, products, faces, and hands strictly positioned within safe boundaries, "
                    "clear of mobile UI overlays and social media navigation bars."
                )
            sections.append("\n".join(copy_lines))

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

        # 5. Product Fidelity & 100% Commercial SKU Approval Gate
        if scene.has_product_lock and scene.approval_gate_100pct:
            gate_lines = [
                "100% Commercial SKU Approval Gate (Mandatory 5-Point Forensic Inspection):",
                "Any render failing any of the following 5 commercial criteria is defective and rejected:",
            ]
            if scene.cap_geometry:
                gate_lines.append(f"- [GATE 1: CAP & CLOSURE GEOMETRY]: Exact physical form factor, diameter, height, knurling count, threading, and closure mechanics. Strictly locked to: {scene.cap_geometry}.")
            else:
                gate_lines.append("- [GATE 1: CAP & CLOSURE GEOMETRY]: Exact physical form factor, diameter, height, knurling count, threading, and closure mechanics matching reference crop 100%. Zero cap substitution, zero missing threads, zero pump/dropper hallucination.")

            if scene.label_kerning:
                gate_lines.append(f"- [GATE 2: LABEL KERNING & TYPOGRAPHY]: Character-for-character typography, font weight, tracking, and letter kerning locked to: {scene.label_kerning}. Zero typographic hallucination, zero warped glyphs.")
            else:
                gate_lines.append("- [GATE 2: LABEL KERNING & TYPOGRAPHY]: Character-for-character typography, font weight, tracking, and letter kerning matching reference crop 100%. Zero typographic hallucination, zero warped glyphs, zero garbled text.")

            if scene.seam_geometry:
                gate_lines.append(f"- [GATE 3: PARTING SEAMS & MOLD LINES]: Exact manufacturing seams, mold parting lines, and edge radiuses locked to: {scene.seam_geometry}.")
            else:
                gate_lines.append("- [GATE 3: PARTING SEAMS & MOLD LINES]: Exact manufacturing seams, mold parting lines, can rims, and edge radiuses matching physical manufacturing.")

            if scene.material_finish:
                gate_lines.append(f"- [GATE 4: MATERIAL FINISH & SPECULAR RESPONSE]: Surface roughness, coating, gloss/satin/matte reflectance, and tactile texture locked to: {scene.material_finish}.")
            else:
                gate_lines.append("- [GATE 4: MATERIAL FINISH & SPECULAR RESPONSE]: Authentic material physics (matte vs satin vs gloss, refractive index, transparency/opacity) matching reference crop 100%. No plastic substitution for glass or metal.")

            if scene.sku_color:
                gate_lines.append(f"- [GATE 5: SKU COLOR & CHROMATIC FIDELITY]: Exact commercial product color locked to: {scene.sku_color}. Zero tint shift, zero lighting contamination on brand color.")
            else:
                gate_lines.append("- [GATE 5: SKU COLOR & CHROMATIC FIDELITY]: Exact commercial product color matching reference crop 100%. Zero tint shift, zero lighting contamination on brand color.")

            sections.append("\n".join(gate_lines))

        # Biomechanical Hand & Finger Precision Gate (5-Point Grip Lock)
        if scene.has_hand_lock:
            grip_desc = scene.grip_type.value.replace("_", " ") if scene.grip_type else "ergonomic contact grip"
            details = f" ({scene.hand_details})" if scene.hand_details else ""
            hand_block = (
                f"Biomechanical Hand & Finger Precision Gate (5-Point Grip Lock - {grip_desc}{details}):\n"
                "- [GATE H1: 5-RAY METACARPAL ARCHITECTURE]: Exactly five fully articulated digits (thumb, index, middle, ring, pinky) "
                "with authentic human anatomical proportions (2:3:4:3.5:2.5 length ratio) and distinct metacarpophalangeal (MCP), "
                "proximal interphalangeal (PIP), and distal interphalangeal (DIP) joints.\n"
                "- [GATE H2: GRIP PHYSICS & CONTACT BLANCHING]: Natural physical contact with object; authentic micro-capillary blood "
                "displacement and tissue blanching where skin compresses against surface. Zero clipping, zero digits penetrating solid objects.\n"
                "- [GATE H3: FLEXION CREASES & THENAR ANATOMY]: Authentic palmar and digital flexion creases, anatomically defined thenar "
                "and hypothenar eminence musculature, visible wrist tendons.\n"
                "- [GATE H4: NAIL BED & CUTICLE REALISM]: Translucent nail plates with natural pinkish vascular flush, visible pale lunula "
                "crescents, micro-cuticles, and clean natural nail margins (no synthetic press-on appearance).\n"
                "- [GATE H5: ZERO FINGER MUTATION SHIELD]: Zero fused digits, zero clipping, zero extra phalanges, zero rubber knuckles, "
                "zero dislocated thumbs, zero webbed fingers, zero amorphous fingertip pads."
            )
            sections.append(hand_block)

        # Body Morphology & Proportional Volume Calibration
        if scene.has_body_morphology:
            regions = scene.body_volume or (", ".join(scene.body_morphology.volume_regions) if scene.body_morphology and scene.body_morphology.volume_regions else "biceps, chest, gut")
            wt = f" with target body mass {scene.weight_lb} lbs" if scene.weight_lb else ""
            morph_lines = [
                f"Body Morphology & Proportional Volume Calibration ({regions}{wt}):",
                "- [PROPORTIONALITY RULE]: All enlarged regions (biceps, chest, gut, legs, waist) must remain strictly proportional to existing skeletal frame, shoulder width, torso width, limb length, head size, and total body mass. Read as one coherent fuller physique rather than isolated inflated parts.",
                "- [NATURAL ASYMMETRY RULE]: Preserve authentic human bilateral asymmetry. Strictly prohibit mechanical mirroring or cloned anatomical forms.",
                "- [GRAVITATIONAL & SOFT-TISSUE BEHAVIOR]: Natural abdominal projection, realistic seated soft-tissue compression, believable weight distribution, and continuous smooth anatomical contours into adjacent musculature.",
                "- [CLOTHING CONFORMITY]: Garments conform and stretch naturally over enlarged body mass while retaining original pattern, color sequence, straps, and construction without breaking or warping.",
                "- [ANTI-EXAGGERATION LOCK]: Absolute prohibition of extreme bodybuilding, comic-book musculature, balloon abdomen, hyper-vascularity, or detached limbs.",
            ]
            sections.append("\n".join(morph_lines))

        # 4D Volumetric & Premium Material Engine
        if scene.has_material_style:
            mat_desc = scene.material_style.value.replace("_", " ") if scene.material_style and scene.material_style != MaterialStyle.NONE else "dimensional volumetric finish"
            bg_desc = f" Background: {scene.background_style.value.replace('_', ' ')}." if scene.background_style and scene.background_style != BackgroundStyle.DEFAULT else ""
            mat_lines = [
                f"4D Volumetric & Premium Material Engine ({mat_desc}):",
                "- [VOLUMETRIC PRESENCE]: Clear foreground-background separation, precise contour rim lighting, deep tonal separation, and tangible 3D/4D volumetric presence (prohibiting temporal motion trails or surreal distortion).",
                "- [MATERIAL PHYSICS]: Realistic surface curvature, controlled specular highlights, rounded dimensional highlights, micro-contrast, and clean edge definition without cheap plastic toy appearance or flat CGI shading.",
            ]
            if bg_desc:
                mat_lines.append(f"- [BACKGROUND ISOLATION]:{bg_desc} Strong subject separation, opaque and non-distracting.")
            sections.append("\n".join(mat_lines))

        # Conditional text removal engine
        if scene.remove_text_when_present:
            sections.append(
                "Text removal engine: Remove letters, words, captions, typography, and decorative lettering only when visibly present in source/reference. "
                "Replace removed text areas with contextually consistent background/material without introducing new symbols or graphics."
            )

        # Print-Calibrated Prepress Specification
        if scene.is_print_calibrated:
            paper_name = scene.paper_profile.value.replace("_", " ") if scene.paper_profile and scene.paper_profile != PaperProfile.NONE else (scene.print_spec.paper.value.replace("_", " ") if scene.print_spec and scene.print_spec.paper != PaperProfile.NONE else "exhibition fine art paper")
            prepress_desc = [f"Print-calibrated exhibition prepress specification ({paper_name}):"]
            if scene.print_spec:
                prepress_desc.append(f"- Target print size: {scene.print_spec.width_in}\" x {scene.print_spec.height_in}\" at {scene.print_spec.ppi} PPI ({int(round(scene.print_spec.width_in * scene.print_spec.ppi))} x {int(round(scene.print_spec.height_in * scene.print_spec.ppi))} pixels).")
                prepress_desc.append(f"- Rendering intent: {scene.print_spec.rendering_intent.value.replace('_', ' ')} with Black Point Compensation.")
            prepress_desc.append(f"- Paper profile: {paper_name}, preserving tonal gradient depth, Dmax response, and zero digital banding.")
            sections.append("\n".join(prepress_desc))

        # 6. Focus discipline & Surface rendering
        is_slow_shutter = (
            scene.capture_mode == "slow_shutter_crowd_motion"
            or (hasattr(scene.capture_mode, "value") and scene.capture_mode.value == "slow_shutter_crowd_motion")
            or bool(scene.crowd_action)
            or (profile.profile_id == "leica_sl2" and "motion" in scene.subject.lower())
        )
        if scene.has_product_lock:
            focus_block = (
                "Focus discipline: Critical focal plane locked on the product's primary brand label, typography, and container shoulder seam. "
                "Tack-sharp edge acutance across the entire packaging silhouette. Absolute zero optical drift, zero motion blur, zero depth-of-field averaging."
            )
        elif is_slow_shutter:
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
        if scene.has_product_lock:
            surface_block = (
                "Surface rendering: Authentic commercial product material physics. "
                + (f"Material finish: {scene.material_finish}. " if scene.material_finish else "Natural material texture without artificial plastic gloss. ")
                + f"{surface_directives}. Crisp product edges, uncompressed specular highlight falloff, zero haze."
            )
        else:
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

        # 7. Lighting Geometry & Light Transport
        lighting_parts = [
            f"Lighting geometry: {scene.lighting or profile.lighting_and_exposure.primary_lighting}."
        ]
        if scene.lighting_ratio:
            lighting_parts.append(f"Key-to-fill contrast ratio: {scene.lighting_ratio.value}.")
        if scene.gobo:
            gobo_desc = scene.gobo.value.replace("_", " ")
            lighting_parts.append(
                f"Optical gobo projection cookie: {gobo_desc} projecting crisp architectural shadow play and dappled light breaks across subject and background."
            )
        if scene.grip_modifier:
            grip_desc = scene.grip_modifier.value.replace("_", " ")
            lighting_parts.append(f"Studio grip modifier: {grip_desc}.")
        lighting_parts.append(
            "Directional key light positioned 35–45° off-axis, slightly above eye line for micro-contrast. "
            "Minimal fill. Strong black flag negative fill on the shadow side for deep tonal separation. "
            "Optional very low-power rim light only for edge separation (no glow, no second key). "
            "Background kept controlled to prevent spill. Contrast is editorial, not cinematic."
        )
        lighting_block = " ".join(lighting_parts)
        sections.append(lighting_block)

        # Color tone / Monochrome
        if scene.is_monochrome:
            mono_block = (
                "Color tone: Restrained black-and-white, inspired by indie-cinema monochrome; "
                "gentle highlight roll-off; clean midtones; no HDR; fine, subtle, consistent organic film grain."
            )
            sections.append(mono_block)

        # 8. Camera Hardware & Lens Module
        cam = profile.sensor_and_optics
        color_desc = f" Color science: {cam.dynamic_range}." if cam.dynamic_range else ""
        lens_spec = cam.lens
        if scene.is_anamorphic:
            squeeze = scene.anamorphic_squeeze.value if scene.anamorphic_squeeze else "2.0x"
            flare = scene.streak_flare.value.replace("_", " ") if scene.streak_flare else "cyan/blue"
            blades = scene.iris_blades.value.replace("_", " ") if scene.iris_blades else "14-blade circular"
            anamorphic_optics = (
                f" Optics: Cinema anamorphic lens with {squeeze} squeeze factor, {flare} horizontal streak flares, and {blades} iris. "
                f"Out-of-focus background highlights render as vertical 2:1 elliptical oval bokeh discs with authentic cylindrical edge astigmatism."
            )
        else:
            anamorphic_optics = " Clean rectilinear projection with zero perspective distortion."

        camera_block = (
            f"Camera hardware: Shot on {cam.camera_system}. "
            f"Lens: {lens_spec} set to {cam.aperture_sweet_spot}. "
            f"Sensor: {cam.sensor_dimensions}, {cam.sensor_type}. "
            f"Exposure: {cam.shutter}, base {cam.iso_base}.{color_desc}"
            f"{anamorphic_optics}"
        )
        sections.append(camera_block)

        # 9. Output Resolution Target & File Quality
        if ref_mode == ReferenceMode.DEPIXELATE_GFX100RF:
            res = scene.output_resolution or "102MP Medium Format (11648 x 8736 native GFX100RF resolution, scaled to source aspect ratio)"
        elif ref_mode == ReferenceMode.RECONSTRUCTION_LOCK_4X or scene.has_reconstruction_lock_4x:
            res = scene.output_resolution or "Exact 4X Linear Source-Locked Reconstruction (16X pixel area, uncompressed master raster)"
        else:
            res = scene.output_resolution or self._resolve_default_resolution(scene.aspect_ratio)
        res_block = (
            f"Output specification: {res}. "
            f"Uncompressed 16-bit raw tonal latitude, maximum acutance without JPEG compression artifacts, "
            f"zero chroma subsampling (4:4:4)."
        )
        sections.append(res_block)

        # 4X Reconstruction Lock Protocol Directives
        if scene.has_reconstruction_lock_4x or ref_mode == ReferenceMode.RECONSTRUCTION_LOCK_4X:
            recon = scene.reconstruction_lock
            b_val = recon.backend.value if recon else "realesrnet_x4plus"
            dn_val = recon.denoise_strength if recon else 0.15
            bl_val = recon.blend_ratio if recon else 0.20
            sky_txt = "Active (zero synthetic noise or haloing in smooth sky/haze)" if (recon is None or recon.protect_sky_haze) else "Disabled"
            sections.append(
                f"4X Reconstruction Lock Directives:\n"
                f"- Linear Dimension Scaling: Exact 4X linear expansion ($W_{{out}} = 4W_0, H_{{out}} = 4H_0$). Area multiplier: 16X.\n"
                f"- Super-Resolution Reconstruction Backend: {b_val} (denoise: {dn_val}, selective detail blend: {bl_val}).\n"
                f"- Sky and Atmospheric Haze Protection: {sky_txt}.\n"
                "- Anti-Model Stacking: Prohibit sequential model cascades.\n"
                "- Strict Source Geometry Lock: Prohibit generative hallucination, geological mutation, or terrain drift."
            )

        # PFEP Diagnostic Stress Probe
        if scene.has_stress_probe and scene.stress_probe:
            sections.append(scene.stress_probe.directive_text)

        # Exhibition Lighting Environment
        if scene.has_lighting_environment and scene.lighting_environment:
            le = scene.lighting_environment
            sections.append(
                f"Exhibition Lighting Calibration: Tuned for gallery presentation at {le.illuminance_lux} lux, "
                f"{le.cct_kelvin}K CCT, with TM-30/CRI {le.spectral_cri} spectral fidelity against {le.wall_surround} surround."
            )

        # Series Visual Cohesion
        if scene.has_series_cohesion and scene.series_cohesion:
            sc = scene.series_cohesion
            sections.append(
                f"Series Cohesion Protocol: Visual cohesion locked to anchor '{sc.anchor_image_id or 'master'}' "
                f"in gallery zone '{sc.gallery_zone or 'primary'}', midtone density target {sc.midtone_density}, "
                f"shadow depth {sc.shadow_depth}, highlight roll-off {sc.highlight_rolloff}."
            )

        # Closed-Loop File Size Constraint
        if scene.min_file_mb:
            sections.append(
                f"Closed-Loop Output Constraint: Non-negotiable minimum file size of {scene.min_file_mb:.1f} MB uncompressed raster."
            )


        # 10. Negative constraints embedded in natural language
        neg_tokens = profile.negative_embeddings.all_tokens(
            include_anti_drift=is_ref,
            include_branding=scene.suppress_text_branding and not scene.has_product_lock,
            include_compression=True,
            include_outpaint=(ref_mode == ReferenceMode.OUTPAINT_FULL_BODY),
            include_skin_realism=scene.human_skin_realism,
            include_product_drift=scene.has_product_lock,
            include_hand_drift=scene.has_hand_lock,
            include_body_distortion=scene.has_body_morphology,
            include_reconstruction_drift=bool(scene.has_reconstruction_lock_4x or ref_mode == ReferenceMode.RECONSTRUCTION_LOCK_4X),
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
            "5:5": "16MP PNG, square 5:5 full-frame ratio (4000 x 4000)",
            "9:12": "44.2MP PNG, vertical 9:12 aspect ratio (5760 x 7680, 8K-class master)",
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
