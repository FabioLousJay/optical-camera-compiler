"""Tests for Leica SL2 hardware profile, slow-shutter motion-blur crowd physics, and identity lock."""

from __future__ import annotations

import json
import unittest

from optical_compiler import (
    CaptureMode,
    ContentType,
    LightingPreset,
    OpticalCompiler,
    ReferenceImageInput,
    ReferenceMode,
    SceneInput,
    TargetEngine,
    auto_select_profile,
    compile_scene,
    load_profile,
)


class TestLeicaSL2MotionBlur(unittest.TestCase):
    """Test suite for Leica SL2, slow-shutter crowd motion, and strict identity lock."""

    def test_leica_sl2_profile_specifications(self) -> None:
        """Verify the Leica SL2 profile contains exact hardware, lens, and shutter specs."""
        profile = load_profile("leica_sl2")
        self.assertEqual(profile.profile_id, "leica_sl2")
        self.assertIn("Leica SL2", profile.title)
        self.assertIn("47.3MP", profile.sensor_and_optics.sensor_dimensions)
        self.assertIn("Summilux", profile.sensor_and_optics.lens)
        self.assertEqual(profile.sensor_and_optics.aperture_sweet_spot, "f/2.8")
        self.assertIn("Maestro III", profile.sensor_and_optics.camera_system)
        self.assertIn("slow shutter motion-blur", profile.sensor_and_optics.shutter)

        # Negative embeddings
        neg = profile.negative_embeddings.all_tokens(include_anti_drift=True)
        self.assertIn("ghost faces in crowd", neg)
        self.assertIn("melted bodies", neg)
        self.assertIn("gender reinterpretation", neg)
        self.assertIn("body slimming", neg)

    def test_auto_router_leica_sl2(self) -> None:
        """Verify intelligent auto-router routes motion-blur crowd and Leica SL2 scenes."""
        p1 = auto_select_profile("Cinematic motion-blur photography shot on a Leica SL2 with a 50mm Summilux at f/2.8")
        self.assertEqual(p1, "leica_sl2")

        p2 = auto_select_profile("Editorial calm vs chaos with slow shutter motion-blur crowd")
        self.assertEqual(p2, "leica_sl2")

        p3 = auto_select_profile("Chest-level frontal portrait with commuters rushing past creating motion blur")
        self.assertEqual(p3, "leica_sl2")

    def test_capture_mode_slow_shutter_crowd_motion(self) -> None:
        """Verify CaptureMode.SLOW_SHUTTER_CROWD_MOTION directive and parsing."""
        cm1 = CaptureMode.from_str("slow_shutter_crowd_motion")
        self.assertEqual(cm1, CaptureMode.SLOW_SHUTTER_CROWD_MOTION)

        cm2 = CaptureMode.from_str("calm_vs_chaos")
        self.assertEqual(cm2, CaptureMode.SLOW_SHUTTER_CROWD_MOTION)

        cm3 = CaptureMode.from_str("motion_blur_crowd")
        self.assertEqual(cm3, CaptureMode.SLOW_SHUTTER_CROWD_MOTION)

    def test_lighting_preset_flat_overcast(self) -> None:
        """Verify LightingPreset.FLAT_OVERCAST applies soft diffusion and low contrast."""
        lp = LightingPreset.from_str("flat_overcast")
        self.assertEqual(lp, LightingPreset.FLAT_OVERCAST)

        compiler = OpticalCompiler(profile="leica_sl2")
        payload = compiler.compile(
            "Subject in station",
            target="gpt_images",
            lighting_preset="flat_overcast",
        )
        self.assertIn("Flat overcast daylight", payload.positive_prompt)

    def test_reference_mode_identity_lock(self) -> None:
        """Verify ReferenceMode.IDENTITY_LOCK parsing and anti-drift tokens."""
        mode = ReferenceMode.from_str("identity_lock")
        self.assertEqual(mode, ReferenceMode.IDENTITY_LOCK)

        mode_alias = ReferenceMode.from_str("identity")
        self.assertEqual(mode_alias, ReferenceMode.IDENTITY_LOCK)

    def test_gpt_images_motion_blur_and_identity_lock(self) -> None:
        """Verify GPT Images adapter generates identity lock, crowd action, angle, and monochrome."""
        compiler = OpticalCompiler(profile="leica_sl2")
        scene = SceneInput(
            subject="The attached reference person standing completely still, calm quiet rebellion through stillness",
            framing="medium portrait (waist-up to mid-torso), subject centered",
            camera_angle="chest-level frontal angle",
            crowd_action="hundreds of commuters rushing past in all directions, bodies stretched into smooth horizontal and diagonal motion-blur trails",
            color_mode="monochrome",
            aspect_ratio="4:5",
            capture_mode="slow_shutter_crowd_motion",
            reference=ReferenceImageInput(
                filename="person.jpg",
                mode=ReferenceMode.IDENTITY_LOCK,
                fidelity_lock=1.0,
            ),
        )
        payload = compiler.compile(scene, target="gpt_images")
        prompt = payload.positive_prompt

        self.assertIn("Base instruction (Identity-Locked Editorial Portrait):", prompt)
        self.assertIn("gender reinterpretation", prompt)
        self.assertIn("body slimming", prompt)
        self.assertIn("Camera angle & perspective: chest-level frontal angle", prompt)
        self.assertIn("Crowd action and motion physics: hundreds of commuters rushing past", prompt)
        self.assertIn("Focus discipline: Focus locked on the near eye", prompt)
        self.assertIn("Camera steady relative to subject; blur originates solely from surrounding crowd motion", prompt)
        self.assertIn("Color tone: Restrained black-and-white, inspired by indie-cinema monochrome", prompt)
        self.assertIn("Camera hardware: Shot on Leica SL2", prompt)
        self.assertIn("Summilux", prompt)
        self.assertIn("ghost faces in crowd", payload.negative_prompt)
        self.assertIn("melted bodies", payload.negative_prompt)

    def test_imagen_motion_blur_adapter(self) -> None:
        """Verify Imagen/Gemini adapter weaves Leica SL2 and crowd blur into prose."""
        compiler = OpticalCompiler(profile="leica_sl2")
        scene = SceneInput(
            subject="Person standing completely still",
            camera_angle="chest-level frontal angle",
            crowd_action="hundreds of commuters rushing past in multiple directions creating layered motion blur trails",
            color_mode="monochrome",
            aspect_ratio="4:5",
            capture_mode="slow_shutter_crowd_motion",
            reference=ReferenceImageInput(
                filename="person.jpg",
                mode=ReferenceMode.IDENTITY_LOCK,
            ),
        )
        payload = compiler.compile(scene, target="imagen")
        prompt = payload.positive_prompt

        self.assertIn("Strict anatomical identity lock", prompt)
        self.assertIn("Leica SL2", prompt)
        self.assertIn("Summilux", prompt)
        self.assertIn("chest-level frontal angle", prompt)
        self.assertIn("restrained black-and-white indie-cinema monochrome", prompt)
        self.assertIn("surrounded by hundreds of commuters rushing past", prompt)
        self.assertIn("subject completely stationary with zero subject motion blur while crowd flows", prompt)

    def test_midjourney_motion_blur_adapter(self) -> None:
        """Verify Midjourney adapter produces --sref, --ar 4:5, --style raw, --v 8.2, and --no flags."""
        compiler = OpticalCompiler(profile="leica_sl2")
        scene = SceneInput(
            subject="Person standing completely still",
            camera_angle="chest-level frontal angle",
            crowd_action="commuters rushing past with motion blur trails",
            color_mode="monochrome",
            aspect_ratio="4:5",
            capture_mode="slow_shutter_crowd_motion",
            reference=ReferenceImageInput(
                filename="person.jpg",
                mode=ReferenceMode.IDENTITY_LOCK,
            ),
        )
        payload = compiler.compile(scene, target="midjourney")
        prompt = payload.positive_prompt

        self.assertIn("--ar 4:5", prompt)
        self.assertIn("--style raw", prompt)
        self.assertIn("--v 8.2", prompt)
        self.assertIn("--sref person.jpg", prompt)
        self.assertIn("--iw 2.0", prompt)
        self.assertIn("--cw 100", prompt)
        self.assertIn("standing completely still subject, tack-sharp eyes", prompt)
        self.assertIn("shot on Leica SL2", prompt)
        self.assertIn("--no", prompt)
        self.assertIn("color", prompt)
        self.assertIn("ghost faces", prompt)

    def test_flux_motion_blur_adapter(self) -> None:
        """Verify Flux adapter produces narrative description with embedded negative assertions."""
        compiler = OpticalCompiler(profile="leica_sl2")
        scene = SceneInput(
            subject="Person standing still",
            camera_angle="chest-level frontal angle",
            crowd_action="commuters rushing past in all directions",
            color_mode="monochrome",
            aspect_ratio="4:5",
            capture_mode="slow_shutter_crowd_motion",
            reference=ReferenceImageInput(
                filename="person.jpg",
                mode=ReferenceMode.IDENTITY_LOCK,
            ),
        )
        payload = compiler.compile(scene, target="flux")
        prompt = payload.positive_prompt

        self.assertIn("Documentary editorial portrait with strict reference identity lock", prompt)
        self.assertIn("Shot on a Leica SL2", prompt)
        self.assertIn("Summilux", prompt)
        self.assertIn("Restrained black-and-white indie-cinema monochrome", prompt)
        self.assertIn("Eliminate ghost faces, melted bodies, duplicated people", prompt)

    def test_sdxl_motion_blur_adapter(self) -> None:
        """Verify SDXL adapter outputs structured positive and negative payloads."""
        compiler = OpticalCompiler(profile="leica_sl2")
        scene = SceneInput(
            subject="Person standing still",
            camera_angle="chest-level frontal angle",
            crowd_action="commuters rushing past in motion blur trails",
            color_mode="monochrome",
            aspect_ratio="4:5",
            capture_mode="slow_shutter_crowd_motion",
            reference=ReferenceImageInput(
                filename="person.jpg",
                mode=ReferenceMode.IDENTITY_LOCK,
            ),
        )
        payload = compiler.compile(scene, target="sdxl")

        self.assertIn("Leica SL2", payload.positive_prompt)
        self.assertIn("Summilux", payload.positive_prompt)
        self.assertIn("chest-level frontal angle", payload.positive_prompt)
        self.assertIn("restrained black-and-white indie-cinema monochrome", payload.positive_prompt)
        self.assertIn("ghost faces in crowd", payload.negative_prompt)
        self.assertIn("melted bodies", payload.negative_prompt)

    def test_json_all_in_one_motion_blur_adapter(self) -> None:
        """Verify JSON All-in-One Prompt contains schema 3.1 and identity lock protocol."""
        compiler = OpticalCompiler(profile="leica_sl2")
        scene = SceneInput(
            subject="Person standing completely still",
            camera_angle="chest-level frontal angle",
            crowd_action="hundreds of commuters rushing past",
            color_mode="monochrome",
            aspect_ratio="4:5",
            capture_mode="slow_shutter_crowd_motion",
            reference=ReferenceImageInput(
                filename="person.jpg",
                mode=ReferenceMode.IDENTITY_LOCK,
            ),
        )
        payload = compiler.compile(scene, target="json")
        data = json.loads(payload.positive_prompt)

        self.assertIn(data["schema_version"], ("3.1", "3.2"))
        self.assertIn("Identity-Locked", data["protocol"])
        self.assertEqual(data["scene"]["camera_angle"], "chest-level frontal angle")
        self.assertEqual(data["scene"]["color_mode"], "monochrome")
        self.assertEqual(data["scene"]["crowd_action"], "hundreds of commuters rushing past")
        self.assertEqual(data["camera_hardware"]["profile_id"], "leica_sl2")
        self.assertIn("prohibited_drift", data["reference_image"])
        self.assertIn("gender reinterpretation", data["reference_image"]["prohibited_drift"])
        self.assertIn("gpt_images", data["compiled_prompts"])
        self.assertIn("midjourney_v8_2", data["compiled_prompts"])


if __name__ == "__main__":
    unittest.main()
