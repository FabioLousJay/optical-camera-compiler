"""Comprehensive test suite for Universal De-Pixelate + Upscale Restoration Prompt v2.0
and the Leica Q3 Monochrom hardware profile.
"""

from __future__ import annotations

import json
import unittest

from optical_compiler.compiler import OpticalCompiler, compile_scene
from optical_compiler.models import (
    APPROVED_RESTORATION_CAMERAS,
    APPROVED_RESTORATION_LENSES,
    DEFAULT_FLAT_GRAPHIC_SELECTION,
    DEFAULT_MONOCHROME_SELECTION,
    ContentType,
    ReferenceImageInput,
    ReferenceMode,
    SceneInput,
    TargetEngine,
    UniversalDepixelateV2Spec,
)
from optical_compiler.profiles import auto_select_profile, load_profile


class TestLeicaQ3MonochromProfile(unittest.TestCase):
    """Test loading, hardware specs, and aliases for Leica Q3 Monochrom."""

    def test_load_leica_q3_monochrom_direct(self):
        profile = load_profile("leica_q3_monochrom")
        self.assertEqual(profile.profile_id, "leica_q3_monochrom")
        self.assertIn("Leica Q3 Monochrom", profile.title)
        self.assertIn("Leica Q3 Monochrom", profile.sensor_and_optics.camera_system)
        self.assertIn("60.3MP", profile.sensor_and_optics.sensor_type)
        self.assertIn("Color Filter Array", profile.sensor_and_optics.sensor_type)
        self.assertIn("Summilux 28mm f/1.7", profile.sensor_and_optics.lens)
        self.assertIn("125", profile.sensor_and_optics.iso_base)

    def test_profile_aliases(self):
        aliases = ["leica_q3", "q3_monochrom", "q3m", "q3", "LEICA_Q3_MONOCHROM"]
        for alias in aliases:
            p = load_profile(alias)
            self.assertEqual(p.profile_id, "leica_q3_monochrom", f"Failed for alias: {alias}")

        # Check Sony A7R V aliases as well
        sony_aliases = ["sony_a7rv", "sony_a7r_v", "sony_alpha_7r_v", "a7rv", "a7r5"]
        for s_alias in sony_aliases:
            p = load_profile(s_alias)
            self.assertEqual(p.profile_id, "sony_a7rv", f"Failed for alias: {s_alias}")

        # Check Leica SL3 alias
        sl3 = load_profile("leica_sl3")
        self.assertEqual(sl3.profile_id, "leica_sl3_p")

    def test_approved_cameras_and_lenses_constants(self):
        self.assertIn("Sony Alpha 7R V", APPROVED_RESTORATION_CAMERAS)
        self.assertIn("Sony a1 II", APPROVED_RESTORATION_CAMERAS)
        self.assertIn("Leica SL3", APPROVED_RESTORATION_CAMERAS)
        self.assertIn("Leica Q3 Monochrom", APPROVED_RESTORATION_CAMERAS)
        self.assertEqual(len(APPROVED_RESTORATION_LENSES), 19)
        self.assertEqual(DEFAULT_FLAT_GRAPHIC_SELECTION["camera"], "Sony Alpha 7R V")
        self.assertEqual(DEFAULT_FLAT_GRAPHIC_SELECTION["lens"], "Sony 55mm f/1.8 Sonnar T FE ZA")
        self.assertEqual(DEFAULT_MONOCHROME_SELECTION["camera"], "Leica Q3 Monochrom")
        self.assertEqual(DEFAULT_MONOCHROME_SELECTION["lens"], "Leica Summilux 28mm f/1.7 ASPH")


