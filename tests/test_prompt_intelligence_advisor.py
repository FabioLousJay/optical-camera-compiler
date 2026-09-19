"""Tests for AI Rig Advisor & Multi-Rig Recommendation Engine with Anti-Drift & Anti-Hallucination Quality Gate."""

import json
import unittest
from unittest.mock import MagicMock

from optical_compiler.compiler import OpticalCompiler, recommend_rigs
from optical_compiler.intelligence import (
    PROHIBITED_ARTIST_NAMES,
    PROHIBITED_DEFECT_TOKENS,
    PromptIntelligenceEngine,
    QualityGateResult,
    RigRecommendation,
    SceneIntent,
)
from optical_compiler.web import HTML_TEMPLATE, StudioAPIHandler


class TestPromptIntelligenceAdvisor(unittest.TestCase):
    """Test suite for PromptIntelligenceEngine, Anti-Drift/Anti-Hallucination Quality Gate, Web API, and CLI."""

    def test_intent_extraction_genres(self):
        """Verify intent parsing correctly identifies primary genre and flags across diverse scene inputs."""
        # 1. Wildlife
        intent_wildlife = PromptIntelligenceEngine.extract_intent("A cheetah sprinting across the Serengeti savannah at sunset")
        self.assertEqual(intent_wildlife.primary_genre, "wildlife")
        self.assertTrue(intent_wildlife.is_action_intent)
        self.assertIn("cheetah", intent_wildlife.subject_entities)
        self.assertIn("sprinting", intent_wildlife.subject_entities)

        # 2. Macro
        intent_macro = PromptIntelligenceEngine.extract_intent("Extreme macro close-up of dewdrop on an orchid petal with visible micro-relief")
        self.assertEqual(intent_macro.primary_genre, "macro_detail")
        self.assertTrue(intent_macro.is_macro_intent)
        self.assertEqual(intent_macro.depth_scale, "extreme_macro")

        # 3. Architecture
        intent_arch = PromptIntelligenceEngine.extract_intent("Brutalist concrete architecture museum rotunda with soaring fluted columns")
        self.assertEqual(intent_arch.primary_genre, "architecture")
        self.assertIn("rotunda", intent_arch.environment_cues)

        # 4. Cinema
        intent_cine = PromptIntelligenceEngine.extract_intent("Cinematic movie scene still of detective in dark rainy alleyway with anamorphic streak flares")
        self.assertEqual(intent_cine.primary_genre, "cinema")
        self.assertTrue(intent_cine.is_cinematic_intent)

        # 5. Monochrome Street
        intent_street = PromptIntelligenceEngine.extract_intent("Black and white street candid in Tokyo Shinjuku with reflective puddles")
        self.assertEqual(intent_street.primary_genre, "street")
        self.assertTrue(intent_street.is_monochrome_intent)

    def test_top_3_recommendations_diversity_and_ranking(self):
        """Verify engine always returns 3 distinct, ranked tiers with complete optical packages."""
        prompt = "A master watchmaker assembling gears under raking afternoon light in a Zurich workshop"
        recs = PromptIntelligenceEngine.recommend_rigs(prompt, num_recommendations=3)

        self.assertEqual(len(recs), 3)

        # Ranks must be 1, 2, 3
        self.assertEqual(recs[0].rank, 1)
        self.assertEqual(recs[1].rank, 2)
        self.assertEqual(recs[2].rank, 3)

        # Tier names must be explicit
        self.assertIn("1st Best", recs[0].tier_name)
        self.assertIn("2nd Best", recs[1].tier_name)
        self.assertIn("3rd Best", recs[2].tier_name)

        # Profile IDs must be distinct
        profile_ids = [r.profile_id for r in recs]
        self.assertEqual(len(set(profile_ids)), 3, "All 3 recommended profiles must be distinct systems")

        # All required optical fields must be present and non-empty
        for r in recs:
            self.assertTrue(r.camera_name, "Camera name must not be empty")
            self.assertTrue(r.lens, "Lens must not be empty")
            self.assertTrue(r.aperture, "Aperture must not be empty")
            self.assertTrue(r.depth_of_field, "Depth of field must not be empty")
            self.assertTrue(r.lighting, "Lighting must not be empty")
            self.assertTrue(r.aspect_ratio, "Aspect ratio must not be empty")
            self.assertTrue(r.enhanced_scene, "Enhanced scene prompt must not be empty")
            self.assertTrue(r.rationale, "Technical rationale must not be empty")
            self.assertIsNotNone(r.quality_gate, "Quality gate result must be present")
            self.assertTrue(r.quality_gate.passed, f"Quality gate must pass for {r.camera_name}")

    def test_anti_drift_quality_gate_preservation(self):
        """Verify quality gate guarantees 100% entity and intent recall."""
        user_prompt = "Elderly watchmaker working on vintage pocket watch gears"
        intent = PromptIntelligenceEngine.extract_intent(user_prompt)
        enhanced = PromptIntelligenceEngine.enhance_scene_prompt(user_prompt, intent, "phase_one_iq4", tier=1)

        qgate = PromptIntelligenceEngine.verify_quality_gate(
            user_prompt=user_prompt,
            enhanced_scene=enhanced,
            camera_name="Phase One XF IQ4 150MP",
            lens="Schneider Kreuznach 110mm LS f/2.8 Blue Ring",
            aperture="f/8.0",
            lighting="Studio Strobe",
            profile_id="phase_one_iq4",
        )

        self.assertTrue(qgate.passed)
        self.assertGreaterEqual(qgate.anti_drift_score, 99.0)
        self.assertEqual(len(qgate.missing_entities), 0)
        self.assertIn("watchmaker", qgate.preserved_entities)
        self.assertIn("gears", qgate.preserved_entities)

        # Test drift detection if scene text completely omits user intent
        hallucinated_scene = "A spaceship floating in deep space near a nebula"
        drift_gate = PromptIntelligenceEngine.verify_quality_gate(
            user_prompt=user_prompt,
            enhanced_scene=hallucinated_scene,
            camera_name="Phase One XF IQ4 150MP",
            lens="Schneider Kreuznach 110mm LS f/2.8 Blue Ring",
            aperture="f/8.0",
            lighting="Studio Strobe",
            profile_id="phase_one_iq4",
        )
        self.assertFalse(drift_gate.passed, "Quality gate must fail when semantic drift occurs")
        self.assertLess(drift_gate.anti_drift_score, 50.0)
        self.assertGreater(len(drift_gate.missing_entities), 0)

    def test_anti_hallucination_zero_artist_compliance(self):
        """Verify quality gate strictly flags and rejects artist and photographer names."""
        clean_prompt = "A high-fashion portrait in Paris"
        intent = PromptIntelligenceEngine.extract_intent(clean_prompt)
        enhanced_clean = PromptIntelligenceEngine.enhance_scene_prompt(clean_prompt, intent, "phase_one_iq4", tier=1)

        clean_gate = PromptIntelligenceEngine.verify_quality_gate(
            user_prompt=clean_prompt,
            enhanced_scene=enhanced_clean,
            camera_name="Phase One XF IQ4 150MP",
            lens="Schneider Kreuznach 110mm LS f/2.8 Blue Ring",
            aperture="f/8.0",
            lighting="Studio Strobe",
            profile_id="phase_one_iq4",
        )
        self.assertTrue(clean_gate.zero_artist_verified)
        self.assertEqual(len(clean_gate.detected_artists), 0)

        # Injected famous photographer
        polluted_scene = f"{enhanced_clean} in the style of Annie Leibovitz and Peter Lindbergh"
        polluted_gate = PromptIntelligenceEngine.verify_quality_gate(
            user_prompt=clean_prompt,
            enhanced_scene=polluted_scene,
            camera_name="Phase One XF IQ4 150MP",
            lens="Schneider Kreuznach 110mm LS f/2.8 Blue Ring",
            aperture="f/8.0",
            lighting="Studio Strobe",
            profile_id="phase_one_iq4",
        )
        self.assertFalse(polluted_gate.zero_artist_verified)
        self.assertFalse(polluted_gate.passed)
        self.assertIn("annie leibovitz", polluted_gate.detected_artists)
        self.assertIn("peter lindbergh", polluted_gate.detected_artists)

    def test_anti_hallucination_defect_free_check(self):
        """Verify quality gate rejects prohibited render defect tokens."""
        clean_prompt = "Portrait of a musician"
        intent = PromptIntelligenceEngine.extract_intent(clean_prompt)
        enhanced_with_defect = "Portrait of a musician with bad face and ugly hands"

        defect_gate = PromptIntelligenceEngine.verify_quality_gate(
            user_prompt=clean_prompt,
            enhanced_scene=enhanced_with_defect,
            camera_name="Phase One XF IQ4 150MP",
            lens="Schneider Kreuznach 110mm LS f/2.8 Blue Ring",
            aperture="f/8.0",
            lighting="Studio Strobe",
            profile_id="phase_one_iq4",
        )
        self.assertFalse(defect_gate.negative_shield_safe)
        self.assertFalse(defect_gate.passed)

    def test_compiler_recommend_rigs_integration(self):
        """Verify OpticalCompiler.recommend_rigs and module helper return valid recommendations."""
        recs = OpticalCompiler.recommend_rigs("A brutalist museum rotunda with natural light")
        self.assertEqual(len(recs), 3)
        self.assertEqual(recs[0].rank, 1)

        # Test module helper
        recs_helper = recommend_rigs("A brutalist museum rotunda with natural light")
        self.assertEqual(len(recs_helper), 3)
        self.assertEqual(recs_helper[0].profile_id, recs[0].profile_id)

    def test_web_api_recommend_rigs_endpoint(self):
        """Verify Web Studio POST /api/recommend-rigs handles requests and returns 3-tier JSON."""
        handler = StudioAPIHandler.__new__(StudioAPIHandler)
        handler.headers = {"Content-Length": "100"}
        handler.path = "/api/recommend-rigs"

        body_data = json.dumps({
            "prompt": "An elegant fashion editorial model in Milan portico",
            "target": "flux",
            "num_recommendations": 3,
        }).encode("utf-8")

        mock_rfile = MagicMock()
        mock_rfile.read.return_value = body_data
        handler.rfile = mock_rfile
        handler.headers["Content-Length"] = str(len(body_data))

        sent_payload = {}
        def fake_send_json(data, status=200):
            sent_payload["data"] = data
            sent_payload["status"] = status

        handler._send_json = fake_send_json
        handler.do_POST()

        self.assertEqual(sent_payload.get("status"), 200)
        resp = sent_payload["data"]
        self.assertIn("recommendations", resp)
        self.assertEqual(len(resp["recommendations"]), 3)
        self.assertEqual(resp["recommendations"][0]["rank"], 1)
        self.assertTrue(resp["recommendations"][0]["quality_gate"]["passed"])

    def test_web_ui_placement_before_camera_style(self):
        """Verify Web Studio HTML places 'Your Prompt' immediately before 'Camera Style' in scenario bar."""
        html = HTML_TEMPLATE

        # 1. HTML must contain the scenario prompt advisor group and input
        self.assertIn('class="scenario-prompt-advisor-group"', html)
        self.assertIn('id="scenarioPromptInput"', html)
        self.assertIn('id="btnRunAdvisor"', html)
        self.assertIn('id="rigAdvisorContainer"', html)
        self.assertIn('id="advisorCardsContainer"', html)

        # 2. Strict placement check: 'Your Prompt' MUST appear BEFORE 'Camera Style'
        advisor_index = html.find('scenario-prompt-advisor-group')
        camera_style_index = html.find('id="cameraPresetSelect"')
        self.assertNotEqual(advisor_index, -1, "scenario-prompt-advisor-group not found in HTML")
        self.assertNotEqual(camera_style_index, -1, "cameraPresetSelect not found in HTML")
        self.assertLess(
            advisor_index,
            camera_style_index,
            "CRITICAL REQUIREMENT: 'Your Prompt' (AI Rig Advisor) MUST be placed BEFORE 'Camera Style' in scenario bar",
        )

    def test_cli_recommend_command(self):
        """Verify CLI recommend subcommand produces formatted output."""
        from io import StringIO
        import sys

        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            from optical_compiler.cli import main
            ret = main(["recommend", "A master watchmaker assembling gears"])
            self.assertEqual(ret, 0)
            output = out.getvalue()
            self.assertIn("OPTICAL CAMERA COMPILER // AI RIG ADVISOR", output)
            self.assertIn("[1st Best (Primary Optical Master)]", output)
            self.assertIn("[2nd Best (Distinct Aesthetic)]", output)
            self.assertIn("[3rd Best (High-Character / Creative Rig)]", output)
            self.assertIn("Quality Gate:", output)
        finally:
            sys.stdout = saved_stdout


if __name__ == "__main__":
    unittest.main()
