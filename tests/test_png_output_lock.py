"""Tests for Universal High-Resolution PNG Output Lock v1.0 and 4X Upscale Workflow."""

import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from optical_compiler import (
    HighResPNGOutputLockSpec,
    OpticalCompiler,
    PNGUpscaleReport,
    ReferenceImageInput,
    ReferenceMode,
    SceneInput,
    TargetEngine,
    compile_scene,
    execute_4x_full_color_png_upscale,
)
from optical_compiler.cli import main, png_lock_main
from optical_compiler.comfy_nodes import Optical4XFullColorPNGUpscaleNode
from optical_compiler.restoration import PILLOW_AVAILABLE
from optical_compiler.web import StudioAPIHandler

if PILLOW_AVAILABLE:
    from PIL import Image


class TestHighResPNGOutputLockModel(unittest.TestCase):
    """Test HighResPNGOutputLockSpec model and dictionary serialization."""

    def test_default_spec(self):
        spec = HighResPNGOutputLockSpec()
        self.assertEqual(spec.title, "Universal High-Resolution PNG Output Lock v1.0")
        self.assertEqual(spec.target_min_mb, 12.0)
        self.assertEqual(spec.compress_level, 0)
        self.assertFalse(spec.optimize)
        self.assertEqual(spec.unsharp_radius, 1.1)
        self.assertEqual(spec.unsharp_percent, 85)
        self.assertEqual(spec.unsharp_threshold, 3)

        d = spec.to_dict()
        self.assertEqual(d["title"], "Universal High-Resolution PNG Output Lock v1.0")
        self.assertEqual(d["export_requirements"]["format"], "PNG")
        self.assertIn("11648 x 6552", d["rendering_requirements"]["resolution_policy"]["preferred_resolutions"])
        self.assertIn("forced palette reduction", d["negative_constraints"][0])
        self.assertIn("step_3", d["delivery_workflow"])
        self.assertEqual(d["delivery_workflow"]["correction_verbiage"], spec.correction_verbiage)

    def test_reference_mode_aliases(self):
        self.assertEqual(ReferenceMode.from_string("universal_png_lock"), ReferenceMode.UNIVERSAL_PNG_LOCK)
        self.assertEqual(ReferenceMode.from_string("png_lock"), ReferenceMode.UNIVERSAL_PNG_LOCK)
        self.assertEqual(ReferenceMode.from_string("high_res_png_lock"), ReferenceMode.UNIVERSAL_PNG_LOCK)
        self.assertEqual(ReferenceMode.from_string("full_color_png"), ReferenceMode.UNIVERSAL_PNG_LOCK)
        self.assertEqual(ReferenceMode.from_string("png_output_lock"), ReferenceMode.UNIVERSAL_PNG_LOCK)

    def test_scene_input_has_png_lock(self):
        # Via explicit png_lock spec
        scene1 = SceneInput(subject="Abstract mural", png_lock=HighResPNGOutputLockSpec())
        self.assertTrue(scene1.has_png_lock)

        # Via reference mode
        ref = ReferenceImageInput(filename="art.png", mode=ReferenceMode.UNIVERSAL_PNG_LOCK)
        scene2 = SceneInput(subject="Abstract mural", reference=ref)
        self.assertTrue(scene2.has_png_lock)

        # Plain scene
        scene3 = SceneInput(subject="Landscape")
        self.assertFalse(scene3.has_png_lock)


