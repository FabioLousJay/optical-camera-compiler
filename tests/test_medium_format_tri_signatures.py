"""Test suite for Medium Format Tri-Signature Architecture & Universal Master Override.

Validates:
1. Module A: Phase One XF + IQ4 150MP (Resolving Authority, 151MP, 110mm LS f/2.8, ISO 50, 15 stops DR)
2. Module B: Hasselblad X2D II 100C (HNCS HDR Tonal Realism, 100MP, XCD 2.5/90V, native ISO 50, 15.3 stops DR)
3. Module C: Fujifilm GFX100 II (Portrait Precision, 102MP, GF 110mm F2, ISO 80, 8-stop IBIS, 87mm equiv)
4. Universal Master Override (UNIVERSAL_MEDIUM_FORMAT_PORTRAIT_OVERRIDE)
5. Tri-Signature Comparison Harness (compile_abc_harness)
6. Preset and Alias Routing (module_a, module_b, module_c)
"""

from __future__ import annotations

import unittest
from typing import Any

from optical_compiler import (
    OpticalCompiler,
    SceneInput,
    compile_scene,
    compile_abc_harness,
    load_profile,
    auto_select_profile,
    CAMERA_PRESETS,
    LENS_CATALOG,
    UNIVERSAL_MEDIUM_FORMAT_PORTRAIT_OVERRIDE,
    format_universal_medium_format_override,
)
from optical_compiler.models import TargetEngine


