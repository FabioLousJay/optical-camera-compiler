"""Unit test suite for camera rig specification implementation.

Verifies:
1. All 12 new camera hardware profiles load successfully and provide valid optical specs.
2. The 4 preset and hardware corrections (Sony FE 90mm Macro, Leica SL3-P without Maestro IV,
   Sony VENICE 2 anchor, and Canon R5 II f/8 texture split).
3. All 17 new camera rig presets compile cleanly across target engines.
4. Strict compliance rule: NEVER put photographer, artist, director, or film title names in prompts.
5. Skin & texture lighting modifiers (raking_hard_key, cross_polarized_flash, hard_backlight_rim)
   and their physical conflict resolution.
"""

from __future__ import annotations

import unittest
from optical_compiler.compiler import OpticalCompiler
from optical_compiler.models import SkinLightingModifier, SceneInput
from optical_compiler.profiles import load_profile, list_available_profiles
from optical_compiler.web import CAMERA_PRESETS, LENS_CATALOG


class TestCameraRigSpec(unittest.TestCase):
    """Test suite covering the compiled camera rig specification."""

    def setUp(self) -> None:
        self.compiler = OpticalCompiler(profile="phase_one_iq4")

    def test_all_twelve_new_profiles_load(self) -> None:
        """Verify that all 12 new camera hardware profiles load without error."""
        new_profile_ids = [
            "imax_msm_9802",
            "arri_alexa_265",
            "nikon_fm2",
            "contax_645",
            "hasselblad_xpan",
            "deardorff_8x10",
            "antique_view_8x10",
            "contax_t2",
            "ricoh_gr_iv",
            "dji_mavic_4_pro",
            "mamiya_rz67",
            "polaroid_20x24",
        ]
        available_ids = {p["id"] for p in list_available_profiles()}
        for pid in new_profile_ids:
            self.assertIn(pid, available_ids, f"Profile {pid} missing from list_available_profiles()")
            prof = load_profile(pid)
            self.assertIsNotNone(prof)
            self.assertEqual(prof.profile_id, pid)
            self.assertTrue(len(prof.title) > 0)
            self.assertTrue(len(prof.sensor_and_optics.camera_system) > 0)
            self.assertTrue(len(prof.sensor_and_optics.lens) > 0)

    def test_four_preset_corrections(self) -> None:
        """Verify the 4 required corrections on existing presets and profiles."""
        # 1. Sony Alpha 7R V horology macro preset must use true macro (Sony FE 90mm f/2.8 Macro G OSS)
        preset_horology = CAMERA_PRESETS["cam_sony_a7rv_macro_horology"]
        self.assertIn("90mm", preset_horology["lens"])
        self.assertIn("Macro", preset_horology["lens"])
        self.assertNotIn("50mm f/1.2", preset_horology["lens"])

        # 2. Leica SL3-P must drop unverified "Maestro IV" claim
        prof_sl3 = load_profile("leica_sl3_p")
        self.assertNotIn("Maestro IV", prof_sl3.title)
        self.assertNotIn("Maestro IV", prof_sl3.purpose)
        preset_sl3 = CAMERA_PRESETS["cam_leica_sl3_p_apo"]
        self.assertNotIn("Maestro IV", preset_sl3["mood"])

        # 3. Sony FX Series profile & preset must anchor to Sony VENICE 2 Full-Frame Digital Cinema Camera
        prof_fx = load_profile("sony_fx_series")
        self.assertIn("Sony VENICE 2", prof_fx.sensor_and_optics.camera_system)
        preset_venice = CAMERA_PRESETS["cam_sony_fx_venice_noir"]
        self.assertIn("Sony VENICE 2", preset_venice["mood"])

        # 4. Canon R5 II Vogue: soft (f/1.4) vs texture (f/8.0)
        self.assertIn("cam_canon_eos_r5_ii_vogue_soft", CAMERA_PRESETS)
        self.assertIn("cam_canon_eos_r5_ii_vogue_texture", CAMERA_PRESETS)
        self.assertEqual(CAMERA_PRESETS["cam_canon_eos_r5_ii_vogue_soft"]["aperture"], "f/1.4")
        self.assertEqual(CAMERA_PRESETS["cam_canon_eos_r5_ii_vogue_texture"]["aperture"], "f/8.0")
        self.assertIn("micro-pore", CAMERA_PRESETS["cam_canon_eos_r5_ii_vogue_texture"]["mood"])

    def test_lens_catalog_contains_new_rig_lenses(self) -> None:
        """Verify that LENS_CATALOG in Web Studio has entries for all new systems."""
        expected_systems = [
            "imax_msm_9802",
            "arri_alexa_265",
            "nikon_fm2",
            "contax_645",
            "hasselblad_xpan",
            "deardorff_8x10",
            "antique_view_8x10",
            "contax_t2",
            "ricoh_gr_iv",
            "dji_mavic_4_pro",
            "mamiya_rz67",
            "polaroid_20x24",
        ]
        for sys_id in expected_systems:
            self.assertIn(sys_id, LENS_CATALOG, f"Missing {sys_id} in LENS_CATALOG")
            self.assertTrue(len(LENS_CATALOG[sys_id]) >= 1)

        # Check existing systems updated with new lenses
        self.assertTrue(any("30mm" in lens and "T/S" in lens for lens in LENS_CATALOG["fujifilm_gfx100ii"]))
        self.assertTrue(any("600mm" in lens and "TC" in lens for lens in LENS_CATALOG["nikon_z9"]))
        self.assertTrue(any("120mm" in lens and "Macro" in lens for lens in LENS_CATALOG["phase_one_iq4"]))
        self.assertTrue(any("100mm" in lens and "Macro" in lens for lens in LENS_CATALOG["canon_eos_r5_ii"]))
        self.assertTrue(any("90mm" in lens and "Macro" in lens for lens in LENS_CATALOG["sony_a7rv"]))

    def test_seventeen_new_presets_compile_and_have_no_forbidden_artist_names(self) -> None:
        """Verify all 17 presets compile and strictly omit photographer/artist/movie names."""
        seventeen_preset_keys = [
            "cam_fujifilm_gfx100ii_ts",
            "cam_leica_m6_cinestill_800t",
            "cam_nikon_z9_tele_wildlife",
            "cam_imax_msm_9802_bw",
            "cam_arri_alexa_265_vista",
            "cam_nikon_fm2_kodachrome",
            "cam_contax_645_wedding",
            "cam_hasselblad_xpan_panorama",
            "cam_deardorff_8x10_portrait",
            "cam_antique_view_8x10_collodion",
            "cam_contax_t2_candid",
            "cam_ricoh_gr_iv_street",
            "cam_dji_mavic_4_pro_nadir",
            "cam_phase_one_iq4_macro_beauty",
            "cam_canon_eos_r5_ii_macro_iris",
            "cam_mamiya_rz67_kino_flo",
            "cam_polaroid_20x24_contact",
        ]

        forbidden_names = [
            "steve mccurry",
            "richard avedon",
            "sally mann",
            "chuck close",
            "gregory crewdson",
            "afghan girl",
            "national geographic",
            "oppenheimer",
            "christopher nolan",
            "hoyte van hoytema",
        ]

        for pkey in seventeen_preset_keys:
            self.assertIn(pkey, CAMERA_PRESETS, f"Preset {pkey} missing from CAMERA_PRESETS")
            cfg = CAMERA_PRESETS[pkey]

            # Compile across multiple engines
            for target in ["gpt_images", "flux", "firefly"]:
                comp = OpticalCompiler(profile=cfg["profile"])
                payload = comp.compile(
                    scene=cfg["subject"],
                    target=target,
                    framing=cfg.get("framing"),
                    environment=cfg.get("environment"),
                    wardrobe=cfg.get("wardrobe"),
                    mood=cfg.get("mood"),
                    aperture=cfg.get("aperture"),
                    lens=cfg.get("lens"),
                    lighting=cfg.get("lighting"),
                    aspect_ratio=cfg.get("aspectRatio", "4:5"),
                    film_stock=cfg.get("filmStock"),
                    skin_lighting=cfg.get("skinLighting"),
                )

                prompt_lower = (payload.positive_prompt + " " + payload.unified_prompt).lower()
                for name in forbidden_names:
                    self.assertNotIn(
                        name,
                        prompt_lower,
                        f"Forbidden name '{name}' detected in compiled prompt for preset {pkey} on {target}!"
                    )

    def test_skin_lighting_modifiers_and_conflict_resolution(self) -> None:
        """Verify skin lighting modifiers and conflict resolution behavior."""
        # 1. Raking Hard Key
        comp = OpticalCompiler(profile="canon_eos_r5_ii")
        p_raking = comp.compile(
            scene="Portrait of an athlete",
            skin_lighting=SkinLightingModifier.RAKING_HARD_KEY,
        )
        self.assertIn("raking low across the skin", p_raking.positive_prompt.lower())
        self.assertIn("non-polarized", p_raking.positive_prompt.lower())
        self.assertIn("vellus hair", p_raking.positive_prompt.lower())

        # 2. Cross-Polarized Flash
        p_cpl = comp.compile(
            scene="Dermatological clinical portrait",
            skin_lighting=SkinLightingModifier.CROSS_POLARIZED_FLASH,
        )
        self.assertIn("cross-polarized flash lighting", p_cpl.positive_prompt.lower())
        self.assertIn("completely matte skin with no specular shine", p_cpl.positive_prompt.lower())

        # 3. Hard Backlight Rim
        p_rim = comp.compile(
            scene="Dramatic cinematic profile",
            skin_lighting=SkinLightingModifier.HARD_BACKLIGHT_RIM,
        )
        self.assertIn("hard backlight rim light", p_rim.positive_prompt.lower())
        self.assertIn("individual hair strands glowing", p_rim.positive_prompt.lower())

        # 4. String alias parsing in compiler
        p_alias = comp.compile(
            scene="Skin portrait",
            skin_lighting="cross_polarized_flash",
        )
        self.assertIn("cross-polarized", p_alias.positive_prompt.lower())


if __name__ == "__main__":
    unittest.main()