class TestPNGOutputLockAdapters(unittest.TestCase):
    """Verify all 7 engine adapters compile PNG Output Lock directives and negative tokens."""

    def setUp(self):
        self.compiler = OpticalCompiler(profile="auto")

    def test_gpt_images_adapter_png_lock(self):
        payload = self.compiler.compile(
            "Whimsical forest of colorful shapes",
            target=TargetEngine.GPT_IMAGES,
            png_lock=True,
            png_min_mb=15.0,
        )
        self.assertIn("Universal High-Resolution PNG Output Lock Directives:", payload.positive_prompt)
        self.assertIn("15 MB", payload.positive_prompt)
        self.assertIn("forced palette reduction", payload.negative_prompt)
        self.assertIn("indexed-color PNG", payload.negative_prompt)
        self.assertTrue(payload.parameters.get("png_output_lock"))
        self.assertEqual(payload.parameters.get("compress_level"), 0)
        self.assertEqual(payload.parameters.get("color_mode"), "RGB")
        self.assertEqual(payload.parameters.get("linear_scale"), 4)

    def test_imagen_adapter_png_lock(self):
        payload = self.compiler.compile(
            "Panoramic watercolor abstract painting",
            target=TargetEngine.IMAGEN,
            png_lock=True,
        )
        self.assertIn("Universal High-Resolution PNG Output Lock v1.0", payload.positive_prompt)
        self.assertIn("forced palette reduction", payload.negative_prompt)
        self.assertIn("compression damage", payload.negative_prompt)
        self.assertTrue(payload.parameters.get("png_output_lock"))
        self.assertEqual(payload.parameters.get("compress_level"), 0)

    def test_midjourney_adapter_png_lock(self):
        payload = self.compiler.compile(
            "Panoramic watercolor abstract painting",
            target=TargetEngine.MIDJOURNEY,
            png_lock=True,
        )
        self.assertIn("Universal High-Resolution PNG Output Lock v1.0", payload.positive_prompt)
        self.assertIn("4X Lanczos upscale workflow", payload.positive_prompt)
        self.assertIn("forced palette reduction", payload.negative_prompt)
        self.assertTrue(payload.parameters.get("png_output_lock"))
        self.assertEqual(payload.parameters.get("compress_level"), 0)

    def test_flux_adapter_png_lock(self):
        payload = self.compiler.compile(
            "Panoramic watercolor abstract painting",
            target=TargetEngine.FLUX,
            png_lock=True,
        )
        self.assertIn("Universal High-Resolution PNG Output Lock v1.0", payload.positive_prompt)
        self.assertIn("zero forced palette reduction", payload.positive_prompt)
        self.assertIn("forced palette reduction", payload.negative_prompt)
        self.assertTrue(payload.parameters.get("png_output_lock"))
        self.assertEqual(payload.parameters.get("linear_scale"), 4)

    def test_sdxl_adapter_png_lock(self):
        payload = self.compiler.compile(
            "Panoramic watercolor abstract painting",
            target=TargetEngine.SDXL,
            png_lock=True,
        )
        self.assertIn("Universal High-Resolution PNG Output Lock v1.0", payload.positive_prompt)
        self.assertIn("forced palette reduction", payload.negative_prompt)
        self.assertTrue(payload.parameters.get("png_output_lock"))

    def test_raw_adapter_png_lock(self):
        payload = self.compiler.compile(
            "Panoramic watercolor abstract painting",
            target=TargetEngine.RAW,
            png_lock=True,
        )
        self.assertIn("--- Universal High-Resolution PNG Output Lock v1.0 ---", payload.positive_prompt)
        self.assertIn("Done ✅ 4× full-color PNG upscale:", payload.positive_prompt)
        self.assertIn("forced palette reduction", payload.negative_prompt)

    def test_json_prompt_adapter_png_lock(self):
        payload = self.compiler.compile(
            "Panoramic watercolor abstract painting",
            target=TargetEngine.JSON_PROMPT,
            png_lock=True,
        )
        data = json.loads(payload.positive_prompt)
        self.assertEqual(data["schema_version"], "3.7")
        self.assertTrue(data["universal_png_output_lock"]["active"])
        self.assertEqual(data["universal_png_output_lock"]["format"], "PNG")
        self.assertEqual(data["universal_png_output_lock"]["upscale_multiplier"], 4)
        self.assertIn("forced palette reduction", data["negative_shield"]["png_degradation"])

    def test_convenience_compile_scene(self):
        payload = compile_scene(
            "Panoramic abstract watercolor",
            target_model="flux",
            png_lock=True,
        )
        self.assertTrue(payload.parameters.get("png_output_lock"))