class TestMediumFormatTriSignatures(unittest.TestCase):
    """Unit tests for Medium Format Tri-Signatures and Master Override."""

    def test_module_a_phase_one_hardware_anchors(self) -> None:
        """Verify Module A Phase One IQ4 150MP hardware anchors against manufacturer facts."""
        profile = load_profile("phase_one_iq4")
        self.assertEqual(profile.profile_id, "phase_one_iq4")
        self.assertIn("Phase One XF IQ4 150MP", profile.sensor_and_optics.camera_system)
        self.assertIn("151 MP", profile.sensor_and_optics.sensor_type)
        self.assertIn("53.4", profile.sensor_and_optics.sensor_dimensions)
        self.assertIn("40.0", profile.sensor_and_optics.sensor_dimensions)
        self.assertIn("Schneider Kreuznach 110mm LS f/2.8", profile.sensor_and_optics.lens)
        self.assertIn("ISO 50", profile.sensor_and_optics.iso_base)
        self.assertIn("15 f-stops", profile.sensor_and_optics.dynamic_range)
        self.assertIn("Opticolor+", profile.sensor_and_optics.dynamic_range)

        # Check structured hardware reference and emulation logic
        hw = profile.hardware_reference
        self.assertEqual(hw.get("camera_system"), "Phase One XF + IQ4 150MP")
        sensor = hw.get("sensor", {})
        self.assertEqual(sensor.get("effective_resolution"), "151 MP")
        self.assertEqual(sensor.get("native_pixel_dimensions"), "14204 x 10652")
        self.assertEqual(sensor.get("pixel_pitch"), "3.76 µm")
        self.assertEqual(sensor.get("color_pipeline"), "16-bit Opticolor+")
        self.assertEqual(sensor.get("dynamic_range"), "15 f-stops")
        self.assertEqual(sensor.get("preferred_sensitivity"), "ISO 50")

        # Emulation directives
        self.assertIn("resolving power", profile.purpose.lower())
        self.assertIn("Human skin realism overrides", profile.skin_realism_override.get("priority", ""))
        self.assertIn("pore stamping", profile.skin_realism_override.get("prohibit", []))
        self.assertIn("enormous resolving power existed at capture", profile.signature_goal)

    def test_module_b_hasselblad_hardware_anchors(self) -> None:
        """Verify Module B Hasselblad X2D II 100C hardware anchors against manufacturer facts."""
        profile = load_profile("hasselblad_x2d_ii_100c")
        self.assertEqual(profile.profile_id, "hasselblad_x2d_ii_100c")
        self.assertIn("Hasselblad X2D II 100C", profile.sensor_and_optics.camera_system)
        self.assertIn("100 MP", profile.sensor_and_optics.sensor_type)
        self.assertIn("43.8", profile.sensor_and_optics.sensor_dimensions)
        self.assertIn("32.9", profile.sensor_and_optics.sensor_dimensions)
        self.assertIn("XCD 2.5/90V", profile.sensor_and_optics.lens)
        self.assertIn("71mm", profile.sensor_and_optics.full_frame_equivalent)
        self.assertIn("ISO 50", profile.sensor_and_optics.iso_base)
        self.assertIn("15.3 stops", profile.sensor_and_optics.dynamic_range)
        self.assertIn("1/4000s", profile.sensor_and_optics.shutter)

        # Check structured hardware reference
        hw = profile.hardware_reference
        self.assertEqual(hw.get("camera"), "Hasselblad X2D II 100C")
        sensor = hw.get("sensor", {})
        self.assertEqual(sensor.get("resolution"), "100 MP")
        self.assertEqual(sensor.get("native_pixel_dimensions"), "11656 x 8742")
        self.assertEqual(sensor.get("pixel_pitch"), "3.76 µm")
        self.assertEqual(sensor.get("native_iso"), 50)
        self.assertEqual(sensor.get("dynamic_range"), "15.3 stops")
        lens = hw.get("lens", {})
        self.assertEqual(lens.get("model"), "Hasselblad XCD 2.5/90V")
        self.assertEqual(lens.get("full_frame_equivalent"), "71 mm")

        # HNCS HDR emulation
        self.assertIn("HNCS", profile.sensor_and_optics.dynamic_range)
        hncs = profile.to_dict().get("hncs_hdr_emulation", {})
        self.assertIn("HDR halos", hncs.get("prohibit", []))

    def test_module_c_fujifilm_hardware_anchors(self) -> None:
        """Verify Module C Fujifilm GFX100 II hardware anchors against manufacturer facts."""
        profile = load_profile("fujifilm_gfx100ii")
        self.assertEqual(profile.profile_id, "fujifilm_gfx100ii")
        self.assertIn("Fujifilm GFX", profile.sensor_and_optics.camera_system)
        self.assertIn("102MP", profile.sensor_and_optics.camera_system)
        self.assertIn("CMOS II HS", profile.sensor_and_optics.sensor_type)
        self.assertIn("43.8", profile.sensor_and_optics.sensor_dimensions)
        self.assertIn("32.9", profile.sensor_and_optics.sensor_dimensions)
        self.assertIn("GF110mm", profile.sensor_and_optics.lens)
        self.assertIn("87mm", profile.sensor_and_optics.full_frame_equivalent)
        self.assertIn("ISO 80", profile.sensor_and_optics.iso_base)
        self.assertIn("IBIS", profile.sensor_and_optics.shutter)

        # Check structured hardware reference
        hw = profile.hardware_reference
        self.assertEqual(hw.get("camera"), "Fujifilm GFX100 II")
        sensor = hw.get("sensor", {})
        self.assertEqual(sensor.get("effective_resolution"), "102 MP")
        self.assertEqual(sensor.get("standard_iso_range"), "ISO 80 to 12800")
        self.assertEqual(sensor.get("extended_low_iso"), "ISO 40")
        self.assertIn("8 stops", sensor.get("stabilization", ""))
        lens = hw.get("lens", {})
        self.assertEqual(lens.get("model"), "Fujinon GF110mmF2 R LM WR")
        self.assertEqual(lens.get("full_frame_equivalent"), "87 mm")
        self.assertIn("4 ED elements", lens.get("construction", ""))

    def test_universal_master_override_specification(self) -> None:
        """Verify the UNIVERSAL_MEDIUM_FORMAT_PORTRAIT_OVERRIDE rules and formatting."""
        override = UNIVERSAL_MEDIUM_FORMAT_PORTRAIT_OVERRIDE
        self.assertIn("Photographic realism", override["priority"])
        self.assertIn("resolution_rule", override)
        self.assertIn("skin_rule", override)
        self.assertIn("hair_rule", override)
        self.assertIn("hdr_rule", override)
        self.assertIn("black_rule", override)
        self.assertIn("sharpness_rule", override)
        self.assertIn("depth_rule", override)
        self.assertIn("detail_rule", override)
        self.assertIn("anatomy_rule", override)
        self.assertIn("final_aesthetic", override)

        formatted = format_universal_medium_format_override()
        self.assertIn("UNIVERSAL MEDIUM FORMAT PORTRAIT OVERRIDE:", formatted)
        self.assertIn("[SKIN REALISM RULE]:", formatted)
        self.assertIn("[BLACK POINT RULE]:", formatted)

    def test_universal_master_override_in_compilation(self) -> None:
        """Verify universal_medium_format_override injects master rules into prompts."""
        compiler = OpticalCompiler("phase_one_iq4")
        payload = compiler.compile(
            "Editorial three-quarter portrait of an artisan in wool apron",
            target="gpt_images",
            universal_medium_format_override=True,
        )
        self.assertTrue(payload.parameters.get("universal_medium_format_override"))
        self.assertIn("UNIVERSAL MEDIUM FORMAT PORTRAIT OVERRIDE:", payload.positive_prompt)
        self.assertIn("Photographic realism above synthetic perceived resolution", payload.positive_prompt)
        self.assertIn("Skin realism overrides sharpening", payload.positive_prompt)

    def test_compile_abc_harness_execution(self) -> None:
        """Verify compile_abc_harness produces three distinct photographic signatures on one scene."""
        scene = "Editorial three-quarter portrait of an artisan examining raw materials"
        harness = compile_abc_harness(scene, target="gpt_images", universal_override=True)

        self.assertIn("module_a", harness)
        self.assertIn("module_b", harness)
        self.assertIn("module_c", harness)
        self.assertIn("camera_a", harness)
        self.assertIn("camera_b", harness)
        self.assertIn("camera_c", harness)
        self.assertTrue(harness["universal_override_active"])

        res_a = harness["module_a"]
        res_b = harness["module_b"]
        res_c = harness["module_c"]

        # Module A (Phase One) checks
        self.assertIn("Phase One XF IQ4 150MP", res_a.positive_prompt)
        self.assertIn("Schneider Kreuznach 110mm LS f/2.8", res_a.positive_prompt)
        self.assertIn("ISO 50", res_a.positive_prompt)

        # Module B (Hasselblad) checks
        self.assertIn("Hasselblad X2D II 100C", res_b.positive_prompt)
        self.assertIn("XCD 2.5/90V", res_b.positive_prompt)
        self.assertIn("HNCS", res_b.positive_prompt)

        # Module C (Fujifilm GFX) checks
        self.assertIn("Fujifilm GFX100 II", res_c.positive_prompt)
        self.assertIn("GF110mmF2", res_c.positive_prompt)
        self.assertIn("87mm", res_c.positive_prompt)

        # All 3 contain the universal override
        for res in (res_a, res_b, res_c):
            self.assertIn("UNIVERSAL MEDIUM FORMAT PORTRAIT OVERRIDE:", res.positive_prompt)

    def test_compile_abc_harness_across_engines(self) -> None:
        """Verify compile_abc_harness functions across Flux and Midjourney targets."""
        scene = "Full-length fashion portrait in architectural studio"
        
        # Flux
        harness_flux = compile_abc_harness(scene, target="flux", universal_override=True)
        self.assertEqual(harness_flux["module_a"].target_engine, TargetEngine.FLUX)
        self.assertIn("Phase One XF IQ4 150MP", harness_flux["module_a"].positive_prompt)
        self.assertIn("Universal Master Override:", harness_flux["module_a"].positive_prompt)
        self.assertIn("Hasselblad X2D II 100C", harness_flux["module_b"].positive_prompt)
        self.assertIn("Fujifilm GFX100 II", harness_flux["module_c"].positive_prompt)

        # Midjourney
        harness_mj = compile_abc_harness(scene, target="midjourney", universal_override=False)
        self.assertEqual(harness_mj["module_a"].target_engine, TargetEngine.MIDJOURNEY)
        self.assertIn("Phase One", harness_mj["module_a"].positive_prompt)
        self.assertIn("Hasselblad", harness_mj["module_b"].positive_prompt)
        self.assertIn("Fujifilm GFX", harness_mj["module_c"].positive_prompt)

    def test_aliases_and_routing(self) -> None:
        """Verify module_a, module_b, and module_c profile aliases and auto-router rules."""
        prof_a = load_profile("module_a")
        prof_b = load_profile("module_b")
        prof_c = load_profile("module_c")

        self.assertEqual(prof_a.profile_id, "phase_one_iq4")
        self.assertEqual(prof_b.profile_id, "hasselblad_x2d_ii_100c")
        self.assertEqual(prof_c.profile_id, "fujifilm_gfx100ii")

        # Router rules
        self.assertEqual(auto_select_profile("Phase One 151MP resolving authority"), "phase_one_iq4")
        self.assertEqual(auto_select_profile("Hasselblad X2D II 100C HNCS tonal realism"), "hasselblad_x2d_ii_100c")
        self.assertEqual(auto_select_profile("Fujifilm GFX 100 II portrait precision with GF 110mm"), "fujifilm_gfx100ii")

    def test_dedicated_presets_presence(self) -> None:
        """Verify dedicated presets for Module A, B, and C exist in CAMERA_PRESETS and compile."""
        self.assertIn("cam_module_a_phase_one_110mm", CAMERA_PRESETS)
        self.assertIn("cam_module_b_hasselblad_90v", CAMERA_PRESETS)
        self.assertIn("cam_module_c_fujifilm_110mm", CAMERA_PRESETS)

        for preset_id in ("cam_module_a_phase_one_110mm", "cam_module_b_hasselblad_90v", "cam_module_c_fujifilm_110mm"):
            cfg = CAMERA_PRESETS[preset_id]
            scene = SceneInput(
                subject=cfg["subject"],
                framing=cfg.get("framing"),
                environment=cfg.get("environment"),
                wardrobe=cfg.get("wardrobe"),
                mood=cfg.get("mood"),
                aperture=cfg.get("aperture"),
                lens=cfg.get("lens"),
                aspect_ratio=cfg.get("aspectRatio", "4:5"),
                universal_medium_format_override=cfg.get("universalMediumFormatOverride", False),
            )
            payload = compile_scene(scene, profile=cfg["profile"], target="gpt_images")
            self.assertIsNotNone(payload.positive_prompt)
            self.assertIn("UNIVERSAL MEDIUM FORMAT PORTRAIT OVERRIDE:", payload.positive_prompt)


if __name__ == "__main__":
    unittest.main()