class TestCameraRouterAndAutoSelection(unittest.TestCase):
    """Test routing logic for depixelate_v2."""

    def test_monochrome_routes_to_q3_monochrom(self):
        scene = SceneInput(
            subject="Degraded vintage photograph",
            color_mode="monochrome",
            depixelate_v2=UniversalDepixelateV2Spec(content_type="photograph"),
        )
        profile_id = auto_select_profile(scene)
        self.assertEqual(profile_id, "leica_q3_monochrom")

    def test_flat_graphic_routes_to_sony_a7rv(self):
        for ctype in ["document_scan", "poster_or_flyer", "meme_or_infographic", "ui_or_screenshot"]:
            scene = SceneInput(
                subject="Scanned document with compression artifacts",
                content_type=ContentType.from_str(ctype),
                depixelate_v2=UniversalDepixelateV2Spec(content_type=ctype),
            )
            profile_id = auto_select_profile(scene)
            self.assertEqual(profile_id, "sony_a7rv", f"Failed routing for {ctype}")

    def test_compiler_defaults_monochrome_lens(self):
        compiler = OpticalCompiler(profile="auto")
        payload = compiler.compile(
            scene="Old family snapshot",
            color_mode="monochrome",
            depixelate_v2=True,
            target="raw",
        )
        self.assertIn("Leica Q3 Monochrom", payload.positive_prompt)
        self.assertIn("Summilux 28mm f/1.7", payload.positive_prompt)

    def test_compiler_defaults_flat_graphic_lens(self):
        compiler = OpticalCompiler(profile="auto")
        payload = compiler.compile(
            scene="Low-res infographic chart with blurry text",
            content_type="meme_or_infographic",
            depixelate_v2=True,
            target="raw",
        )
        self.assertIn("Sony Alpha 7R V", payload.positive_prompt)
        self.assertIn("Sony 55mm f/1.8 Sonnar T FE ZA", payload.positive_prompt)


