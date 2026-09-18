"""Dedicated test suite validating Leica Q3 Monochrom specifications
(60MP monochrome sensor and ISO range of 100-200,000) and the 5 requested Leica lenses.
"""

from __future__ import annotations

import json
import unittest

from optical_compiler.compiler import OpticalCompiler, compile_scene
from optical_compiler.models import (
    APPROVED_RESTORATION_CAMERAS,
    APPROVED_RESTORATION_LENSES,
    RESTORATION_LENS_ALIASES,
    SceneInput,
    TargetEngine,
    UniversalDepixelateV2Spec,
    normalize_lens_name,
)
from optical_compiler.presets import LENS_CATALOG, OPTICAL_PRESETS
from optical_compiler.profiles import auto_select_profile, load_profile


class TestLeicaQ3MonochromHardware(unittest.TestCase):
    """Verify Leica Q3 Monochrom sensor resolution, CFA-free architecture, and ISO range 100-200,000."""

    def setUp(self):
        self.profile = load_profile("leica_q3_monochrom")

    def test_60mp_monochrome_sensor(self):
        """Verify 60MP monochrome sensor specifications."""
        optics = self.profile.sensor_and_optics
        self.assertIn("60.3MP", optics.sensor_type)
        self.assertIn("Monochrome", optics.sensor_type)
        self.assertIn("zero Color Filter Array", optics.sensor_type)
        self.assertIn("60.3MP", optics.sensor_dimensions)
        self.assertIn("pure luminance", optics.sensor_type.lower())

    def test_iso_range_100_to_200000(self):
        """Verify the native ISO range of 100-200,000 is explicitly specified."""
        optics = self.profile.sensor_and_optics
        self.assertIn("100-200,000", optics.iso_base)
        self.assertIn("125", optics.iso_base)

        lighting = self.profile.lighting_and_exposure
        self.assertIn("100-200,000", lighting.primary_lighting)

        self.assertIn("100-200,000", self.profile.execution_directive)

    def test_q3_monochrom_crop_modes_in_catalog(self):
        """Verify 28mm, 35mm, 50mm, 75mm, and 90mm frame line crop modes exist."""
        q3_lenses = LENS_CATALOG.get("leica_q3_monochrom", [])
        lens_text = " ".join(q3_lenses)
        self.assertIn("28mm", lens_text)
        self.assertIn("35mm Crop Mode", lens_text)
        self.assertIn("50mm Crop Mode", lens_text)
        self.assertIn("75mm Crop Mode", lens_text)
        self.assertIn("90mm Crop Mode", lens_text)

    def test_router_handles_iso_and_60mp_keywords(self):
        """Verify queries with ISO 100-200,000 or 60MP monochrome route to Q3 Monochrom."""
        queries = [
            "monochrome street photography at ISO 100-200,000",
            "night documentary shot on 60MP monochrome sensor",
            "high sensitivity ISO 200,000 pure luminance street portrait",
        ]
        for q in queries:
            routed = auto_select_profile(q)
            self.assertEqual(
                routed,
                "leica_q3_monochrom",
                f"Failed routing for query: '{q}' (got '{routed}')",
            )


class TestLeicaLensesPoolAndNormalization(unittest.TestCase):
    """Verify the 5 requested Leica lenses are present and properly normalized."""

    def test_all_five_lenses_in_approved_pool(self):
        """Verify canonical names of all 5 lenses exist in APPROVED_RESTORATION_LENSES."""
        expected = [
            "Leica APO-Summicron-SL 90mm f/2",
            "Leica 50mm f/2 Summicron APO ASPH",
            "Leica 75mm f/1.25 Noctilux",
            "Leica 90mm f/2 Summicron-M",
            "Leica 35mm f/1.4 Summilux-M ASPH II",
        ]
        for lens in expected:
            self.assertIn(lens, APPROVED_RESTORATION_LENSES)

    def test_user_syntax_variants_normalize_properly(self):
        """Verify user syntax variants (e.g., f2, f1.25, Summilux M) resolve to canonical names."""
        test_cases = [
            ("Leica APO-Summicron-SL 90mm f2", "Leica APO-Summicron-SL 90mm f/2"),
            ("leica apo-summicron-sl 90mm f2", "Leica APO-Summicron-SL 90mm f/2"),
            ("Leica APO-Summicron-SL 90mm f/2 ASPH", "Leica APO-Summicron-SL 90mm f/2"),
            ("Leica 50mm f2 Summicron APO ASPH", "Leica 50mm f/2 Summicron APO ASPH"),
            ("leica 50mm f2 summicron apo asph", "Leica 50mm f/2 Summicron APO ASPH"),
            ("Leica APO-Summicron-M 50mm f/2 ASPH", "Leica 50mm f/2 Summicron APO ASPH"),
            ("Leica 75mm f1.25 Noctilux", "Leica 75mm f/1.25 Noctilux"),
            ("leica 75mm f1.25 noctilux", "Leica 75mm f/1.25 Noctilux"),
            ("Leica Noctilux-M 75mm f/1.25 ASPH", "Leica 75mm f/1.25 Noctilux"),
            ("Leica 90mm f2 Summicron-M", "Leica 90mm f/2 Summicron-M"),
            ("leica 90mm f2 summicron-m", "Leica 90mm f/2 Summicron-M"),
            ("Leica APO-Summicron-M 90mm f/2 ASPH", "Leica 90mm f/2 Summicron-M"),
            ("Leica 35mm f/1.4 Summilux M ASPH II", "Leica 35mm f/1.4 Summilux-M ASPH II"),
            ("leica 35mm f/1.4 summilux m asph ii", "Leica 35mm f/1.4 Summilux-M ASPH II"),
            ("Leica Summilux-M 35mm f/1.4 ASPH II", "Leica 35mm f/1.4 Summilux-M ASPH II"),
        ]

        for user_str, expected in test_cases:
            normalized = normalize_lens_name(user_str)
            self.assertEqual(
                normalized,
                expected,
                f"Failed normalizing '{user_str}': got '{normalized}', expected '{expected}'",
            )

    def test_depixelate_v2_spec_normalizes_user_lens(self):
        """Verify UniversalDepixelateV2Spec automatically normalizes user-provided lens strings."""
        spec = UniversalDepixelateV2Spec(
            camera_class="Leica SL3",
            lens="Leica APO-Summicron-SL 90mm f2",
        )
        self.assertEqual(spec.lens, "Leica APO-Summicron-SL 90mm f/2")
        self.assertEqual(spec.selected_lens, "Leica APO-Summicron-SL 90mm f/2")


