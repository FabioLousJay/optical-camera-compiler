"""Unit tests for the Industry-Pioneering Tri-Suite:
1. Biomechanical Hand & Finger Precision Gate (The 5-Point Grip Lock)
2. Cinema Anamorphic Optics & Flare Engine
3. Commercial Advertising Suite (Gobo Light Shapers + Ad-Safe Copy-Space & Safe-Zone Framing)
"""

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from optical_compiler.cli import main
from optical_compiler.comfy_nodes import OpticalCameraCompilerNode
from optical_compiler.compiler import OpticalCompiler
from optical_compiler.models import (
    AdSafeZone,
    AnamorphicSqueeze,
    CopySpace,
    GoboPattern,
    GripModifier,
    GripType,
    IrisBladeCount,
    LightingRatio,
    NegativeShield,
    SceneInput,
    StreakFlare,
    TargetEngine,
)
from optical_compiler.profiles import auto_select_profile


class TestTriPioneerSuite(unittest.TestCase):
    """Test suite validating all three pioneering tool additions."""

    def setUp(self) -> None:
        self.compiler = OpticalCompiler(profile="auto")

    # =========================================================================
    # ENUM & MODEL PARSING TESTS
    # =========================================================================

    def test_grip_type_parsing(self) -> None:
        """Verify GripType parsing and alias tolerance."""
        self.assertEqual(GripType.PRECISION_PINCH.value, "precision_pinch")
        for alias in ["precision_pinch", "PRECISION_PINCH", "pinch", "pinch_grip", "fingertip"]:
            self.assertEqual(GripType.from_string(alias), GripType.PRECISION_PINCH)
        for alias in ["cylindrical_wrap", "cylindrical", "wrap", "power_grip"]:
            self.assertEqual(GripType.from_string(alias), GripType.CYLINDRICAL_WRAP)
        for alias in ["palm_support", "palm", "flat_palm"]:
            self.assertEqual(GripType.from_string(alias), GripType.PALM_SUPPORT)
        for alias in ["relaxed_rest", "relaxed", "rest", "loose"]:
            self.assertEqual(GripType.from_string(alias), GripType.RELAXED_REST)
        for alias in ["open_palm", "open", "splay"]:
            self.assertEqual(GripType.from_string(alias), GripType.OPEN_PALM)

    def test_anamorphic_squeeze_parsing(self) -> None:
        """Verify AnamorphicSqueeze parsing and alias tolerance."""
        self.assertEqual(AnamorphicSqueeze.SQUEEZE_2_0X.value, "2.0x")
        for alias in ["2.0x", "2x", "2.0", "scope", "anamorphic_2x"]:
            self.assertEqual(AnamorphicSqueeze.from_string(alias), AnamorphicSqueeze.SQUEEZE_2_0X)
        for alias in ["1.33x", "1.33"]:
            self.assertEqual(AnamorphicSqueeze.from_string(alias), AnamorphicSqueeze.SQUEEZE_1_33X)
        for alias in ["1.5x", "1.5"]:
            self.assertEqual(AnamorphicSqueeze.from_string(alias), AnamorphicSqueeze.SQUEEZE_1_5X)
        for alias in ["1.8x", "1.8"]:
            self.assertEqual(AnamorphicSqueeze.from_string(alias), AnamorphicSqueeze.SQUEEZE_1_8X)

    def test_streak_flare_parsing(self) -> None:
        """Verify StreakFlare color profile parsing."""
        self.assertEqual(StreakFlare.CYAN_BLUE.value, "cyan_blue")
        for alias in ["cyan_blue", "blue", "cyan"]:
            self.assertEqual(StreakFlare.from_string(alias), StreakFlare.CYAN_BLUE)
        for alias in ["warm_gold", "gold", "amber", "vintage_gold"]:
            self.assertEqual(StreakFlare.from_string(alias), StreakFlare.WARM_GOLD)
        for alias in ["neutral_silver", "silver", "neutral", "white"]:
            self.assertEqual(StreakFlare.from_string(alias), StreakFlare.NEUTRAL_SILVER)
        for alias in ["vintage_magenta", "magenta", "purple"]:
            self.assertEqual(StreakFlare.from_string(alias), StreakFlare.VINTAGE_MAGENTA)

    def test_iris_blade_parsing(self) -> None:
        """Verify IrisBladeCount parsing."""
        self.assertEqual(IrisBladeCount.BLADES_14_CIRCULAR.value, "14_blade_circular")
        for alias in ["14_blade_circular", "14", "14_blade", "circular"]:
            self.assertEqual(IrisBladeCount.from_string(alias), IrisBladeCount.BLADES_14_CIRCULAR)
        for alias in ["9_blade_rounded", "9", "9_blade"]:
            self.assertEqual(IrisBladeCount.from_string(alias), IrisBladeCount.BLADES_9_ROUNDED)
        for alias in ["8_blade_octagonal", "8", "8_blade", "octagonal"]:
            self.assertEqual(IrisBladeCount.from_string(alias), IrisBladeCount.BLADES_8_OCTAGONAL)
        for alias in ["6_blade_hexagonal", "6", "6_blade", "hexagonal"]:
            self.assertEqual(IrisBladeCount.from_string(alias), IrisBladeCount.BLADES_6_HEXAGONAL)

    def test_advertising_suite_enums_parsing(self) -> None:
        """Verify Gobo, GripModifier, LightingRatio, CopySpace, and AdSafeZone parsing."""
        self.assertEqual(GoboPattern.from_string("venetian_blinds"), GoboPattern.VENETIAN_BLINDS)
        self.assertEqual(GoboPattern.from_string("dappled_foliage"), GoboPattern.DAPPLED_FOLIAGE)
        self.assertEqual(GripModifier.from_string("beauty_dish_honeycomb"), GripModifier.BEAUTY_DISH_HONEYCOMB)
        self.assertEqual(GripModifier.from_string("butterfly_8x8_silk"), GripModifier.BUTTERFLY_8X8_SILK)
        self.assertEqual(LightingRatio.from_string("4:1"), LightingRatio.RATIO_4_1)
        self.assertEqual(LightingRatio.from_string("8:1"), LightingRatio.RATIO_8_1)
        self.assertEqual(CopySpace.from_string("left_third"), CopySpace.LEFT_THIRD)
        self.assertEqual(CopySpace.from_string("top_third"), CopySpace.TOP_THIRD)
        self.assertEqual(AdSafeZone.from_string("tiktok_reels_9_16"), AdSafeZone.TIKTOK_REELS_9_16)
        self.assertEqual(AdSafeZone.from_string("instagram_feed_4_5"), AdSafeZone.INSTAGRAM_FEED_4_5)

    def test_negative_shield_hand_drift_tokens(self) -> None:
        """Verify NegativeShield includes at least 25 specialized anti-hand-mutation tokens."""
        shield = NegativeShield()
        hand_tokens = shield.hand_drift
        self.assertGreaterEqual(len(hand_tokens), 25)
        self.assertIn("extra fingers", hand_tokens)
        self.assertIn("missing fingers", hand_tokens)
        self.assertIn("fused fingers", hand_tokens)
        self.assertIn("polydactyly", hand_tokens)
        self.assertIn("ectrodactyly", hand_tokens)
        self.assertIn("webbed digits", hand_tokens)
        self.assertIn("floating knuckles", hand_tokens)

        all_tokens = shield.all_tokens(include_hand_drift=True)
        self.assertIn("extra fingers", all_tokens)
        self.assertIn("polydactyly", all_tokens)

    # =========================================================================
    # TOOL 1: BIOMECHANICAL HAND & FINGER PRECISION GATE TESTS
    # =========================================================================

    def test_hand_lock_scene_property(self) -> None:
        """Verify SceneInput.has_hand_lock property triggers appropriately."""
        s1 = SceneInput(subject="Person standing")
        self.assertFalse(s1.has_hand_lock)

        s2 = SceneInput(subject="Person standing", hand_lock=True)
        self.assertTrue(s2.has_hand_lock)

        s3 = SceneInput(subject="Person holding pen", grip_type=GripType.PRECISION_PINCH)
        self.assertTrue(s3.has_hand_lock)

    def test_hand_lock_gpt_images(self) -> None:
        """Verify GPT Images adapter generates all 5 forensic hand precision gates."""
        scene = SceneInput(
            subject="Master watchmaker holding tourbillon balance wheel",
            hand_lock=True,
            grip_type=GripType.PRECISION_PINCH,
            hand_details="visible lunula, clean cuticles, contact tissue blanching on tweezers",
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.GPT_IMAGES)
        prompt = res.positive_prompt

        self.assertIn("GATE H1: 5-RAY METACARPAL ARCHITECTURE", prompt)
        self.assertIn("2:3:4:3.5:2.5", prompt)
        self.assertIn("GATE H2: GRIP PHYSICS & CONTACT BLANCHING", prompt)
        self.assertIn("GATE H3: FLEXION CREASES & THENAR ANATOMY", prompt)
        self.assertIn("GATE H4: NAIL BED & CUTICLE REALISM", prompt)
        self.assertIn("GATE H5: ZERO FINGER MUTATION SHIELD", prompt)
        self.assertIn("precision pinch", prompt)

    def test_hand_lock_imagen(self) -> None:
        """Verify Imagen 3 adapter incorporates photographic hand biomechanics prose."""
        scene = SceneInput(
            subject="Botanist holding a delicate orchid petal",
            hand_lock=True,
            grip_type=GripType.PRECISION_PINCH,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.IMAGEN)
        prompt = res.positive_prompt

        self.assertIn("Hand Precision Gate", prompt)
        self.assertIn("metacarpal", prompt)
        self.assertIn("blanching", prompt)
        self.assertIn("palmar flexion creases", prompt)

    def test_hand_lock_midjourney(self) -> None:
        """Verify Midjourney adapter includes hand precision tokens and negative exclusions."""
        scene = SceneInput(
            subject="Craftsman gripping oak chisel",
            hand_lock=True,
            grip_type=GripType.CYLINDRICAL_WRAP,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.MIDJOURNEY)
        prompt = res.positive_prompt

        self.assertIn("5-ray metacarpal architecture", prompt)
        self.assertIn("cylindrical wrap", prompt)
        self.assertIn("contact tissue blanching", prompt)
        self.assertIn("--no", prompt)
        self.assertIn("fused digits", prompt)
        self.assertIn("six fingers", prompt)

    def test_hand_lock_flux(self) -> None:
        """Verify Flux.1 adapter includes narrative hand biomechanics directives."""
        scene = SceneInput(
            subject="Ceramist resting hand on clay pot",
            hand_lock=True,
            grip_type=GripType.PALM_SUPPORT,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.FLUX)
        prompt = res.positive_prompt

        self.assertIn("Biomechanical 5-Point Hand Precision Gate", prompt)
        self.assertIn("2:3:4:3.5:2.5 ratio", prompt)
        self.assertIn("palm support", prompt)
        self.assertIn("zero finger mutations", prompt)

    def test_hand_lock_sdxl(self) -> None:
        """Verify SDXL dual-channel positive and negative hand tokens."""
        scene = SceneInput(
            subject="Musician holding cello bow",
            hand_lock=True,
            grip_type=GripType.PRECISION_PINCH,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.SDXL)
        self.assertIn("5-ray metacarpal architecture", res.positive_prompt)
        self.assertIn("contact blanching", res.positive_prompt)
        self.assertIn("fused digits", res.negative_prompt)
        self.assertIn("six fingers", res.negative_prompt)

    def test_hand_lock_raw_spec(self) -> None:
        """Verify Raw Spec adapter outputs dedicated Biomechanical Hand & Finger Precision Gate section."""
        scene = SceneInput(
            subject="Doctor examining surgical instrument",
            hand_lock=True,
            grip_type=GripType.PRECISION_PINCH,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.RAW)
        self.assertIn("--- Biomechanical Hand & Finger Precision Gate ---", res.positive_prompt)
        self.assertIn("Gate H1 (Metacarpal Proportions): 5-ray architecture", res.positive_prompt)
        self.assertIn("Gate H2 (Grip Physics): Contact tissue blanching under pressure", res.positive_prompt)

    # =========================================================================
    # TOOL 2: CINEMA ANAMORPHIC OPTICS & FLARE ENGINE TESTS
    # =========================================================================

    def test_anamorphic_auto_camera_router(self) -> None:
        """Verify that activating anamorphic optics dynamically routes to ARRI Alexa 35."""
        scene = SceneInput(
            subject="Cinematic night runner",
            anamorphic_squeeze=AnamorphicSqueeze.SQUEEZE_2_0X,
        )
        profile_id = auto_select_profile(scene)
        self.assertEqual(profile_id, "arri_alexa_35")

    def test_anamorphic_gpt_images(self) -> None:
        """Verify GPT Images adapter simulates anamorphic cylindrical elements, oval bokeh, and streak flares."""
        scene = SceneInput(
            subject="Cyberpunk detective in rain-soaked neon street",
            anamorphic_squeeze=AnamorphicSqueeze.SQUEEZE_2_0X,
            streak_flare=StreakFlare.CYAN_BLUE,
            iris_blades=IrisBladeCount.BLADES_14_CIRCULAR,
            aspect_ratio="2.39:1",
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.GPT_IMAGES)
        prompt = res.positive_prompt

        self.assertIn("Cooke Anamorphic /i", prompt)
        self.assertIn("2.0x cylindrical front element", prompt)
        self.assertIn("2:1 elliptical oval bokeh", prompt)
        self.assertIn("cyan blue horizontal streak flare", prompt)
        self.assertIn("14 blade circular iris", prompt)

    def test_anamorphic_midjourney(self) -> None:
        """Verify Midjourney adapter forces --ar 2.39:1 and injects anamorphic lens tokens."""
        scene = SceneInput(
            subject="Astronaut gazing at planetary horizon",
            anamorphic_squeeze=AnamorphicSqueeze.SQUEEZE_2_0X,
            streak_flare=StreakFlare.WARM_GOLD,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.MIDJOURNEY)
        prompt = res.positive_prompt

        self.assertIn("--ar 2.39:1", prompt)
        self.assertIn("2.0x squeeze", prompt)
        self.assertIn("vertical elliptical oval bokeh", prompt)
        self.assertIn("warm gold horizontal streak flare", prompt)

    def test_anamorphic_flux(self) -> None:
        """Verify Flux.1 adapter describes anamorphic rig and optical characteristics."""
        scene = SceneInput(
            subject="Indie film protagonist in vintage diner booth",
            anamorphic_squeeze=AnamorphicSqueeze.SQUEEZE_1_8X,
            streak_flare=StreakFlare.NEUTRAL_SILVER,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.FLUX)
        prompt = res.positive_prompt

        self.assertIn("1.8x squeeze factor", prompt)
        self.assertIn("2:1 vertical elliptical oval bokeh", prompt)
        self.assertIn("horizontal neutral silver streak flares", prompt)

    def test_anamorphic_raw_spec(self) -> None:
        """Verify Raw Spec adapter outputs dedicated Cinema Anamorphic Optics & Flare Engine section."""
        scene = SceneInput(
            subject="Racer preparing in pit lane at dusk",
            anamorphic_squeeze=AnamorphicSqueeze.SQUEEZE_2_0X,
            streak_flare=StreakFlare.CYAN_BLUE,
            iris_blades=IrisBladeCount.BLADES_9_ROUNDED,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.RAW)
        prompt = res.positive_prompt

        self.assertIn("--- Cinema Anamorphic Optics & Flare Engine ---", prompt)
        self.assertIn("Squeeze Factor: 2.0x", prompt)
        self.assertIn("Bokeh Geometry: 2:1 vertical elliptical oval bokeh discs", prompt)
        self.assertIn("Streak Flare Coating: cyan_blue", prompt)
        self.assertIn("Iris Blades: 9_blade_rounded", prompt)

    # =========================================================================
    # TOOL 3: COMMERCIAL ADVERTISING SUITE TESTS
    # =========================================================================

    def test_commercial_advertising_gpt_images(self) -> None:
        """Verify GPT Images adapter incorporates gobo cookies, studio grip, lighting ratios, and copy-space."""
        scene = SceneInput(
            subject="Luxury perfume bottle on travertine block",
            gobo=GoboPattern.VENETIAN_BLINDS,
            grip_modifier=GripModifier.BEAUTY_DISH_HONEYCOMB,
            lighting_ratio=LightingRatio.RATIO_4_1,
            copy_space=CopySpace.LEFT_THIRD,
            ad_safe_zone=AdSafeZone.INSTAGRAM_FEED_4_5,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.GPT_IMAGES)
        prompt = res.positive_prompt

        self.assertIn("Commercial Copy-Space", prompt)
        self.assertIn("left third", prompt)
        self.assertIn("Advertising Safe-Zone", prompt)
        self.assertIn("venetian blinds", prompt)
        self.assertIn("beauty dish honeycomb", prompt)
        self.assertIn("4:1", prompt)

    def test_commercial_advertising_imagen(self) -> None:
        """Verify Imagen 3 adapter incorporates advertising lighting and composition prose."""
        scene = SceneInput(
            subject="Artisanal ceramic vase bathed in light",
            gobo=GoboPattern.DAPPLED_FOLIAGE,
            lighting_ratio=LightingRatio.RATIO_2_1,
            copy_space=CopySpace.RIGHT_THIRD,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.IMAGEN)
        prompt = res.positive_prompt

        self.assertIn("dappled foliage", prompt)
        self.assertIn("2:1 lighting ratio", prompt)
        self.assertIn("right third", prompt)

    def test_commercial_advertising_midjourney(self) -> None:
        """Verify Midjourney adapter includes copy space and gobo tokens."""
        scene = SceneInput(
            subject="Designer sunglasses on marble slab",
            gobo=GoboPattern.WINDOW_PANES,
            copy_space=CopySpace.TOP_THIRD,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.MIDJOURNEY)
        prompt = res.positive_prompt

        self.assertIn("commercial negative copy space in top third", prompt)
        self.assertIn("window panes", prompt)

    def test_commercial_advertising_raw_spec(self) -> None:
        """Verify Raw Spec adapter outputs dedicated Commercial Advertising Framing & Copy-Space section."""
        scene = SceneInput(
            subject="Swiss chronometer watch on slate pedestal",
            gobo=GoboPattern.GEOMETRIC_SLITS,
            grip_modifier=GripModifier.BUTTERFLY_8X8_SILK,
            lighting_ratio=LightingRatio.RATIO_8_1,
            copy_space=CopySpace.LEFT_THIRD,
            ad_safe_zone=AdSafeZone.TIKTOK_REELS_9_16,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.RAW)
        prompt = res.positive_prompt

        self.assertIn("--- Commercial Advertising Framing & Copy-Space ---", prompt)
        self.assertIn("Negative Copy-Space: left_third", prompt)
        self.assertIn("Advertising Safe-Zone: tiktok_reels_9_16", prompt)
        self.assertIn("Gobo Projection Cookie: geometric_slits", prompt)
        self.assertIn("Lighting Contrast Ratio: 8:1", prompt)

    # =========================================================================
    # JSON SCHEMA 3.3 VALIDATION TESTS
    # =========================================================================

    def test_json_schema_version_3_3_when_pioneers_active(self) -> None:
        """Verify JSON prompt adapter outputs schema_version 3.3 when any of the 3 pioneer tools are active."""
        scene = SceneInput(
            subject="Hand holding smartphone displaying fintech app",
            hand_lock=True,
            grip_type=GripType.PRECISION_PINCH,
            anamorphic_squeeze=AnamorphicSqueeze.SQUEEZE_2_0X,
            streak_flare=StreakFlare.CYAN_BLUE,
            gobo=GoboPattern.VENETIAN_BLINDS,
            copy_space=CopySpace.LEFT_THIRD,
        )
        res = self.compiler.compile(scene=scene, target=TargetEngine.JSON)
        data = json.loads(res.positive_prompt)

        self.assertEqual(data["schema_version"], "3.3")
        self.assertIn("hand_biomechanics", data)
        self.assertEqual(data["hand_biomechanics"]["grip_type"], "precision_pinch")
        self.assertEqual(data["hand_biomechanics"]["metacarpal_ratio"], "2:3:4:3.5:2.5")
        self.assertTrue(data["hand_biomechanics"]["contact_tissue_blanching"])

        self.assertIn("anamorphic_optics", data)
        self.assertEqual(data["anamorphic_optics"]["squeeze_factor"], "2.0x")
        self.assertEqual(data["anamorphic_optics"]["streak_flare"], "cyan_blue")

        self.assertIn("lighting_grip", data)
        self.assertEqual(data["lighting_grip"]["gobo_cookie_pattern"], "venetian_blinds")

        self.assertIn("advertising_framing", data)
        self.assertEqual(data["advertising_framing"]["copy_space"], "left_third")

    # =========================================================================
    # CLI INTEGRATION TESTS
    # =========================================================================

    def test_cli_combined_pioneer_flags(self) -> None:
        """Verify CLI execution with combined hand lock, anamorphic, and advertising suite flags."""
        stdout_buf = io.StringIO()
        with redirect_stdout(stdout_buf):
            exit_code = main([
                "Commercial hero packshot of luxury chronograph",
                "-t", "flux",
                "-p", "auto",
                "--hand-lock",
                "--grip-type", "precision_pinch",
                "--anamorphic",
                "--squeeze", "2.0x",
                "--streak-flare", "cyan_blue",
                "--gobo", "venetian_blinds",
                "--copy-space", "left_third",
            ])

        self.assertEqual(exit_code, 0)
        output = stdout_buf.getvalue()
        self.assertIn("Biomechanical 5-Point Hand Precision Gate", output)
        self.assertIn("precision pinch", output)
        self.assertIn("2.0x", output)
        self.assertIn("cyan blue", output)
        self.assertIn("left third", output)

    # =========================================================================
    # COMFYUI NODE INTEGRATION TESTS
    # =========================================================================

    def test_comfy_node_pioneer_suites(self) -> None:
        """Verify ComfyUI node compiles seamlessly with all 3 pioneer suites active."""
        node = OpticalCameraCompilerNode()
        pos, neg, unified = node.compile_optical_prompt(
            camera_rig="Auto (Intelligent Camera Router)",
            model_target="gpt_images",
            subject="A hands-on demonstration of a mechanical iris diaphragm",
            hand_lock="enabled",
            grip_type="precision_pinch",
            anamorphic="enabled",
            anamorphic_squeeze="2.0x",
            streak_flare="cyan_blue",
            iris_blades="14_blade_circular",
            gobo="venetian_blinds",
            grip_modifier="beauty_dish_honeycomb",
            lighting_ratio="4:1",
            copy_space="left_third",
            ad_safe_zone="instagram_feed_4_5",
        )

        self.assertIn("GATE H1: 5-RAY METACARPAL ARCHITECTURE", pos)
        self.assertIn("2.0x", pos)
        self.assertIn("cyan blue", pos)
        self.assertIn("Commercial Copy-Space", pos)
        self.assertIn("left third", pos)


if __name__ == "__main__":
    unittest.main()
