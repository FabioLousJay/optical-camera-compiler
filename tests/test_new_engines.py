"""Unit tests for the new photorealistic target engines:

- Adobe Firefly Image 5 / Image 4 Ultra (firefly)
- FLUX1.1 [pro] Ultra Raw (flux_raw)
- Runway Gen-4 Image (runway)
- HUMAIN Image 1 (humain)
"""

from __future__ import annotations

import json
import unittest

from optical_compiler import OpticalCompiler, TargetEngine
from optical_compiler.adapters import (
    FireflyAdapter,
    FluxRawAdapter,
    HumainAdapter,
    RunwayAdapter,
    get_adapter,
)
from optical_compiler.web import StudioAPIHandler
from tests.test_web import MockSocket


class TestNewPhotorealisticEngines(unittest.TestCase):
    """Test suite for the new top-notch photorealistic target engines."""

    def setUp(self) -> None:
        self.compiler = OpticalCompiler(profile="sony_a1_ii")

    def test_target_engine_enum_and_aliases(self) -> None:
        """Verify TargetEngine enum values and alias parsing."""
        self.assertEqual(TargetEngine.from_str("firefly"), TargetEngine.FIREFLY)
        self.assertEqual(TargetEngine.from_str("adobe_firefly"), TargetEngine.FIREFLY)
        self.assertEqual(TargetEngine.from_str("firefly5"), TargetEngine.FIREFLY)
        self.assertEqual(TargetEngine.from_str("firefly_4_ultra"), TargetEngine.FIREFLY)

        self.assertEqual(TargetEngine.from_str("flux_raw"), TargetEngine.FLUX_RAW)
        self.assertEqual(TargetEngine.from_str("flux_ultra_raw"), TargetEngine.FLUX_RAW)
        self.assertEqual(TargetEngine.from_str("flux1.1_pro_ultra_raw"), TargetEngine.FLUX_RAW)

        self.assertEqual(TargetEngine.from_str("runway"), TargetEngine.RUNWAY)
        self.assertEqual(TargetEngine.from_str("runway_gen4"), TargetEngine.RUNWAY)
        self.assertEqual(TargetEngine.from_str("gen4"), TargetEngine.RUNWAY)

        self.assertEqual(TargetEngine.from_str("humain"), TargetEngine.HUMAIN)
        self.assertEqual(TargetEngine.from_str("humain_image_1"), TargetEngine.HUMAIN)

    def test_adapter_factory(self) -> None:
        """Verify get_adapter instantiates the correct adapter classes."""
        self.assertIsInstance(get_adapter("firefly"), FireflyAdapter)
        self.assertIsInstance(get_adapter("flux_raw"), FluxRawAdapter)
        self.assertIsInstance(get_adapter("runway"), RunwayAdapter)
        self.assertIsInstance(get_adapter("humain"), HumainAdapter)

    def test_firefly_adapter_compilation(self) -> None:
        """Verify Adobe Firefly prompt compilation and properties."""
        payload = self.compiler.compile(
            scene="Editorial portrait of an architect in a brutalist pavilion",
            target="firefly",
            framing="Tight close-up",
            human_skin_realism=True,
            hand_lock=True,
        )
        self.assertEqual(payload.target_engine, TargetEngine.FIREFLY)
        self.assertIn("Style: Authentic Professional Color Photograph", payload.positive_prompt)
        self.assertIn("Sony a1 II", payload.positive_prompt)
        self.assertIn("Natural optical depth of field", payload.positive_prompt)
        self.assertIn("Natural human skin realism: visible fine pores", payload.positive_prompt)
        self.assertIn("Anatomically correct hands with exactly five distinct fingers", payload.positive_prompt)
        # Firefly does not use negative prompt channel
        self.assertEqual(payload.negative_prompt, "")
        self.assertEqual(payload.unified_prompt, payload.positive_prompt)
        self.assertEqual(payload.parameters["engine"], "Adobe Firefly Image 5 / Image 4 Ultra")

    def test_flux_raw_adapter_compilation(self) -> None:
        """Verify FLUX1.1 [pro] Ultra Raw mode compilation."""
        payload = self.compiler.compile(
            scene="Candid street portrait of a jazz musician at dusk",
            target="flux_raw",
            framing="Medium environmental portrait",
            hand_lock=True,
        )
        self.assertEqual(payload.target_engine, TargetEngine.FLUX_RAW)
        self.assertIn("Sony a1 II", payload.positive_prompt)
        self.assertIn("Captured in 16-bit raw mode", payload.positive_prompt)
        self.assertIn("zero artificial HDR tone-mapping", payload.positive_prompt)
        self.assertIn("Hands are rendered with strict anatomical fidelity", payload.positive_prompt)
        self.assertTrue(payload.parameters.get("raw"))
        self.assertIn("plastic skin", payload.negative_prompt)
        self.assertIn("synthetic skin", payload.negative_prompt)

    def test_runway_adapter_compilation(self) -> None:
        """Verify Runway Gen-4 Image cinematic compilation."""
        payload = self.compiler.compile(
            scene="Astronaut gazing at distant nebula through observation cupola",
            target="runway",
            framing="Wide anamorphic establishing shot",
            anamorphic=True,
            film_stock="Kodak Vision3 500T",
        )
        self.assertEqual(payload.target_engine, TargetEngine.RUNWAY)
        self.assertIn("Cinematic motion picture still", payload.positive_prompt)
        self.assertIn("anamorphic optics", payload.positive_prompt)
        self.assertIn("Kodak Vision3 500T", payload.positive_prompt)
        self.assertIn("CGI look", payload.negative_prompt)
        self.assertEqual(payload.parameters["engine"], "Runway Gen-4 Image")

    def test_humain_adapter_compilation(self) -> None:
        """Verify HUMAIN Image 1 biometric human portraiture compilation."""
        payload = self.compiler.compile(
            scene="Grandmother smiling gently by a kitchen window",
            target="humain",
            framing="Intimate macro portrait",
            hand_lock=True,
        )
        self.assertEqual(payload.target_engine, TargetEngine.HUMAIN)
        self.assertIn("Forensic human portrait photography", payload.positive_prompt)
        self.assertIn("Skin micro-topography: authentic human epidermis", payload.positive_prompt)
        self.assertIn("delicate vellus facial hair", payload.positive_prompt)
        self.assertIn("Eyes: crisp iris fibril detail", payload.positive_prompt)
        self.assertIn("Hands: strictly five anatomically correct", payload.positive_prompt)
        self.assertIn("uncanny valley", payload.negative_prompt)
        self.assertIn("doll skin", payload.negative_prompt)
        self.assertEqual(payload.parameters["engine"], "HUMAIN Image 1")

    def test_json_all_in_one_includes_new_engines(self) -> None:
        """Verify that JSON All-in-One prompt bundle contains prompts for all new engines."""
        payload = self.compiler.compile(
            scene="Portrait of a watchmaker at workbench",
            target="json",
        )
        data = json.loads(payload.positive_prompt)
        compiled_prompts = data["compiled_prompts"]

        self.assertIn("adobe_firefly_5", compiled_prompts)
        self.assertIn("flux_ultra_raw", compiled_prompts)
        self.assertIn("runway_gen4", compiled_prompts)
        self.assertIn("humain_image_1", compiled_prompts)

        self.assertIn("Style: Authentic Professional Color Photograph", compiled_prompts["adobe_firefly_5"])
        self.assertIn("Captured in 16-bit raw mode", compiled_prompts["flux_ultra_raw"])
        self.assertIn("Cinematic motion picture still", compiled_prompts["runway_gen4"])
        self.assertIn("Forensic human portrait photography", compiled_prompts["humain_image_1"])

    def test_web_studio_renders_new_engine_tabs(self) -> None:
        """Verify Web Studio UI root contains tabs for Firefly, FLUX Ultra Raw, Runway, and HUMAIN."""
        import io
        raw_request = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
        input_stream = io.BytesIO(raw_request)
        output_stream = io.BytesIO()

        handler = StudioAPIHandler.__new__(StudioAPIHandler)
        handler.rfile = input_stream
        handler.wfile = output_stream
        handler.connection = MockSocket()
        handler.client_address = ("127.0.0.1", 54321)
        handler.server = unittest.mock.MagicMock()
        handler.close_connection = False

        handler.handle_one_request()

        output_stream.seek(0)
        raw_response = output_stream.read()
        html = raw_response.decode("utf-8")

        self.assertIn("setTarget('firefly')", html)
        self.assertIn("Adobe Firefly 5", html)
        self.assertIn("setTarget('flux_raw')", html)
        self.assertIn("FLUX1.1 Ultra Raw", html)
        self.assertIn("setTarget('runway')", html)
        self.assertIn("Runway Gen-4", html)
        self.assertIn("setTarget('humain')", html)
        self.assertIn("HUMAIN Image 1", html)


if __name__ == "__main__":
    unittest.main()
