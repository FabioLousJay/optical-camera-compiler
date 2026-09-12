"""Raw specification adapter for technical inspection and metadata preservation."""

from __future__ import annotations

from ..models import CameraProfile, CompiledPayload, PaperProfile, SceneInput, TargetEngine
from .base import BaseAdapter


class RawSpecAdapter(BaseAdapter):
    """Outputs the complete structured hardware and optical specification as formatted text."""

    target_engine = TargetEngine.RAW

    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        optics = profile.sensor_and_optics
        lighting = profile.lighting_and_exposure
        micro = profile.micro_detail_and_physics
        shield = profile.negative_embeddings

        lines = [
            f"=== OPTICAL RIG SPECIFICATION: {profile.title} ===",
            f"Subject: {scene.subject}",
            f"Framing: {scene.framing or 'Not specified'}",
            f"Environment: {scene.environment or 'Studio / Neutral'}",
            f"Wardrobe: {scene.wardrobe or 'Not specified'}",
            f"Mood: {scene.mood or 'Neutral / Editorial'}",
            "",
            "--- Sensor & Optics ---",
            f"Camera System: {optics.camera_system}",
            f"Sensor Type: {optics.sensor_type} ({optics.sensor_dimensions})",
            f"Lens: {optics.lens} @ {optics.aperture_sweet_spot}",
            f"Field of View: {optics.full_frame_equivalent}",
            f"Shutter: {optics.shutter}",
            f"Sensitivity & Latitude: {optics.iso_base}, {optics.dynamic_range}",
            "",
            "--- Lighting & Light Transport ---",
            f"Primary: {lighting.primary_lighting}",
            f"Modifiers & Fill: {lighting.light_transport}",
            "",
            "--- Micro-Detail & Physics Directives ---",
            *[f"- {item}" for item in micro.surface_rendering],
            *[f"- {item}" for item in micro.depth_and_optics],
            "",
            "--- Execution Directive ---",
            profile.execution_directive,
        ]

        if scene.has_product_lock:
            lines.extend([
                "",
                "--- Commercial Product Fidelity & 100% Approval Gate ---",
                f"Product Crop Reference: {scene.product_crop or 'Attached reference crop'}",
                f"SKU Color: {scene.sku_color or 'Locked to reference'}",
                f"Cap & Closure Geometry: {scene.cap_geometry or 'Locked to reference'}",
                f"Label Kerning & Typography: {scene.label_kerning or 'Locked to reference'}",
                f"Manufacturing Seams: {scene.seam_geometry or 'Locked to reference'}",
                f"Material Finish: {scene.material_finish or 'Locked to reference'}",
                f"100% Approval Gate: {'ENFORCED' if scene.approval_gate_100pct else 'DISABLED'}",
            ])

        if scene.is_anamorphic:
            lines.extend([
                "",
                "--- Cinema Anamorphic Optics & Flare Engine ---",
                f"Squeeze Factor: {scene.anamorphic_squeeze.value if scene.anamorphic_squeeze else '2.0x'}",
                f"Streak Flare Coating: {scene.streak_flare.value if scene.streak_flare else 'cyan_blue'}",
                f"Iris Blades: {scene.iris_blades.value if scene.iris_blades else '14_blade_circular'}",
                "Bokeh Geometry: 2:1 vertical elliptical oval bokeh discs",
                "Diffraction Spikes: Symmetric starburst flare spikes derived from iris blade count",
            ])

        if scene.has_copy_space or scene.gobo or scene.grip_modifier or scene.lighting_ratio:
            lines.extend([
                "",
                "--- Commercial Advertising Framing & Copy-Space ---",
                f"Negative Copy-Space: {scene.copy_space.value if scene.copy_space else 'none'}",
                f"Advertising Safe-Zone: {scene.ad_safe_zone.value if scene.ad_safe_zone else 'none'}",
                f"Gobo Projection Cookie: {scene.gobo.value if scene.gobo else 'none'}",
                f"Studio Grip Modifier: {scene.grip_modifier.value if scene.grip_modifier else 'none'}",
                f"Lighting Contrast Ratio: {scene.lighting_ratio.value if scene.lighting_ratio else 'none'}",
            ])

        if scene.has_hand_lock:
            lines.extend([
                "",
                "--- Biomechanical Hand & Finger Precision Gate ---",
                f"Grip Type: {scene.grip_type.value if scene.grip_type else 'ergonomic_contact_grip'}",
                f"Hand Details: {scene.hand_details or 'Natural 5-finger anatomical articulation'}",
                "Gate H1 (Metacarpal Proportions): 5-ray architecture, 2:3:4:3.5:2.5 length ratio, distinct MCP/PIP/DIP joints",
                "Gate H2 (Grip Physics): Contact tissue blanching under pressure, zero solid-object clipping",
                "Gate H3 (Flexion Creases): Authentic palmar lines, defined thenar musculature, wrist tendon tension",
                "Gate H4 (Nail Bed Realism): Translucent nail plate, pink vascular flush, pale lunula crescent, micro-cuticles",
                "Gate H5 (Mutation Shield): 100% rejection of fused digits, extra phalanges, rubber knuckles, dislocated thumbs",
            ])

        if scene.is_policy_safe:
            lines.extend([
                "",
                "--- Policy-Safe Compliance Recovery Directive ---",
                "Status: ENFORCED",
                "Compliance Mode: Tasteful editorial fine-art, fully clothed subjects, strictly safe platform output",
                "Preservation: Camera physics, optical acutance, authentic lighting, and anatomical fidelity fully locked",
            ])

        if scene.has_body_morphology:
            regions = scene.body_volume or (", ".join(scene.body_morphology.volume_regions) if scene.body_morphology and scene.body_morphology.volume_regions else "biceps, chest, gut")
            lines.extend([
                "",
                "--- Body Morphology & Proportional Volume Calibration ---",
                f"Volume Target Regions: {regions}",
                f"Calibrated Weight: {scene.weight_lb} lbs" if scene.weight_lb else "Calibrated Weight: Frame-proportional",
                "Proportionality Rule: Proportional to skeletal frame, head size, and total mass",
                "Bilateral Asymmetry: Authentic human asymmetry strictly preserved (anti-mirroring)",
                "Soft-Tissue Mechanics: Believable gravity, seated abdominal compression, continuous anatomical contours",
                "Clothing Conformity: Authentic garment tension and stretch over enlarged mass",
                "Anti-Exaggeration Lock: Absolute prohibition of cartoon musculature or caricature ballooning",
            ])

        if scene.has_material_style or scene.is_4d_volumetric:
            lines.extend([
                "",
                "--- 4D Volumetric & Premium Material Engine ---",
                f"Material Style: {scene.material_style.value if scene.material_style else 'dimensional_volumetric'}",
                f"Background Style: {scene.background_style.value if scene.background_style else 'default'}",
                "Volumetric Rendering: Tangible foreground-background separation, rim contour lighting, deep tonal isolation",
                "Specular Physics: Controlled micro-contrast, realistic surface curvature, uncompressed specular highlights",
                f"Conditional Text Removal: {'ENFORCED' if scene.remove_text_when_present else 'DISABLED'}",
            ])

        if scene.is_print_calibrated:
            paper_name = scene.paper_profile.value if scene.paper_profile and scene.paper_profile != PaperProfile.NONE else (scene.print_spec.paper.value if scene.print_spec and scene.print_spec.paper != PaperProfile.NONE else 'fine_art')
            lines.extend([
                "",
                "--- Print-Calibrated Prepress & Exhibition Lab Matrix ---",
                f"Paper Profile: {paper_name}",
            ])
            if scene.print_spec:
                lines.extend([
                    f"Physical Print Size: {scene.print_spec.width_in}\" x {scene.print_spec.height_in}\" @ {scene.print_spec.ppi} PPI",
                    f"Pixel Dimensions: {int(round(scene.print_spec.width_in * scene.print_spec.ppi))} x {int(round(scene.print_spec.height_in * scene.print_spec.ppi))}",
                    f"Rendering Intent: {scene.print_spec.rendering_intent.value}",
                ])

        positive_prompt = "\n".join(lines)
        negative_prompt = ", ".join(
            shield.all_tokens(
                include_product_drift=scene.has_product_lock,
                include_hand_drift=scene.has_hand_lock,
                include_body_distortion=scene.has_body_morphology,
            )
        )

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            parameters={"aspect_ratio": scene.aspect_ratio},
            metadata=profile.to_dict(),
        )
