"""Verification suite for the 6 Sony Cinema Line full-frame camera profiles."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from optical_compiler.compiler import OpticalCompiler
from optical_compiler.comfy_nodes import RIG_NAMES, RIG_NAME_TO_ID
from optical_compiler.intelligence import (
    DEFAULT_HARDWARE_SPECS,
    PROFILE_DISPLAY_NAMES,
    PromptIntelligenceEngine,
)
from optical_compiler.models import SceneInput, TargetEngine
from optical_compiler.presets import CAMERA_PRESETS, LENS_CATALOG
from optical_compiler.profiles import (
    auto_select_profile,
    list_available_profiles,
    load_profile,
)
from optical_compiler.web import HTML_TEMPLATE

ROOT = Path(__file__).resolve().parent.parent
PROFILES_DIR = ROOT / "profiles"
PACKAGE_PROFILES_DIR = ROOT / "optical_compiler" / "profiles_data"

SONY_CINEMA_IDS = [
    "sony_fx5",
    "sony_fx3",
    "sony_fx6",
    "sony_fx9",
    "sony_burano",
    "sony_venice",
]

PRESET_FOR_PROFILE = {
    "sony_fx5": "cam_sony_fx5_open_gate",
    "sony_fx3": "cam_sony_fx3_lowlight",
    "sony_fx6": "cam_sony_fx6_docu_nd",
    "sony_fx9": "cam_sony_fx9_6k_oversample",
    "sony_burano": "cam_sony_burano_pl_ibis",
    "sony_venice": "cam_sony_venice_6k_anamorphic",
}

BANNED_NAME_TOKENS = (
    "kubrick",
    "deakins",
    "lubezki",
    "hoytema",
    "tarantino",
    "villeneuve",
    "fincher",
    "scorsese",
    "nolan",
    "wes anderson",
    "barry lyndon",
    "blade runner",
    "oppenheimer",
    "leibovitz",
    "avedon",
    "lindbergh",
    "bresson",
    "newtown",
    "newton",
)


class SonyCinemaLineSuiteTest(unittest.TestCase):
    def test_profiles_exist_and_match_package_data(self) -> None:
        available = {p["id"] for p in list_available_profiles()}
        for pid in [*SONY_CINEMA_IDS, "sony_fx_series"]:
            self.assertIn(pid, available)

        for pid in SONY_CINEMA_IDS:
            root_path = PROFILES_DIR / f"{pid}.json"
            pkg_path = PACKAGE_PROFILES_DIR / f"{pid}.json"
            self.assertTrue(root_path.is_file(), f"Missing {root_path}")
            self.assertTrue(pkg_path.is_file(), f"Missing {pkg_path}")
            self.assertEqual(root_path.read_bytes(), pkg_path.read_bytes())

            raw = json.loads(root_path.read_text(encoding="utf-8"))
            self.assertEqual(raw.get("schema_version"), "2.0")
            profile = load_profile(pid)
            self.assertEqual(profile.profile_id, pid)
            self.assertIn("Full-Frame", profile.sensor_and_optics.sensor_type)

            blob = root_path.read_text(encoding="utf-8").lower()
            for banned in BANNED_NAME_TOKENS:
                self.assertNotIn(banned, blob, f"Banned token {banned!r} in {pid}.json")

    def test_aliases_resolve_including_x3_typo_to_fx3(self) -> None:
        expected_aliases = {
            "fx5": "sony_fx5",
            "ilme_fx5": "sony_fx5",
            "sony_fx5": "sony_fx5",
            "fx3": "sony_fx3",
            "fx3a": "sony_fx3",
            "x3": "sony_fx3",
            "sony_x3": "sony_fx3",
            "fx6": "sony_fx6",
            "ilme_fx6": "sony_fx6",
            "fx9": "sony_fx9",
            "pxw_fx9": "sony_fx9",
            "burano": "sony_burano",
            "mpc_2610": "sony_burano",
            "venice": "sony_venice",
            "mpc_3610": "sony_venice",
        }
        for alias, target_id in expected_aliases.items():
            profile = load_profile(alias)
            self.assertEqual(profile.profile_id, target_id, f"Alias {alias!r} failed")

    def test_auto_select_router_and_existing_venice2_preservation(self) -> None:
        self.assertEqual(
            auto_select_profile("Netflix 5K 3:2 Open Gate scene on Sony FX5 with triple base ISO"),
            "sony_fx5",
        )
        self.assertEqual(
            auto_select_profile("Low-light street scene at ISO 12800 on Sony FX3"),
            "sony_fx3",
        )
        self.assertEqual(
            auto_select_profile("Daylight documentary with electronic variable ND on Sony FX6"),
            "sony_fx6",
        )
        self.assertEqual(
            auto_select_profile("Broadcast 6K oversampled documentary interview on Sony FX9"),
            "sony_fx9",
        )
        self.assertEqual(
            auto_select_profile("8.6K PL-mount IBIS narrative cinema shot on Sony BURANO"),
            "sony_burano",
        )
        self.assertEqual(
            auto_select_profile("Theatrical 6K Open Gate anamorphic shot on Sony VENICE"),
            "sony_venice",
        )
        # Preserve existing test_master_pro_prompts contract
        self.assertEqual(
            auto_select_profile(
                "Cinematic film still of a detective in a rain-soaked alleyway, 180-degree shutter"
            ),
            "sony_fx_series",
        )

    def test_presets_lenses_intelligence_comfy_and_web_parity(self) -> None:
        for pid in SONY_CINEMA_IDS:
            # Presets & Lenses
            self.assertIn(pid, LENS_CATALOG)
            self.assertGreaterEqual(len(LENS_CATALOG[pid]), 5)
            preset_id = PRESET_FOR_PROFILE[pid]
            self.assertIn(preset_id, CAMERA_PRESETS)
            preset = CAMERA_PRESETS[preset_id]
            self.assertEqual(preset["profile"], pid)

            preset_blob = json.dumps(preset).lower()
            for banned in BANNED_NAME_TOKENS:
                self.assertNotIn(banned, preset_blob, f"Banned token {banned!r} in {preset_id}")

            # Intelligence metadata
            self.assertIn(pid, PROFILE_DISPLAY_NAMES)
            self.assertIn(pid, DEFAULT_HARDWARE_SPECS)

            # Web UI HTML/JS parity
            self.assertIn(f'value="{preset_id}"', HTML_TEMPLATE)
            self.assertIn(f"{pid}: [", HTML_TEMPLATE)
            self.assertIn(f"{preset_id}: {{", HTML_TEMPLATE)

            # End-to-end compilation across all TargetEngine modes
            compiler = OpticalCompiler(profile=pid)
            for engine in TargetEngine:
                scene = SceneInput(
                    subject=preset["subject"],
                    lens=LENS_CATALOG[pid][0],
                    aperture=preset["aperture"],
                    aspect_ratio=preset["aspectRatio"],
                )
                compiled = compiler.compile(scene, target=engine)
                self.assertTrue(compiled.positive_prompt.strip(), f"Empty prompt for {pid} on {engine}")

        # ComfyUI node dropdown & mapping sync
        mapped_ids = set(RIG_NAME_TO_ID.values())
        for pid in SONY_CINEMA_IDS:
            self.assertIn(pid, mapped_ids)
        for rig_name, rig_id in RIG_NAME_TO_ID.items():
            if rig_id in SONY_CINEMA_IDS:
                self.assertIn(rig_name, RIG_NAMES)

        # Recommender returns Sony Cinema Line candidates for cinema queries
        recs = PromptIntelligenceEngine.recommend_rigs(
            "Sony FX5 Netflix 5K Open Gate cinema drama at blue hour",
            num_recommendations=5,
        )
        rec_ids = [r.profile_id for r in recs]
        self.assertIn("sony_fx5", rec_ids)


if __name__ == "__main__":
    unittest.main()
