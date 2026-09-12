"""Unit tests for the GenAI Photography Mastery Suite (v3.4):
1. Body Morphology & Proportional Volume Calibration Engine
2. 4D Volumetric & Premium Material Engine
3. Policy-Safe Compliance Recovery Layer (--policy-safe)
4. Print-Calibrated Prepress & Exhibition Lab Matrix
5. Master Resolution Engine & JSON Schema 3.4
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
    BackgroundStyle,
    BodyMorphologyConfig,
    BodyVolumeRegion,
    MaterialStyle,
    NegativeShield,
    PaperProfile,
    PrintSpec,
    RenderingIntent,
    SceneInput,
    TargetEngine,
    VolumeDegree,
)
from optical_compiler.restoration import (
    PAPER_CHARACTERISTICS,
    STANDARD_PRINT_SIZES,
    inches_to_pixels,
)


class TestGenAIMasterySuite(unittest.TestCase):
    """Test suite validating all five v3.4 mastery modules."""

    def setUp(self) -> None:
        self.compiler = OpticalCompiler(profile="auto")

    # =========================================================================
    # ENUM & MODEL PARSING TESTS
    # =========================================================================

    def test_body_volume_region_parsing(self) -> None:
        """Verify BodyVolumeRegion parsing and alias tolerance."""
        self.assertEqual(BodyVolumeRegion.BICEPS.value, "biceps")
        for alias in ["biceps", "bicep", "BICEP", "arms"]:
            self.assertEqual(BodyVolumeRegion.from_string(alias), BodyVolumeRegion.BICEPS)
        for alias in ["chest", "pecs", "torso"]:
            self.assertEqual(BodyVolumeRegion.from_string(alias), BodyVolumeRegion.CHEST)
        for alias in ["gut", "belly", "stomach", "abdomen"]:
            self.assertEqual(BodyVolumeRegion.from_string(alias), BodyVolumeRegion.GUT)
        for alias in ["legs", "thighs", "quads"]:
            self.assertEqual(BodyVolumeRegion.from_string(alias), BodyVolumeRegion.LEGS)
        for alias in ["waist", "midsection", "love_handles"]:
            self.assertEqual(BodyVolumeRegion.from_string(alias), BodyVolumeRegion.WAIST)

    def test_volume_degree_parsing(self) -> None:
        """Verify VolumeDegree parsing and alias tolerance."""
        self.assertEqual(VolumeDegree.SUBTLE.value, "subtle")
        for alias in ["subtle", "slight", "minor"]:
            self.assertEqual(VolumeDegree.from_string(alias), VolumeDegree.SUBTLE)
        for alias in ["moderate", "medium", "natural", "athletic", "muscular", "cut"]:
            self.assertEqual(VolumeDegree.from_string(alias), VolumeDegree.NOTICEABLE_RESTRAINED)
        for alias in ["significant", "heavy", "bulky", "large", "heavyweight", "bodybuilder", "powerlifter"]:
            self.assertEqual(VolumeDegree.from_string(alias), VolumeDegree.HEAVY_WEIGHT)

    def test_material_style_parsing(self) -> None:
        """Verify MaterialStyle parsing and alias tolerance."""
        self.assertEqual(MaterialStyle.LATEX_GLOSS.value, "latex_gloss")
        for alias in ["latex", "latex_gloss", "shiny_latex", "black_latex"]:
            self.assertEqual(MaterialStyle.from_string(alias), MaterialStyle.LATEX_GLOSS)
        for alias in ["liquid_glass", "glass", "blown_glass"]:
            self.assertEqual(MaterialStyle.from_string(alias), MaterialStyle.LIQUID_GLASS)
        for alias in ["dielectric_acrylic", "acrylic", "lucite", "perspex"]:
            self.assertEqual(MaterialStyle.from_string(alias), MaterialStyle.DIELECTRIC_ACRYLIC)
        for alias in ["polished_vinyl", "vinyl", "pvc"]:
            self.assertEqual(MaterialStyle.from_string(alias), MaterialStyle.POLISHED_VINYL)
        for alias in ["anodized_aluminum", "aluminum", "metallic"]:
            self.assertEqual(MaterialStyle.from_string(alias), MaterialStyle.ANODIZED_ALUMINUM)

    def test_background_style_parsing(self) -> None:
        """Verify BackgroundStyle parsing and alias tolerance."""
        self.assertEqual(BackgroundStyle.PURE_BLACK_BLUR.value, "pure_black_blur")
        for alias in ["pure_black_blur", "black_blur", "soft_black", "black_background"]:
            self.assertEqual(BackgroundStyle.from_string(alias), BackgroundStyle.PURE_BLACK_BLUR)
        for alias in ["minimalist_studio_grey", "studio_grey", "grey_cyclorama"]:
            self.assertEqual(BackgroundStyle.from_string(alias), BackgroundStyle.MINIMALIST_STUDIO_GREY)
        for alias in ["clean_high_key_white", "high_key", "pure_white"]:
            self.assertEqual(BackgroundStyle.from_string(alias), BackgroundStyle.CLEAN_HIGH_KEY_WHITE)

    def test_paper_profile_parsing(self) -> None:
        """Verify PaperProfile parsing and alias tolerance."""
        self.assertEqual(PaperProfile.MATTE_COTTON.value, "matte_cotton")
        for alias in ["matte_cotton", "matte", "cotton_rag", "hahnemuhle"]:
            self.assertEqual(PaperProfile.from_string(alias), PaperProfile.MATTE_COTTON)
        for alias in ["baryta", "baryta_photographique", "fiber"]:
            self.assertEqual(PaperProfile.from_string(alias), PaperProfile.BARYTA)
        for alias in ["luster", "lustre", "semi_gloss", "satin"]:
            self.assertEqual(PaperProfile.from_string(alias), PaperProfile.LUSTER)
        for alias in ["glossy", "high_gloss"]:
            self.assertEqual(PaperProfile.from_string(alias), PaperProfile.GLOSSY)
        for alias in ["canvas", "stretched_canvas"]:
            self.assertEqual(PaperProfile.from_string(alias), PaperProfile.CANVAS)

    def test_rendering_intent_parsing(self) -> None:
        """Verify RenderingIntent parsing and alias tolerance."""
        self.assertEqual(RenderingIntent.RELATIVE_COLORIMETRIC.value, "relative_colorimetric")
        for alias in ["relative_colorimetric", "relative"]:
            self.assertEqual(RenderingIntent.from_string(alias), RenderingIntent.RELATIVE_COLORIMETRIC)
        for alias in ["perceptual", "photographic"]:
            self.assertEqual(RenderingIntent.from_string(alias), RenderingIntent.PERCEPTUAL)

    # =========================================================================
    # PREPRESS & RESOLUTION CALCULATIONS
    # =========================================================================

    def test_inches_to_pixels(self) -> None:
        """Verify accurate physical print size to pixel dimensions conversion."""
        w, h = inches_to_pixels(16, 24, ppi=300)
        self.assertEqual((w, h), (4800, 7200))

        w, h = inches_to_pixels(9, 12, ppi=640)
        self.assertEqual((w, h), (5760, 7680))

        self.assertIn("16x24@300", STANDARD_PRINT_SIZES)
        self.assertEqual(STANDARD_PRINT_SIZES["16x24@300"]["dimensions"], (4800, 7200))
        self.assertIn("matte_cotton", PAPER_CHARACTERISTICS)
        self.assertIn("baryta", PAPER_CHARACTERISTICS)

    def test_aspect_ratios_5_5_and_9_12(self) -> None:
        """Verify new 5:5 and 9:12 aspect ratio calculations across engines."""
        payload_55 = self.compiler.compile(
            scene="Studio portrait",
            target="gpt_images",
            aspect_ratio="5:5",
        )
        self.assertEqual(payload_55.aspect_ratio, "5:5")
        self.assertIn("4000 x 4000", payload_55.positive_prompt)

        payload_912 = self.compiler.compile(
            scene="Exhibition full height fashion shot",
            target="midjourney",
            aspect_ratio="9:12",
        )
        self.assertEqual(payload_912.aspect_ratio, "9:12")
        self.assertIn("--ar 9:12", payload_912.positive_prompt)

    # =========================================================================
    # BODY MORPHOLOGY & PROPORTIONAL VOLUME CALIBRATION
    # =========================================================================

    def test_body_morphology_config_parsing(self) -> None:
        """Verify BodyMorphologyConfig parsing from string syntax."""
        cfg = BodyMorphologyConfig.from_string("biceps:significant, chest:moderate, gut:subtle")
        self.assertIn(BodyVolumeRegion.BICEPS, cfg.target_regions)
        self.assertEqual(cfg.target_regions[BodyVolumeRegion.BICEPS], VolumeDegree.HEAVY_WEIGHT)
        self.assertEqual(cfg.target_regions[BodyVolumeRegion.CHEST], VolumeDegree.NOTICEABLE_RESTRAINED)
        self.assertEqual(cfg.target_regions[BodyVolumeRegion.GUT], VolumeDegree.SUBTLE)

    def test_body_morphology_prompt_injection(self) -> None:
        """Verify body morphology directives and negative shield tokens across engines."""
        payload = self.compiler.compile(
            scene="Athlete seated on wooden bench wearing t-shirt",
            target="flux",
            body_volume="biceps:significant, chest:moderate",
            weight_lb=230,
        )

        prompt = payload.positive_prompt
        self.assertIn("Proportional Body Volume Calibration", prompt)
        self.assertIn("biceps", prompt.lower())
        self.assertIn("230 lb", prompt)
        self.assertIn("bilateral asymmetry", prompt.lower())
        self.assertIn("clothing conformity", prompt.lower())
        self.assertIn("soft-tissue gravity", prompt.lower())

        # Check negative shield contains body distortion protection tokens
        neg = payload.negative_prompt
        self.assertIn("extreme bodybuilding", neg.lower())
        self.assertIn("cartoon proportions", neg.lower())
        self.assertIn("balloon muscles", neg.lower())

    # =========================================================================
    # 4D VOLUMETRIC & PREMIUM MATERIAL ENGINE
    # =========================================================================

    def test_volumetric_material_engine(self) -> None:
        """Verify 4D volumetric lighting, material physics, and background styles."""
        payload = self.compiler.compile(
            scene="Sculptural avant-garde fashion figure",
            target="gpt_images",
            is_4d_volumetric=True,
            material_style="latex_gloss",
            background_style="pure_black_blur",
            remove_text_when_present=True,
        )

        prompt = payload.positive_prompt
        self.assertIn("4D Volumetric & Premium Material Engine", prompt)
        self.assertIn("latex gloss", prompt.lower())
        self.assertIn("contour rim lighting", prompt.lower())
        self.assertIn("pure black blur", prompt.lower())
        self.assertIn("Text removal engine", prompt)

        neg = payload.negative_prompt
        self.assertIn("text", neg.lower())
        self.assertIn("branding", neg.lower())

    # =========================================================================
    # POLICY-SAFE COMPLIANCE RECOVERY LAYER
    # =========================================================================

    def test_policy_safe_all_adapters(self) -> None:
        """Verify policy-safe non-destructive compliance directive across all 7 target adapters."""
        targets = ["gpt_images", "imagen", "midjourney", "flux", "sdxl", "raw", "json"]

        for t in targets:
            payload = self.compiler.compile(
                scene="Dramatic editorial figure in form-fitting wardrobe",
                target=t,
                policy_safe=True,
            )
            self.assertTrue(payload.policy_safe)

            if t == "json":
                data = json.loads(payload.positive_prompt)
                self.assertTrue(data.get("policy_compliance_layer", {}).get("active"))
            elif t == "midjourney":
                self.assertIn("safe ethical fine-art styling", payload.positive_prompt)
                self.assertIn("revealing", payload.negative_prompt.lower())
            elif t == "sdxl":
                self.assertIn("safe ethical fine-art photography", payload.positive_prompt)
                self.assertIn("revealing", payload.negative_prompt.lower())
            else:
                self.assertIn("policy-safe", payload.positive_prompt.lower())

    # =========================================================================
    # PRINT-CALIBRATED PREPRESS MATRIX
    # =========================================================================

    def test_prepress_matrix_compilation(self) -> None:
        """Verify paper profile and print specs in compiler output."""
        payload = self.compiler.compile(
            scene="Architectural gallery study",
            target="raw",
            paper_profile="baryta",
            print_spec="16x24@300",
        )

        self.assertIn("Print-Calibrated Prepress & Exhibition Lab Matrix", payload.positive_prompt)
        self.assertIn("baryta", payload.positive_prompt.lower())
        self.assertIn("4800 x 7200", payload.positive_prompt)
        self.assertIn("300 ppi", payload.positive_prompt.lower())

    # =========================================================================
    # JSON SCHEMA 3.4 UPGRADE
    # =========================================================================

    def test_json_schema_3_4_structure(self) -> None:
        """Verify JSON Prompt engine upgrades to Schema 3.4 when v3.4 features are enabled."""
        payload = self.compiler.compile(
            scene="High-fashion model",
            target="json",
            body_volume="chest:significant",
            weight_lb=210,
            material_style="liquid_glass",
            background_style="pure_black_blur",
            is_4d_volumetric=True,
            paper_profile="matte_cotton",
            policy_safe=True,
        )

        data = json.loads(payload.positive_prompt)
        self.assertEqual(data.get("schema_version"), "3.4")
        self.assertIn("body_morphology_volume_engine", data)
        self.assertEqual(data["body_morphology_volume_engine"]["weight_lb"], 210)
        self.assertIn("volumetric_material_engine", data)
        self.assertEqual(data["volumetric_material_engine"]["material_style"], "liquid_glass")
        self.assertIn("prepress_matrix", data)
        self.assertEqual(data["prepress_matrix"]["paper_profile"], "matte_cotton")
        self.assertIn("policy_compliance_layer", data)
        self.assertTrue(data["policy_compliance_layer"]["active"])
        self.assertIn("body_distortion", data.get("negative_shield", {}))

    # =========================================================================
    # CLI INTEGRATION
    # =========================================================================

    def test_cli_v3_4_flags(self) -> None:
        """Verify CLI accepts and processes v3.4 arguments cleanly."""
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([
                "--scene", "Heroic athlete portrait",
                "--target", "flux",
                "--body-volume", "biceps:significant, chest:moderate",
                "--weight-lb", "225",
                "--material", "latex_gloss",
                "--volumetric-4d",
                "--remove-text",
                "--paper", "baryta",
                "--policy-safe",
            ])
        self.assertEqual(code, 0)
        captured = out.getvalue()
        self.assertIn("Proportional Body Volume Calibration", captured)
        self.assertIn("4D Volumetric & Premium Material Engine", captured)
        self.assertIn("Policy-Safe Compliance Directive", captured)

    # =========================================================================
    # COMFYUI NODE INTEGRATION
    # =========================================================================

    def test_comfyui_node_v3_4_inputs(self) -> None:
        """Verify ComfyUI custom node handles all v3.4 input arguments."""
        node = OpticalCameraCompilerNode()
        inputs = node.INPUT_TYPES()
        optional_keys = inputs.get("optional", {})
        self.assertIn("body_volume", optional_keys)
        self.assertIn("weight_lb", optional_keys)
        self.assertIn("material_style", optional_keys)
        self.assertIn("background_style", optional_keys)
        self.assertIn("volumetric_4d", optional_keys)
        self.assertIn("remove_text", optional_keys)
        self.assertIn("paper_profile", optional_keys)
        self.assertIn("policy_safe", optional_keys)

        pos, neg, unified = node.compile_optical_prompt(
            camera_rig="Phase One XF IQ4 150MP Trichromatic",
            model_target="flux",
            subject="Gallery exhibition portrait",
            aspect_ratio="9:12",
            body_volume="biceps:noticeable",
            weight_lb=215,
            material_style="dielectric_acrylic",
            volumetric_4d="enabled",
            paper_profile="matte_cotton",
            policy_safe="enabled",
        )

        self.assertIn("Proportional Body Volume Calibration", pos)
        self.assertIn("4D Volumetric & Premium Material Engine", pos)
        self.assertIn("extreme bodybuilding", neg.lower())
        self.assertIn(pos, unified)


if __name__ == "__main__":
    unittest.main()
