"""Test suite for the 6 new camera systems:
- Canon PowerShot G7 X Mark III
- Fujifilm X-E5
- Nikon Z50 II
- OM System OM-5 Mark II
- Panasonic Lumix G97
- Sony Alpha 7C II
"""

import json
from pathlib import Path
import unittest

from optical_compiler.compiler import OpticalCompiler
from optical_compiler.intelligence import (
    DEFAULT_HARDWARE_SPECS,
    PROFILE_DISPLAY_NAMES,
    PromptIntelligenceEngine,
)
from optical_compiler.models import CameraProfile, SceneInput, TargetEngine
from optical_compiler.presets import CAMERA_PRESETS, LENS_CATALOG
from optical_compiler.profiles import (
    auto_select_profile,
    DEFAULT_PROFILES_DIR,
    load_profile,
    PACKAGE_PROFILES_DIR,
)


class TestNewCamerasSuite(unittest.TestCase):
    """Rigorously verify all 6 newly added camera systems."""

    NEW_CAMERAS = [
        "canon_powershot_g7x_iii",
        "fujifilm_x_e5",
        "nikon_z50_ii",
        "om_system_om5_ii",
        "panasonic_lumix_g97",
        "sony_a7c_ii",
    ]

    def test_profile_files_exist_in_both_directories(self):
        """Verify profile JSON files exist in both repo profiles/ and package profiles_data/."""
        for cam in self.NEW_CAMERAS:
            repo_file = DEFAULT_PROFILES_DIR / f"{cam}.json"
            pkg_file = PACKAGE_PROFILES_DIR / f"{cam}.json"
            self.assertTrue(repo_file.is_file(), f"Missing repo profile: {repo_file}")
            self.assertTrue(pkg_file.is_file(), f"Missing package profile: {pkg_file}")

            # Verify valid JSON and Schema 2.0
            with open(repo_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data.get("profile_id"), cam)
            self.assertEqual(data.get("schema_version"), "2.0")
            self.assertIn("sensor_and_optics", data)
            self.assertIn("micro_detail_and_physics", data)
            self.assertIn("execution_directive", data)

    def test_profile_loading_and_dataclass(self):
        """Verify load_profile successfully constructs CameraProfile dataclass."""
        for cam in self.NEW_CAMERAS:
            profile = load_profile(cam)
            self.assertIsInstance(profile, CameraProfile)
            self.assertEqual(profile.profile_id, cam)
            self.assertTrue(profile.title)
            self.assertTrue(profile.sensor_and_optics.camera_system)
            self.assertTrue(profile.sensor_and_optics.sensor_type)
            self.assertTrue(profile.sensor_and_optics.lens)
            self.assertTrue(profile.execution_directive)

    def test_profile_aliases_resolution(self):
        """Verify common abbreviations and colloquial names resolve correctly."""
        alias_tests = [
            ("g7x_iii", "canon_powershot_g7x_iii"),
            ("powershot_g7x", "canon_powershot_g7x_iii"),
            ("canon_g7x_mark_iii", "canon_powershot_g7x_iii"),
            ("xe5", "fujifilm_x_e5"),
            ("fuji_x_e5", "fujifilm_x_e5"),
            ("fujifilm_xe5", "fujifilm_x_e5"),
            ("z50_ii", "nikon_z50_ii"),
            ("z50ii", "nikon_z50_ii"),
            ("nikon_z50", "nikon_z50_ii"),
            ("om5_ii", "om_system_om5_ii"),
            ("om-5 mark ii", "om_system_om5_ii"),
            ("om_system_om5", "om_system_om5_ii"),
            ("lumix_g97", "panasonic_lumix_g97"),
            ("dc_g97", "panasonic_lumix_g97"),
            ("panasonic_g97", "panasonic_lumix_g97"),
            ("a7c_ii", "sony_a7c_ii"),
            ("a7cii", "sony_a7c_ii"),
            ("sony_alpha_7c_ii", "sony_a7c_ii"),
        ]
        for alias, expected in alias_tests:
            profile = load_profile(alias)
            self.assertEqual(profile.profile_id, expected, f"Alias '{alias}' did not resolve to '{expected}'")

    def test_camera_router_keywords(self):
        """Verify auto_select_profile routes distinctive keywords to new cameras."""
        router_tests = [
            ("Street photograph shot on Canon PowerShot G7 X Mark III with flash", "canon_powershot_g7x_iii"),
            ("Documentary shot in Kyoto on Fujifilm X-E5 with Reala Ace", "fujifilm_x_e5"),
            ("Artisan workshop captured on Nikon Z50 II with picture control button", "nikon_z50_ii"),
            ("Wilderness expedition in rain with OM System OM-5 Mark II IP53 weather sealed", "om_system_om5_ii"),
            ("Travel documentary shot on Panasonic Lumix G97 with 5-axis dual is 2", "panasonic_lumix_g97"),
            ("Fashion street editorial on Sony A7C II compact full frame", "sony_a7c_ii"),
        ]
        for text, expected in router_tests:
            result = auto_select_profile(text)
            self.assertEqual(result, expected, f"Text '{text}' did not route to '{expected}', got '{result}'")

    def test_lens_catalog_entries(self):
        """Verify all 6 cameras have matched real-world lenses in LENS_CATALOG."""
        for cam in self.NEW_CAMERAS:
            self.assertIn(cam, LENS_CATALOG, f"Missing {cam} in LENS_CATALOG")
            lenses = LENS_CATALOG[cam]
            self.assertGreaterEqual(len(lenses), 3, f"Expected at least 3 lenses for {cam}, found {len(lenses)}")
            for lens in lenses:
                self.assertIsInstance(lens, str)
                self.assertTrue(len(lens) > 5)

    def test_camera_presets_integrity(self):
        """Verify calibrated presets exist and reference valid camera profiles."""
        preset_keys = [
            "cam_canon_g7x_iii_flash",
            "cam_fujifilm_xe5_reala_street",
            "cam_nikon_z50_ii_street",
            "cam_om_system_om5_ii_wild",
            "cam_lumix_g97_hybrid_doc",
            "cam_sony_a7c_ii_cinetone",
        ]
        for pkey in preset_keys:
            self.assertIn(pkey, CAMERA_PRESETS, f"Missing preset {pkey} in CAMERA_PRESETS")
            preset = CAMERA_PRESETS[pkey]
            self.assertIn(preset["profile"], self.NEW_CAMERAS)
            self.assertTrue(preset["lens"])
            self.assertTrue(preset["aperture"])
            self.assertTrue(preset["subject"])
            self.assertTrue(preset["mood"])

    def test_compiler_compiles_all_new_cameras_across_all_8_models(self):
        """Verify compilation runs without error across all 8 target engines for each new camera."""
        compiler = OpticalCompiler()
        all_targets = [
            TargetEngine.MIDJOURNEY,
            TargetEngine.FLUX,
            TargetEngine.FIREFLY,
            TargetEngine.SDXL,
            TargetEngine.IMAGEN,
            TargetEngine.GPT_IMAGES,
            TargetEngine.RUNWAY,
            TargetEngine.HUMAIN,
        ]

        for cam in self.NEW_CAMERAS:
            compiler = OpticalCompiler(profile=cam)
            scene = SceneInput(
                subject="Test subject in authentic environment",
                aperture="f/4.0",
                framing="medium portrait",
                environment="urban street",
                mood="high acutance, authentic optical capture",
            )
            for target in all_targets:
                result = compiler.compile(scene, target=target)
                self.assertTrue(result.positive_prompt, f"Failed compilation for {cam} on {target.value}")
                self.assertEqual(result.target_engine, target)
                if target == TargetEngine.MIDJOURNEY:
                    self.assertIn("--ar", result.positive_prompt)
                elif target == TargetEngine.SDXL:
                    self.assertIsNotNone(result.negative_prompt)

    def test_ai_rig_advisor_specs_and_display_names(self):
        """Verify AI Rig Advisor contains valid hardware specs and display names for all 6 cameras."""
        for cam in self.NEW_CAMERAS:
            self.assertIn(cam, PROFILE_DISPLAY_NAMES, f"Missing display name for {cam}")
            self.assertTrue(PROFILE_DISPLAY_NAMES[cam])

            self.assertIn(cam, DEFAULT_HARDWARE_SPECS, f"Missing hardware specs for {cam}")
            spec = DEFAULT_HARDWARE_SPECS[cam]
            self.assertIn("lens", spec)
            self.assertIn("aperture", spec)
            self.assertIn("dof", spec)
            self.assertIn("lighting_key", spec)
            self.assertIn("medium_type", spec)

    def test_ai_rig_advisor_recommendations(self):
        """Verify AI Rig Advisor recommends the new cameras when given targeted scene prompts."""
        advisor_queries = [
            ("casual friends laughing over yakitori direct flash snapshot in shinjuku", "canon_powershot_g7x_iii"),
            ("gion kyoto reala ace film simulation street walk", "fujifilm_x_e5"),
            ("hiking through misty alpine rainforest waterfall moss", "om_system_om5_ii"),
            ("milan street fashion stylist tailored blazer s-cinetone", "sony_a7c_ii"),
        ]

        for prompt, expected_cam in advisor_queries:
            recs = PromptIntelligenceEngine.recommend_rigs(prompt, num_recommendations=3)
            self.assertEqual(len(recs), 3)
            recommended_profiles = [r.profile_id for r in recs]
            self.assertIn(
                expected_cam,
                recommended_profiles,
                f"Expected {expected_cam} in recommendations for '{prompt}', got: {recommended_profiles}",
            )

    def test_web_ui_has_new_camera_options_and_presets(self):
        """Verify web.py contains HTML select options and JavaScript presets for all 6 cameras."""
        web_file = Path(__file__).resolve().parent.parent / "optical_compiler" / "web.py"
        with open(web_file, "r", encoding="utf-8") as f:
            content = f.read()

        # HTML options check
        expected_options = [
            'value="cam_canon_g7x_iii_flash"',
            'value="cam_fujifilm_xe5_reala_street"',
            'value="cam_sony_a7c_ii_cinetone"',
            'value="cam_nikon_z50_ii_street"',
            'value="cam_om_system_om5_ii_wild"',
            'value="cam_lumix_g97_hybrid_doc"',
        ]
        for opt in expected_options:
            self.assertIn(opt, content, f"Missing HTML option {opt} in web.py")

        # JavaScript presets check
        expected_js_presets = [
            "cam_canon_g7x_iii_flash:",
            "cam_fujifilm_xe5_reala_street:",
            "cam_sony_a7c_ii_cinetone:",
            "cam_nikon_z50_ii_street:",
            "cam_om_system_om5_ii_wild:",
            "cam_lumix_g97_hybrid_doc:",
        ]
        for js_p in expected_js_presets:
            self.assertIn(js_p, content, f"Missing JS preset {js_p} in web.py")


if __name__ == "__main__":
    unittest.main()
