"""Unit tests for the Reference Image Pipeline & Extreme Anti-Drift Engine."""

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from optical_compiler.cli import main
from optical_compiler.compiler import OpticalCompiler
from optical_compiler.models import (
    ReferenceImageInput,
    ReferenceMode,
    SceneInput,
    TargetEngine,
)
from optical_compiler.web import StudioAPIHandler


class MockSocket:
    """Mock socket for BaseHTTPRequestHandler testing."""

    def makefile(self, *args: str, **kwargs: int) -> io.BytesIO:
        return io.BytesIO()


class TestReferencePipeline(unittest.TestCase):
    """Test suite for reference image restoration, aesthetic transformation, and anti-drift parameters."""

    def setUp(self) -> None:
        self.compiler = OpticalCompiler(profile="phase_one_iq4")

    def test_flux_restore_upscale(self) -> None:
        """Verify Flux adapter in restore mode injects 1:1 identity lock and anti-drift tokens."""
        ref = ReferenceImageInput(
            filename="master_portrait.jpg",
            mode=ReferenceMode.RESTORE_UPSCALE,
            fidelity_lock=0.98,
            denoise_strength=0.35,
        )
        payload = self.compiler.compile(
            "Sculptor in atelier",
            target="flux",
            reference=ref,
        )

        self.assertEqual(payload.target_engine, TargetEngine.FLUX)
        self.assertIn("Master optical remaster", payload.positive_prompt)
        self.assertIn("1:1 biometric identity lock", payload.positive_prompt)
        self.assertIn("98% fidelity lock", payload.positive_prompt)
        self.assertIn("facial morphing", payload.negative_prompt)
        self.assertIn("identity loss", payload.negative_prompt)
        self.assertEqual(payload.parameters["reference_mode"], "restore_upscale")
        self.assertEqual(payload.parameters["denoising_strength"], 0.35)
        self.assertEqual(payload.parameters["controlnet_tile_weight"], 0.85)
        self.assertEqual(payload.metadata["reference_image"], "master_portrait.jpg")
        # Verify unified prompt includes anti-drift shield
        self.assertIn("[ANTI-ARTIFACT NEGATIVE SHIELD]:", payload.unified_prompt)
        self.assertIn("facial morphing", payload.unified_prompt)

    def test_flux_transform_adapt(self) -> None:
        """Verify Flux adapter in transform mode preserves identity anchors while adapting scene."""
        ref = ReferenceImageInput(
            filename="portrait_sample.png",
            mode=ReferenceMode.TRANSFORM_ADAPT,
            fidelity_lock=0.85,
            denoise_strength=0.65,
            preserved_elements=["facial bone structure", "eye gaze"],
        )
        payload = self.compiler.compile(
            "Architect in cyberpunk Tokyo street",
            target="flux",
            reference=ref,
        )

        self.assertIn("Photographic adaptation and contextual transformation", payload.positive_prompt)
        self.assertIn("biometric identity", payload.positive_prompt)
        self.assertIn("facial bone structure", payload.positive_prompt)
        self.assertIn("85% biometric lock", payload.positive_prompt)
        self.assertIn("Tokyo street", payload.positive_prompt)
        self.assertEqual(payload.parameters["reference_mode"], "transform_adapt")
        self.assertEqual(payload.parameters["denoising_strength"], 0.65)
        self.assertIn("facial morphing", payload.negative_prompt)

    def test_imagen_restore_and_transform(self) -> None:
        """Verify Imagen 3 adapter incorporates photographic reference prose."""
        ref_restore = ReferenceImageInput(
            filename="vintage_photo.jpg",
            mode=ReferenceMode.RESTORE_UPSCALE,
            fidelity_lock=0.95,
        )
        p_restore = self.compiler.compile("Gentleman in study", target="imagen", reference=ref_restore)
        self.assertIn("Master optical remaster and high-resolution restoration", p_restore.positive_prompt)
        self.assertIn("Strict optical preservation directive", p_restore.positive_prompt)
        self.assertIn("facial morphing", p_restore.negative_prompt)
        self.assertEqual(p_restore.parameters["reference_mode"], "restore_upscale")

        ref_transform = ReferenceImageInput(
            filename="model_face.jpg",
            mode=ReferenceMode.TRANSFORM_ADAPT,
            fidelity_lock=0.90,
        )
        p_transform = self.compiler.compile("Model on Amalfi cliff", target="imagen", reference=ref_transform)
        self.assertIn("Reference-guided photographic transformation", p_transform.positive_prompt)
        self.assertIn("Biometric anchor directive", p_transform.positive_prompt)
        self.assertIn("Amalfi cliff", p_transform.positive_prompt)
        self.assertEqual(p_transform.parameters["reference_mode"], "transform_adapt")

    def test_midjourney_reference_flags(self) -> None:
        """Verify Midjourney adapter includes --iw 2.0, --cw 100 for restore and --cref for adapt."""
        ref_restore = ReferenceImageInput(
            filename="headshot.png",
            mode=ReferenceMode.RESTORE_UPSCALE,
        )
        p_restore = self.compiler.compile("CEO portrait", target="midjourney", reference=ref_restore)
        self.assertIn("[REFERENCE_IMAGE_URL]", p_restore.positive_prompt)
        self.assertIn("--iw 2.0", p_restore.positive_prompt)
        self.assertIn("--cw 100", p_restore.positive_prompt)
        self.assertIn("facial morphing", p_restore.positive_prompt)
        self.assertEqual(p_restore.parameters["image_weight"], 2.0)

        ref_adapt = ReferenceImageInput(
            filename="subject.png",
            mode=ReferenceMode.TRANSFORM_ADAPT,
        )
        p_adapt = self.compiler.compile("Subject in Parisian cafe", target="midjourney", reference=ref_adapt)
        self.assertIn("--cref [REFERENCE_IMAGE_URL]", p_adapt.positive_prompt)
        self.assertIn("--cw 80", p_adapt.positive_prompt)
        self.assertIn("--iw 1.5", p_adapt.positive_prompt)
        self.assertEqual(p_adapt.parameters["character_weight"], 80)

    def test_sdxl_reference_parameters(self) -> None:
        """Verify SDXL adapter injects identity tokens, ControlNet weights, and anti-drift shield."""
        ref = ReferenceImageInput(
            filename="reference_source.jpg",
            mode=ReferenceMode.RESTORE_UPSCALE,
            fidelity_lock=0.95,
            denoise_strength=0.35,
        )
        payload = self.compiler.compile("Elderly fisherman", target="sdxl", reference=ref)
        self.assertIn("1:1 biometric identity lock", payload.positive_prompt)
        self.assertIn("facial morphing", payload.negative_prompt)
        self.assertIn("identity loss", payload.negative_prompt)
        self.assertEqual(payload.parameters["reference_mode"], "restore_upscale")
        self.assertEqual(payload.parameters["denoising_strength"], 0.35)
        self.assertEqual(payload.parameters["controlnet_tile_weight"], 0.85)

    def test_cli_with_reference(self) -> None:
        """Verify CLI accepts --reference, --ref-mode, and --fidelity-lock flags."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main([
                "Artisan woodcarver",
                "--ref", "artisan.jpg",
                "--ref-mode", "transform",
                "--fidelity-lock", "0.90",
                "--target", "flux",
                "--json",
            ])

        self.assertEqual(exit_code, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["parameters"]["reference_mode"], "transform_adapt")
        self.assertEqual(data["parameters"]["fidelity_lock"], "90%")
        self.assertIn("Photographic adaptation", data["positive_prompt"])
        self.assertIn("facial morphing", data["negative_prompt"])

    def test_web_api_reference_compile(self) -> None:
        """Verify Web Studio /api/compile processes reference payloads and returns anti-drift prompts."""
        request_body = {
            "scene": "Fashion model in minimalist gallery",
            "target": "imagen",
            "profile": "phase_one_iq4",
            "reference": {
                "filename": "editorial_model.jpg",
                "mode": "restore_upscale",
                "fidelity_lock": 0.95,
                "denoise_strength": 0.35,
                "preserved_elements": ["facial geometry and bone structure", "eye shape and gaze direction"],
            },
        }

        raw_req = (
            b"POST /api/compile HTTP/1.1\r\n"
            b"Host: localhost\r\n"
            b"Content-Type: application/json\r\n"
            b"Content-Length: " + str(len(json.dumps(request_body))).encode("utf-8") + b"\r\n\r\n" +
            json.dumps(request_body).encode("utf-8")
        )

        input_stream = io.BytesIO(raw_req)
        output_stream = io.BytesIO()

        handler = StudioAPIHandler.__new__(StudioAPIHandler)
        handler.rfile = input_stream
        handler.wfile = output_stream
        handler.connection = MockSocket()
        handler.client_address = ("127.0.0.1", 54321)
        handler.close_connection = False

        handler.handle_one_request()

        output_stream.seek(0)
        resp_bytes = output_stream.read()
        _, _, body_part = resp_bytes.partition(b"\r\n\r\n")
        res_data = json.loads(body_part.decode("utf-8"))

        self.assertIn("positive_prompt", res_data)
        self.assertIn("unified_prompt", res_data)
        self.assertIn("Master optical remaster", res_data["positive_prompt"])
        self.assertIn("facial morphing", res_data["unified_prompt"])
        self.assertEqual(res_data["parameters"]["reference_mode"], "restore_upscale")


if __name__ == "__main__":
    unittest.main()
