from __future__ import annotations

import unittest

from optical_compiler.compiler import OpticalCompiler
from optical_compiler.models import SceneInput
from optical_compiler.pro_acuity import PRO_ACUITY_NEGATIVES, pro_acuity_negatives
from optical_compiler.profiles import list_available_profiles as list_profiles


class TestProAcuityShield(unittest.TestCase):
    """The professional acuity negative set must reach every camera profile and engine."""

    def test_every_profile_receives_pro_negatives_on_qwen_and_sdxl(self) -> None:
        profiles = list_profiles()
        self.assertGreater(len(profiles), 10)
        for prof in profiles:
            pid = prof["id"]
            compiler = OpticalCompiler(profile=pid)
            for target in ("qwen_image", "sdxl", "flux"):
                payload = compiler.compile(SceneInput(subject="editorial portrait of a man"), target=target)
                neg = payload.negative_prompt.lower()
                for tok in ("soft focus", "motion blur", "oversmoothed skin", "beauty filter", "warped hands"):
                    self.assertIn(tok, neg, f"{pid}/{target} missing '{tok}'")
                self.assertIn("Professional Acuity Lock", payload.positive_prompt)

    def test_wide_and_fisheye_lens_exemption(self) -> None:
        self.assertNotIn("wide angle", pro_acuity_negatives("Canon RF 15-35mm f/2.8L"))
        self.assertNotIn("fisheye", pro_acuity_negatives("Nikon 8-15mm Fisheye"))
        self.assertEqual(list(PRO_ACUITY_NEGATIVES), pro_acuity_negatives("Sony FE 85mm F1.4 GM II"))

    def test_midjourney_no_flag_extended_without_anatomy_nouns(self) -> None:
        payload = OpticalCompiler(profile="sony_a1_ii").compile(SceneInput(subject="portrait"), target="midjourney")
        self.assertIn("soft focus", payload.positive_prompt.split("--no", 1)[1])
        self.assertNotIn("anatomy", payload.negative_prompt.lower())


if __name__ == "__main__":
    unittest.main()
