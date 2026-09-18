"""Unit test suite verifying Nikon Z5 II, Canon EOS R6 III, and Canon EOS R5 II gear specifications."""

from __future__ import annotations

import unittest
from optical_compiler.compiler import OpticalCompiler
from optical_compiler.comfy_nodes import RIG_NAMES, RIG_NAME_TO_ID
from optical_compiler.presets import CAMERA_PRESETS as PRESETS_PY_PRESETS, LENS_CATALOG as PRESETS_PY_LENSES
from optical_compiler.profiles import auto_select_profile, list_available_profiles, load_profile
from optical_compiler.web import CAMERA_PRESETS as WEB_PRESETS, LENS_CATALOG as WEB_LENSES, StudioAPIHandler


class TestGearSpecification(unittest.TestCase):
    """Verification suite for Nikon Z5 II, Canon EOS R6 III, and Canon EOS R5 II."""

    def test_gear_profiles_present_in_catalog(self) -> None:
        """Verify all three gear profiles are discovered by list_available_profiles()."""
        available = list_available_profiles()
        ids = {p["id"] for p in available}
        self.assertIn("nikon_z5_ii", ids)
        self.assertIn("canon_eos_r6_iii", ids)
        self.assertIn("canon_eos_r5_ii", ids)

    def test_nikon_z5_ii_specifications(self) -> None:
        """Verify Nikon Z5 II 24MP full-frame CMOS, 4K 60p, and all-rounder specifications."""
        prof = load_profile("nikon_z5_ii")
        self.assertEqual(prof.profile_id, "nikon_z5_ii")
        self.assertIn("Nikon Z 5 II", prof.title)
        self.assertIn("24MP", prof.purpose)
        self.assertIn("4K 60p", prof.purpose)
        self.assertIn("all-rounder", prof.purpose.lower())
        self.assertIn("touchscreen", prof.purpose.lower())
        self.assertIn("great value", prof.purpose.lower())

        # Sensor and optics check
        so = prof.sensor_and_optics
        self.assertEqual(so.camera_system, "Nikon Z 5 II")
        self.assertIn("24", so.sensor_dimensions)
        self.assertIn("full-frame", so.sensor_type.lower())
        self.assertIn("4K 60p", so.dynamic_range)
        self.assertIn("NIKKOR Z", so.lens)

    def test_canon_eos_r6_iii_specifications(self) -> None:
        """Verify Canon EOS R6 III 32.5MP full-frame CMOS, 7K 60p, and autofocus specifications."""
        prof = load_profile("canon_eos_r6_iii")
        self.assertEqual(prof.profile_id, "canon_eos_r6_iii")
        self.assertIn("Canon EOS R6 Mark III", prof.title)
        self.assertIn("32.5MP", prof.purpose)
        self.assertIn("7K 60p", prof.purpose)
        self.assertIn("all-rounder", prof.purpose.lower())
        self.assertIn("autofocus", prof.purpose.lower())

        # Sensor and optics check
        so = prof.sensor_and_optics
        self.assertEqual(so.camera_system, "Canon EOS R6 Mark III")
        self.assertIn("32.5MP", so.sensor_dimensions)
        self.assertIn("full-frame", so.sensor_type.lower())
        self.assertIn("7K 60p", so.dynamic_range)
        self.assertIn("Canon RF", so.lens)

    def test_canon_eos_r5_ii_specifications(self) -> None:
        """Verify Canon EOS R5 II 45MP full-frame CMOS, 8K 60p specifications."""
        prof = load_profile("canon_eos_r5_ii")
        self.assertEqual(prof.profile_id, "canon_eos_r5_ii")
        self.assertIn("Canon EOS R5 Mark II", prof.title)
        self.assertIn("45MP", prof.purpose)
        self.assertIn("8K", prof.purpose)
        self.assertIn("60p", prof.purpose)

        # Sensor and optics check
        so = prof.sensor_and_optics
        self.assertEqual(so.camera_system, "Canon EOS R5 Mark II")
        self.assertIn("45", so.sensor_dimensions)
        self.assertIn("full-frame", so.sensor_type.lower())
        self.assertIn("8K 60p", so.dynamic_range)

    def test_profile_aliases_resolution(self) -> None:
        """Verify common naming variations and aliases resolve to target profiles."""
        nikon_aliases = ["nikon_z5_ii", "nikon z5 ii", "nikon-z5-ii", "z5_ii", "z5ii", "nikon_z5"]
        for alias in nikon_aliases:
            prof = load_profile(alias)
            self.assertEqual(prof.profile_id, "nikon_z5_ii", f"Failed alias: {alias}")

        r6_aliases = ["canon_eos_r6_iii", "canon eos r6 mark iii", "canon_r6_iii", "r6_iii", "r6iii"]
        for alias in r6_aliases:
            prof = load_profile(alias)
            self.assertEqual(prof.profile_id, "canon_eos_r6_iii", f"Failed alias: {alias}")

        r5_aliases = ["canon_eos_r5_ii", "canon eos r5 mark ii", "canon_r5_ii", "r5_ii", "r5ii"]
        for alias in r5_aliases:
            prof = load_profile(alias)
            self.assertEqual(prof.profile_id, "canon_eos_r5_ii", f"Failed alias: {alias}")

    def test_intelligent_auto_routing(self) -> None:
        """Verify natural scene queries route to the appropriate camera systems."""
        self.assertEqual(auto_select_profile("Editorial craft documentary shot on Nikon Z5 II"), "nikon_z5_ii")
        self.assertEqual(auto_select_profile("Travel series captured with 4k 60p nikon setup"), "nikon_z5_ii")

        self.assertEqual(auto_select_profile("Architectural shoot with Canon EOS R6 Mark III 7K 60p"), "canon_eos_r6_iii")
        self.assertEqual(auto_select_profile("Studio shoot with Canon 32.5MP all-rounder"), "canon_eos_r6_iii")

        self.assertEqual(auto_select_profile("High-fashion beauty shot on Canon EOS R5 Mark II 8k 60p"), "canon_eos_r5_ii")
        self.assertEqual(auto_select_profile("High-resolution studio portrait with Canon 45MP stacked sensor"), "canon_eos_r5_ii")

    def test_lens_catalog_entries(self) -> None:
        """Verify matched lenses exist for all three systems in presets and web modules."""
        for catalog in (PRESETS_PY_LENSES, WEB_LENSES):
            self.assertIn("nikon_z5_ii", catalog)
            self.assertGreaterEqual(len(catalog["nikon_z5_ii"]), 3)
            self.assertTrue(any("24-70mm" in l for l in catalog["nikon_z5_ii"]))

            self.assertIn("canon_eos_r6_iii", catalog)
            self.assertGreaterEqual(len(catalog["canon_eos_r6_iii"]), 3)
            self.assertTrue(any("24-70mm" in l for l in catalog["canon_eos_r6_iii"]))

            self.assertIn("canon_eos_r5_ii", catalog)
            self.assertGreaterEqual(len(catalog["canon_eos_r5_ii"]), 3)
            self.assertTrue(any("85mm" in l for l in catalog["canon_eos_r5_ii"]))

    def test_comfy_ui_node_registration(self) -> None:
        """Verify ComfyUI node lists the new camera systems in dropdowns and mapping dictionary."""
        self.assertIn("Nikon Z 5 II All-Rounder Full-Frame", RIG_NAMES)
        self.assertIn("Canon EOS R6 Mark III All-Rounder Full-Frame", RIG_NAMES)
        self.assertIn("Canon EOS R5 Mark II Stacked Full-Frame", RIG_NAMES)

        self.assertEqual(RIG_NAME_TO_ID["Nikon Z 5 II All-Rounder Full-Frame"], "nikon_z5_ii")
        self.assertEqual(RIG_NAME_TO_ID["Canon EOS R6 Mark III All-Rounder Full-Frame"], "canon_eos_r6_iii")
        self.assertEqual(RIG_NAME_TO_ID["Canon EOS R5 Mark II Stacked Full-Frame"], "canon_eos_r5_ii")

    def test_presets_compilation(self) -> None:
        """Verify presets for the new cameras compile cleanly across target engines."""
        test_presets = [
            "cam_nikon_z5_ii_allrounder",
            "cam_canon_eos_r6_iii_allrounder",
            "cam_canon_eos_r5_ii_vogue_soft",
        ]
        targets = ["gpt_images", "flux", "sdxl", "midjourney"]

        for pkey in test_presets:
            self.assertIn(pkey, PRESETS_PY_PRESETS)
            self.assertIn(pkey, WEB_PRESETS)
            cfg = PRESETS_PY_PRESETS[pkey]
            for tgt in targets:
                compiler = OpticalCompiler(profile=cfg["profile"])
                payload = compiler.compile(
                    scene=cfg["subject"],
                    target=tgt,
                    framing=cfg.get("framing"),
                    environment=cfg.get("environment"),
                    wardrobe=cfg.get("wardrobe"),
                    mood=cfg.get("mood"),
                    aperture=cfg.get("aperture"),
                    lens=cfg.get("lens"),
                    lighting=cfg.get("lighting"),
                    aspect_ratio=cfg.get("aspectRatio", "4:5"),
                    film_stock=cfg.get("filmStock"),
                )
                self.assertIsNotNone(payload.positive_prompt)
                self.assertGreater(len(payload.positive_prompt), 50)
                self.assertIsNotNone(payload.unified_prompt)


if __name__ == "__main__":
    unittest.main()
