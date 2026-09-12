"""Raw specification adapter for technical inspection and metadata preservation."""

from __future__ import annotations

from ..models import CameraProfile, CompiledPayload, SceneInput, TargetEngine
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

        positive_prompt = "\n".join(lines)
        negative_prompt = ", ".join(shield.all_tokens(include_product_drift=scene.has_product_lock))

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            parameters={"aspect_ratio": scene.aspect_ratio},
            metadata=profile.to_dict(),
        )