class TestAdaptersDepixelateV2(unittest.TestCase):
    """Test all 7 adapters with Universal De-Pixelate v2.0."""

    def setUp(self):
        self.compiler = OpticalCompiler(profile="sony_a7rv")
        self.ref = ReferenceImageInput(
            filename="source_blurry.png",
            mode=ReferenceMode.DEPIXELATE_V2,
            fidelity_lock=0.98,
        )

    def test_gpt_images_adapter(self):
        payload = self.compiler.compile(
            scene="Portrait of a craftsman in his workshop",
            reference=self.ref,
            depixelate_v2=True,
            target="gpt_images",
        )
        text = payload.positive_prompt
        self.assertIn("Universal De-Pixelate + Upscale Restoration Prompt v2.0", text)
        self.assertIn("single source of truth", text.lower())
        self.assertIn("Repair priorities:", text)
        self.assertIn("Text preservation & OCR safety protocol", text)
        self.assertIn("Confidence-based detail reconstruction", text)
        self.assertIn("restyling", payload.negative_prompt)
        self.assertEqual(payload.parameters.get("depixelate_v2"), True)
        self.assertEqual(payload.parameters.get("confidence_mode"), "evidence_proportional")

    def test_imagen_adapter(self):
        payload = self.compiler.compile(
            scene="Vintage portrait of a lady",
            reference=self.ref,
            depixelate_v2=True,
            target="imagen",
        )
        text = payload.positive_prompt
        self.assertIn("Universal De-Pixelate and Upscale Restoration v2.0", text)
        self.assertIn("Universal De-Pixelate v2.0 Protocol", text)
        self.assertIn("OCR Safety", text)
        self.assertIn("restyling", payload.negative_prompt)
        self.assertEqual(payload.parameters.get("reference_mode"), "depixelate_v2")

    def test_midjourney_adapter(self):
        payload = self.compiler.compile(
            scene="Studio portrait",
            reference=self.ref,
            depixelate_v2=True,
            target="midjourney",
        )
        text = payload.positive_prompt
        self.assertIn("Universal De-Pixelate v2.0 restoration", text)
        self.assertIn("--sref source_blurry.png", text)
        self.assertIn("--iw 2.0", text)
        self.assertIn("--cw 100", text)
        self.assertIn("restyling", payload.negative_prompt)
        self.assertEqual(payload.parameters.get("reference_mode"), "depixelate_v2")

    def test_flux_adapter(self):
        payload = self.compiler.compile(
            scene="Street portrait of a traveler",
            reference=self.ref,
            depixelate_v2=True,
            target="flux",
        )
        text = payload.positive_prompt
        self.assertIn("Universal De-Pixelate and Upscale Restoration v2.0", text)
        self.assertIn("Text & OCR Safety Protocol", text)
        self.assertIn("Confidence-based reconstruction", text)
        self.assertIn("restyling", payload.negative_prompt)
        self.assertEqual(payload.parameters.get("reference_mode"), "depixelate_v2")

    def test_sdxl_adapter(self):
        payload = self.compiler.compile(
            scene="Close-up portrait",
            reference=self.ref,
            depixelate_v2=True,
            target="sdxl",
        )
        text = payload.positive_prompt
        self.assertIn("universal de-pixelate and upscale restoration v2.0", text)
        self.assertIn("restyling", payload.negative_prompt)
        self.assertEqual(payload.parameters.get("reference_mode"), "depixelate_v2")

    def test_raw_spec_adapter(self):
        payload = self.compiler.compile(
            scene="Antique portrait",
            reference=self.ref,
            depixelate_v2=True,
            target="raw",
        )
        text = payload.positive_prompt
        self.assertIn("--- Universal De-Pixelate + Upscale Restoration Prompt v2.0 ---", text)
        self.assertIn("Reference Usage Priority: Absolute (single source of truth)", text)
        self.assertIn("OCR & Text Preservation Mode: strict_preserve", text)

    def test_json_prompt_adapter(self):
        payload = self.compiler.compile(
            scene="Archival photograph",
            reference=self.ref,
            depixelate_v2=True,
            target="json",
        )
        data = json.loads(payload.positive_prompt)
        self.assertEqual(data.get("schema_version"), "3.8")
        self.assertEqual(data.get("protocol"), "Universal De-Pixelate + Upscale Restoration Prompt v2.0")
        v2_obj = data.get("universal_depixelate_v2")
        self.assertIsNotNone(v2_obj)
        self.assertTrue(v2_obj.get("active"))
        self.assertEqual(v2_obj.get("reference_usage", {}).get("priority"), "absolute")
        self.assertIn("v2_restoration", data.get("negative_shield", {}))


class TestCLIDepixelateV2(unittest.TestCase):
    """Test CLI parsing and execution with --depixelate-v2."""

    def test_cli_parser_flags(self):
        from optical_compiler.cli import build_parser

        parser = build_parser()
        args = parser.parse_args([
            "Scanned vintage document",
            "--depixelate-v2",
            "--depix-camera", "Sony Alpha 7R V",
            "--depix-lens", "Sony 55mm f/1.8 Sonnar T FE ZA",
            "--target", "flux",
        ])
        self.assertTrue(args.depixelate_v2)
        self.assertEqual(args.depix_camera, "Sony Alpha 7R V")
        self.assertEqual(args.depix_lens, "Sony 55mm f/1.8 Sonnar T FE ZA")


class TestComfyNodeDepixelateV2(unittest.TestCase):
    """Test ComfyUI node integration for depixelate_v2."""

    def test_comfy_node_compile(self):
        from optical_compiler.comfy_nodes import OpticalCameraCompilerNode

        node = OpticalCameraCompilerNode()
        pos, neg, unified = node.compile_optical_prompt(
            camera_rig="Leica Q3 Monochrom Full-Frame (Summilux 28mm f/1.7)",
            model_target="flux",
            subject="Restoration of low-resolution street photograph",
            reference_mode="depixelate_v2",
            content_type="photograph",
        )
        self.assertIn("Universal De-Pixelate and Upscale Restoration v2.0", pos)
        self.assertIn("Leica Q3 Monochrom", pos)
        self.assertIn("restyling", neg)


if __name__ == "__main__":
    unittest.main()
