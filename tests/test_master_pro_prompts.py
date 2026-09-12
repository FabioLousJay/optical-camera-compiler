"""Unit tests for the Universal High-End Pro Master Prompt features.

Covers:
- All 19 calibrated hardware camera profiles
- Intelligent Auto Camera Router (auto_select_profile)
- Modular capture logic (CaptureMode)
- Photographic lighting presets (LightingPreset)
- Master negative constraint tokens and anti-drift shields
- ComfyUI node integration
"""

from __future__ import annotations

import unittest

from optical_compiler.compiler import OpticalCompiler, compile_scene
from optical_compiler.comfy_nodes import OpticalCameraCompilerNode, RIG_NAMES, RIG_NAME_TO_ID
from optical_compiler.models import (
    CaptureMode,
    LightingPreset,
    SceneInput,
    TargetEngine,
)
from optical_compiler.profiles import (
    auto_select_profile,
    list_available_profiles,
    load_profile,
)


class TestUniversalMasterFramework(unittest.TestCase):
    """Test suite covering the 19 profiles, auto routing, capture modes, and lighting presets."""

    def test_all_19_camera_profiles_present(self) -> None:
        """Verify that all 19 calibrated camera profiles are discoverable and loadable."""
        profiles = list_available_profiles()
        profile_ids = [p["id"] for p in profiles]
        self.assertGreaterEqual(len(profile_ids), 19)

        expected_profiles = [
            "phase_one_iq4",
            "sony_a1_ii",
            "canon_eos_r5_ii",
            "nikon_z9",
            "sony_fx_series",
            "hasselblad_x2d_ii_100c",
            "fujifilm_gfx100rf",
            "canon_eos_r1",
            "leica_sl3_p",
            "panasonic_lumix_s1rii",
            "hasselblad_h6d",
            "leica_m11",
            "fujifilm_gfx100ii",
            "sony_a7rv",
            "arri_alexa_35",
            "pentax_67ii",
            "hasselblad_500cm",
            "leica_m6_analog",
            "linhof_technika_4x5",
        ]

        for p_id in expected_profiles:
            self.assertIn(p_id, profile_ids, f"Missing profile: {p_id}")
            prof = load_profile(p_id)
            self.assertIsNotNone(prof.title)
            self.assertIsNotNone(prof.sensor_and_optics.camera_system)
            self.assertIsNotNone(prof.sensor_and_optics.lens)

    def test_auto_camera_router_domain_rules(self) -> None:
        """Verify the intelligent camera router picks the optimal camera per domain intent."""
        # 1. Wildlife / Birds -> Sony a1 II
        self.assertEqual(
            auto_select_profile("Telephoto action shot of a peregrine falcon in mid-dive, feather detail"),
            "sony_a1_ii",
        )

        # 2. Sports / Fast Action -> Canon EOS R1
        self.assertEqual(
            auto_select_profile("Olympic sprinter exploding out of the starting blocks at decisive moment"),
            "canon_eos_r1",
        )

        # 3. Macro / Micro-detail -> Panasonic Lumix S1RII
        self.assertEqual(
            auto_select_profile("Extreme macro specimen study of a metallic beetle exoskeleton, micro texture"),
            "panasonic_lumix_s1rii",
        )

        # 4. Cinema / Venice -> Sony FX Cinema Line
        self.assertEqual(
            auto_select_profile("Cinematic film still of a detective in a rain-soaked alleyway, 180-degree shutter"),
            "sony_fx_series",
        )

        # 5. Architecture / Large Format -> Linhof Technika 4x5
        self.assertEqual(
            auto_select_profile("Architectural facade of a brutalist concrete pavilion, perspective control tilt-shift"),
            "linhof_technika_4x5",
        )

        # 6. Luxury / Fine Art / Horology -> Phase One IQ4
        self.assertEqual(
            auto_select_profile("Fine art horology campaign of an open-worked tourbillon timepiece in museum lighting"),
            "phase_one_iq4",
        )

        # 7. Portrait / Beauty -> Hasselblad X2D II 100C
        self.assertEqual(
            auto_select_profile("Beauty headshot of a model with natural skin pores, eyelashes, soft cosmetics"),
            "hasselblad_x2d_ii_100c",
        )

        # 8. Travel / Street -> FUJIFILM GFX100RF
        self.assertEqual(
            auto_select_profile("Street documentary candid of an elderly artisan in Kyoto, classic chrome"),
            "fujifilm_gfx100rf",
        )

        # 9. Reportage -> Leica SL3-P
        self.assertEqual(
            auto_select_profile("Photojournalism prestige documentary assignment covering a press conference"),
            "leica_sl3_p",
        )

        # 10. Vintage 35mm analog -> Leica M6
        self.assertEqual(
            auto_select_profile("Nostalgic 35mm film candid portrait with grainy film aesthetic and silver halide tones"),
            "leica_m6_analog",
        )

    def test_compiler_with_auto_profile(self) -> None:
        """Verify OpticalCompiler(profile='auto') dynamically routes each scene."""
        compiler = OpticalCompiler(profile="auto")

        # Compile a macro scene
        payload_macro = compiler.compile(
            "Extreme macro of iridescent dragonfly wings",
            target="gpt_images",
        )
        self.assertIn("Panasonic LUMIX S1RII", payload_macro.positive_prompt)

        # Compile a cinema scene
        payload_cine = compiler.compile(
            "Cinematic film still of a spacecraft cockpit",
            target="gpt_images",
        )
        self.assertIn("Sony FX Cinema Line", payload_cine.positive_prompt)

        # Compile a sports scene
        payload_sports = compiler.compile(
            "Athletic sprinter running in stadium at decisive moment",
            target="gpt_images",
        )
        self.assertIn("Canon EOS R1", payload_sports.positive_prompt)

    def test_lighting_presets_application(self) -> None:
        """Verify lighting presets override and augment lighting parameters correctly."""
        c = OpticalCompiler(profile="hasselblad_x2d_ii_100c")

        # Golden Hour
        res_golden = c.compile(
            "Portrait of a ceramicist",
            target="midjourney",
            lighting_preset="golden_hour",
        )
        self.assertIn("golden sunlight", res_golden.positive_prompt)

        # Blue Hour
        res_blue = c.compile(
            "Portrait of a cyclist",
            target="gpt_images",
            lighting_preset="blue_hour",
        )
        self.assertIn("twilight ambient sky illumination", res_blue.positive_prompt)

        # Neon
        res_neon = c.compile(
            "Portrait in cyberpunk arcade",
            target="flux",
            lighting_preset="neon",
        )
        self.assertIn("Multi-chromatic saturated ambient rim", res_neon.positive_prompt)

    def test_capture_mode_application(self) -> None:
        """Verify capture modes inject rigorous physical stability directives."""
        c = OpticalCompiler(profile="sony_a1_ii")

        # Macro Max Detail
        payload_macro = c.compile(
            "Ant head detail",
            target="gpt_images",
            capture_mode="macro_max_detail",
        )
        self.assertIn("1:1 reproduction ratio", payload_macro.positive_prompt)
        self.assertIn("diffraction-suppressed optical plane", payload_macro.positive_prompt)

        # Action Max Detail
        payload_action = c.compile(
            "Cheetah sprinting across savannah",
            target="gpt_images",
            capture_mode="action_max_detail",
        )
        self.assertIn("Decisive-moment freeze", payload_action.positive_prompt)
        self.assertIn("zero motion smear", payload_action.positive_prompt)

    def test_new_negative_constraint_tokens_shield(self) -> None:
        """Verify the extended master negative constraint tokens are present in negative prompts."""
        c = OpticalCompiler(profile="canon_eos_r1")
        payload = c.compile(
            "Basketball player dunking",
            target="sdxl",
            suppress_text_branding=True,
        )

        neg = payload.negative_prompt
        # Render defects
        self.assertIn("crunchy HDR", neg)
        self.assertIn("double edges", neg)
        self.assertIn("focus miss", neg)
        self.assertIn("perspective drift", neg)
        self.assertIn("tilted horizon", neg)

        # Skin & lighting drift
        self.assertIn("artificial pore carving", neg)
        self.assertIn("invented eyelashes", neg)
        self.assertIn("unmotivated teal-orange grading", neg)

        # Branding & text drift
        self.assertIn("invented text", neg)
        self.assertIn("garbled typography", neg)
        self.assertIn("product-design drift", neg)
        self.assertIn("logo drift", neg)

    def test_comfy_node_auto_and_presets(self) -> None:
        """Verify ComfyUI node compiles seamlessly with Auto router and presets."""
        node = OpticalCameraCompilerNode()
        pos, neg, unified = node.compile_optical_prompt(
            camera_rig="Auto (Intelligent Camera Router)",
            model_target="gpt_images",
            subject="Macro photograph of morning dew drops on spiderweb silk",
            lighting_preset="golden_hour",
            capture_mode="macro_max_detail",
        )

        self.assertIn("Panasonic LUMIX S1RII", pos)
        self.assertIn("golden sunlight", pos)
        self.assertIn("1:1 reproduction ratio", pos)
        self.assertIn("crunchy HDR", unified)


if __name__ == "__main__":
    unittest.main()