class TestLeicaLensPresetsAndCatalog(unittest.TestCase):
    """Verify lens catalog and optical presets contain the 5 Leica lenses."""

    def test_sl_mount_cameras_have_90mm_apo_summicron(self):
        """Verify Leica SL3-P and SL2 catalogs contain the 90mm APO-Summicron-SL."""
        for cam in ["leica_sl3_p", "leica_sl2"]:
            catalog = LENS_CATALOG.get(cam, [])
            matches = [l for l in catalog if "90mm" in l and "APO-Summicron-SL" in l]
            self.assertTrue(
                len(matches) > 0,
                f"Missing 90mm APO-Summicron-SL in {cam} catalog",
            )

    def test_m_mount_cameras_have_all_m_lenses(self):
        """Verify Leica M11 and M6 catalogs contain 75mm Noctilux, 90mm Summicron, 50mm Summicron APO, and 35mm Summilux ASPH II."""
        m11_catalog = " ".join(LENS_CATALOG.get("leica_m11", []))
        self.assertIn("Noctilux-M 75mm f/1.25 ASPH", m11_catalog)
        self.assertIn("APO-Summicron-M 90mm f/2 ASPH", m11_catalog)
        self.assertIn("APO-Summicron-M 50mm f/2 ASPH", m11_catalog)
        self.assertIn("Summilux-M 35mm f/1.4 ASPH II", m11_catalog)

        m6_catalog = " ".join(LENS_CATALOG.get("leica_m6_analog", []))
        self.assertIn("Noctilux-M 75mm f/1.25 ASPH", m6_catalog)
        self.assertIn("APO-Summicron-M 90mm f/2 ASPH", m6_catalog)

    def test_new_leica_optical_presets_compile(self):
        """Verify the 5 new Leica optical presets compile cleanly across engines."""
        compiler = OpticalCompiler(profile="phase_one_iq4")
        presets = [
            "cam_leica_sl3_p_apo_90mm",
            "cam_leica_m11_noctilux_75mm",
            "cam_leica_m11_summicron_90mm",
            "cam_leica_m11_summicron_apo_50mm",
            "cam_leica_m11_summilux_35mm_asph_ii",
        ]

        for preset_name in presets:
            self.assertIn(preset_name, OPTICAL_PRESETS)
            data = OPTICAL_PRESETS[preset_name]

            comp = OpticalCompiler(profile=data["profile"])
            payload = comp.compile(
                scene=data["subject"],
                lens=data["lens"],
                aperture=data.get("aperture"),
                target="gpt_images",
            )
            self.assertIn(data["lens"], payload.positive_prompt)
            self.assertIn(data["profile"], payload.metadata.get("hardware_profile"))


class TestCompilerLensOverrides(unittest.TestCase):
    """Verify user can supply any of the 5 lenses directly to the compiler."""

    def test_compile_with_user_provided_lenses(self):
        user_lenses = [
            "Leica APO-Summicron-SL 90mm f2",
            "Leica 50mm f2 Summicron APO ASPH",
            "Leica 75mm f1.25 Noctilux",
            "Leica 90mm f2 Summicron-M",
            "Leica 35mm f/1.4 Summilux M ASPH II",
        ]

        for u_lens in user_lenses:
            payload = compile_scene(
                scene="Intimate documentary street portrait",
                target_model="flux",
                profile="leica_q3_monochrom",
                lens=u_lens,
            )
            self.assertIn(u_lens, payload.positive_prompt)

    def test_compile_q3_monochrom_includes_specs(self):
        """Verify Q3 Monochrom compilations reflect 60.3MP sensor and 100-200,000 ISO range."""
        payload = compile_scene(
            scene="Fine art architectural study in black and white",
            target_model="raw",
            profile="leica_q3_monochrom",
        )
        self.assertIn("60.3MP", payload.positive_prompt)
        self.assertIn("100-200,000", payload.positive_prompt)
        self.assertIn("Monochrome", payload.positive_prompt)


if __name__ == "__main__":
    unittest.main()