class TestMockedExecutionPipeline(unittest.TestCase):
    """Test execute_4x_full_color_png_upscale with mocked Pillow to test all logic branches."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="png_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_mocked_execution_flow(self):
        src_file = Path(self.temp_dir) / "mock_in.png"
        src_file.write_bytes(b"fake_png_bytes")

        mock_src_img = MagicMock()
        mock_src_img.size = (100, 50)
        mock_src_img.mode = "RGB"
        mock_src_img.info = {}
        mock_src_img.convert.return_value = mock_src_img

        mock_up_img = MagicMock()
        mock_up_img.size = (400, 200)
        mock_up_img.mode = "RGB"
        mock_src_img.resize.return_value = mock_up_img
        mock_up_img.filter.return_value = mock_up_img

        # When saving, write dummy file
        def fake_save(out_path, **kwargs):
            Path(out_path).write_bytes(b"x" * 1024)

        mock_up_img.save.side_effect = fake_save

        mock_pil_module = MagicMock()
        mock_pil_module.open.return_value.__enter__.side_effect = [mock_src_img, mock_up_img]
        mock_pil_module.Resampling.LANCZOS = 1

        mock_filter = MagicMock()
        mock_pil_filter = MagicMock()
        mock_pil_filter.UnsharpMask.return_value = mock_filter
        with patch("optical_compiler.restoration.PILLOW_AVAILABLE", True),              patch("optical_compiler.restoration.Image", mock_pil_module, create=True),              patch("optical_compiler.restoration.ImageFilter", mock_pil_filter, create=True):

            rep, rep_dict = execute_4x_full_color_png_upscale(
                input_path=src_file,
                min_mb=0.0001,
                generate_report=True,
            )

            self.assertTrue(rep.validation_passed)
            self.assertEqual(rep.source_dimensions, (100, 50))
            self.assertEqual(rep.output_dimensions, (400, 200))
            self.assertEqual(rep.color_mode, "RGB")
            self.assertEqual(rep.linear_multiplier, 4)
            self.assertEqual(rep.area_multiplier, 16)
            self.assertIn("Done ✅ 4× full-color PNG upscale: 400 × 200 px, RGB PNG,", rep.delivery_string)
            self.assertTrue((Path(self.temp_dir) / "PNG_UPSCALE_REPORT.md").exists())
            self.assertTrue((Path(self.temp_dir) / "PROVENANCE.json").exists())


class TestWebAPIPNGOutputLock(unittest.TestCase):
    """Test /api/png-lock-upscale and /api/compile with png_lock."""

    def test_compile_endpoint_with_png_lock(self):
        handler = object.__new__(StudioAPIHandler)
        body = {
            "scene": "Panoramic abstract art",
            "target": "gpt_images",
            "png_lock": True,
            "png_min_mb": 16.0,
        }
        body_bytes = json.dumps(body).encode("utf-8")
        handler.headers = {"Content-Length": str(len(body_bytes))}
        handler.rfile = io.BytesIO(body_bytes)

        responses = []
        handler._send_json = lambda data, status=200: responses.append((status, data))
        handler.path = "/api/compile"
        handler.do_POST()

        self.assertEqual(len(responses), 1)
        status, data = responses[0]
        self.assertEqual(status, 200)
        self.assertTrue(data["parameters"]["png_output_lock"])

    def test_png_upscale_endpoint_missing_input(self):
        handler = object.__new__(StudioAPIHandler)
        body = {"output_path": "some/out.png"}
        body_bytes = json.dumps(body).encode("utf-8")
        handler.headers = {"Content-Length": str(len(body_bytes))}
        handler.rfile = io.BytesIO(body_bytes)

        responses = []
        handler._send_json = lambda data, status=200: responses.append((status, data))
        handler.path = "/api/png-lock-upscale"
        handler.do_POST()

        self.assertEqual(len(responses), 1)
        status, data = responses[0]
        self.assertEqual(status, 400)
        self.assertIn("Missing required field", data["error"])


if __name__ == "__main__":
    unittest.main()
