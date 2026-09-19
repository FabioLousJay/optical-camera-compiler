"""Test suite for Midjourney and Adobe Firefly prompt quality, photorealism, and visual outcome enforcement.

Verifies:
1. Non-toxic Midjourney negative prompt (zero anatomy/facial noun penalties that turn subjects around).
2. Mandatory gaze and orientation anchors (facing camera, direct eye contact) for portraits.
3. Zero catalog serial numbers (ILCE-1M2, SEL85F14GM2) in Midjourney and Firefly prompts.
4. Adobe Firefly natural narrative flow without colon-separated meta labels (Style:, Setting:, Lighting:).
5. Adobe Firefly exclude-from-image negative channel population and strict <= 1,024 char limit.
6. Real visual consequence clauses across camera profiles (Phase One, Leica, Nikon FM2, Contax T2, IMAX).
"""

from __future__ import annotations

import unittest
from optical_compiler.compiler import OpticalCompiler
from optical_compiler.models import SceneInput, TargetEngine


class TestMidjourneyFireflyQuality(unittest.TestCase):
    """Quality and visual outcome test suite for Midjourney and Firefly."""

    def setUp(self) -> None:
        self.compiler = OpticalCompiler(profile="sony_a1_ii")

    def test_user_scenario_midjourney_non_toxic_negative(self) -> None:
        """Verify the exact user scenario on Midjourney: no toxic negative penalties and clear gaze anchor."""
        scene = SceneInput(
            subject="two tall, ultra large 468 pound fat white males",
            framing="Three quarter editorial portrait",
            environment="Grand Canyon",
            weight_lb=468,
            body_volume="gut, waist",
        )
        res = self.compiler.compile(scene=scene, target="midjourney")
        pos = res.positive_prompt
        neg = res.negative_prompt.lower()

        # 1. Mandatory camera-facing gaze anchor must be present
        self.assertIn("facing camera", pos.lower())
        self.assertIn("direct eye contact", pos.lower())

        # 2. Body build must be described with natural photographic terms, not biomechanical lab jargon
        self.assertIn("heavyset", pos.lower())
        self.assertIn("468lbs", pos)

        # 3. No raw catalog serial numbers
        self.assertNotIn("(ILCE-1M2)", pos)
        self.assertNotIn("(SEL85F14GM2)", pos)

        # 4. Strict Non-Toxic Rule: Negative prompt MUST NOT contain facial, neck, forehead, or cheek nouns
        forbidden_in_negative = [
            "forehead",
            "neck",
            "cheek",
            "swirl",
            "worm",
            "face",
            "bokeh",
            "depth of field",
            "proportions",
            "anatomy",
        ]
        for term in forbidden_in_negative:
            self.assertNotIn(term, neg, f"Toxic token '{term}' found in Midjourney negative prompt!")

        # 5. Core universal render shields must be present
        self.assertIn("plastic skin", neg)
        self.assertIn("airbrushed", neg)
        self.assertIn("cgi", neg)
        self.assertIn("3d render", neg)
        self.assertIn("illustration", neg)

    def test_user_scenario_firefly_clean_narrative(self) -> None:
        """Verify the exact user scenario on Adobe Firefly: clean photographic narrative without meta-labels."""
        scene = SceneInput(
            subject="two tall, ultra large 468 pound fat white males",
            framing="Three quarter editorial portrait",
            environment="Grand Canyon",
            weight_lb=468,
            body_volume="gut, waist",
        )
        res = self.compiler.compile(scene=scene, target="firefly")
        pos = res.positive_prompt

        # 1. No colon-separated meta-labels
        self.assertNotIn("Style:", pos)
        self.assertNotIn("Setting:", pos)
        self.assertNotIn("Attire:", pos)
        self.assertNotIn("Mood:", pos)
        self.assertNotIn("Lighting:", pos)

        # 2. No bureaucratic disclaimers
        self.assertNotIn("Tasteful editorial photographic execution adhering to commercial safety standards", pos)

        # 3. Mandatory gaze anchor
        self.assertIn("facing camera with direct eye contact", pos.lower())

        # 4. Clean optical depth and lighting description
        self.assertIn("Shot on Sony a1 II", pos)
        self.assertIn("optical depth of field", pos.lower())

        # 5. Character limit guarantee
        self.assertLessEqual(len(pos), 1024)

        # 6. Exclude from image negative channel populated
        self.assertTrue(len(res.negative_prompt) > 0)
        self.assertIn("illustration", res.negative_prompt)
        self.assertIn("plastic skin", res.negative_prompt)

    def test_camera_visual_consequences_midjourney(self) -> None:
        """Verify that distinct camera profiles produce concrete visual consequences in Midjourney."""
        # 1. Contax T2 -> direct xenon flash with rapid falloff
        c_t2 = OpticalCompiler(profile="contax_t2")
        res_t2 = c_t2.compile("Party guests celebrating", target="midjourney")
        self.assertIn("direct on-camera xenon flash", res_t2.positive_prompt.lower())

        # 2. Nikon FM2 -> Kodachrome 64 slide film saturation
        c_fm2 = OpticalCompiler(profile="nikon_fm2")
        res_fm2 = c_fm2.compile("Nomad in desert dunes", target="midjourney")
        self.assertIn("kodachrome 64", res_fm2.positive_prompt.lower())

        # 3. Leica Q3 Monochrom -> pure panchromatic black-and-white
        c_q3 = OpticalCompiler(profile="leica_q3_monochrom")
        res_q3 = c_q3.compile("Street musician at night", target="midjourney")
        self.assertIn("pure panchromatic black-and-white", res_q3.positive_prompt.lower())

        # 4. Polaroid 20x24 -> life-size 1:1 contact scale
        c_polaroid = OpticalCompiler(profile="polaroid_20x24")
        res_polaroid = c_polaroid.compile("Artist portrait", target="midjourney")
        self.assertIn("life-size 1:1 contact", res_polaroid.positive_prompt.lower())


if __name__ == "__main__":
    unittest.main()
