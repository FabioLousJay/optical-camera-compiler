"""Tests for Professional 4X Reconstruction Lock Protocol & AI Super-Resolution Engine.

Validates:
1. SuperResolutionBackend enum parsing and aliases.
2. ReconstructionLock4XSpec dataclass defaults and to_dict serialization.
3. SceneInput.has_reconstruction_lock_4x and SceneInput.reconstruction_lock.
4. NegativeEmbeddings reconstruction drift tokens.
5. All 7 engine adapters (GPT Images, Imagen 3, Midjourney, Flux.1, SDXL, Raw, JSON Schema 3.6).
6. execute_4x_reconstruction_lock: exact 4X enlargement, sky/haze protection, SHA-256 provenance, reports.
7. Compiler top-level API kwargs and normalization.
8. CLI flags (--recon-4x, --sr-backend, etc.) and direct execution.
9. ComfyUI custom node: Optical4XReconstructionLockNode.
10. Web Studio /api/recon-4x REST endpoint.
"""

from __future__ import annotations

import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

from optical_compiler import (
    OpticalCompiler,
    ReconstructionLock4XSpec,
    ReconstructionReport,
    ReferenceImageInput,
    ReferenceMode,
    SceneInput,
    SuperResolutionBackend,
    execute_4x_reconstruction_lock,
)
from optical_compiler.cli import main, recon_4x_main
from optical_compiler.comfy_nodes import Optical4XReconstructionLockNode
from optical_compiler.models import NegativeShield
from optical_compiler.restoration import PILLOW_AVAILABLE
from optical_compiler.web import StudioAPIHandler


class TestSuperResolutionBackend(unittest.TestCase):
    """Test backend enum parsing and normalization."""

    def test_enum_values(self) -> None:
        self.assertEqual(SuperResolutionBackend.REAL_ESRNET_X4PLUS.value, "realesrnet_x4plus")
        self.assertEqual(SuperResolutionBackend.SWINIR_M_X4.value, "swinir_m_x4")
        self.assertEqual(SuperResolutionBackend.REAL_ESRGAN_X4V3.value, "realesrgan_x4v3")
        self.assertEqual(SuperResolutionBackend.REAL_ESRGAN_X4PLUS.value, "realesrgan_x4plus")
        self.assertEqual(SuperResolutionBackend.HAT_S_X4.value, "hat_s_x4")
        self.assertEqual(SuperResolutionBackend.PIL_CONSERVATIVE.value, "pil_conservative")

    def test_from_str_normalization(self) -> None:
        self.assertEqual(
            SuperResolutionBackend.from_str("RealESRNet_x4plus"),
            SuperResolutionBackend.REAL_ESRNET_X4PLUS,
        )
        self.assertEqual(
            SuperResolutionBackend.from_str("swinir"),
            SuperResolutionBackend.SWINIR_M_X4,
        )
        self.assertEqual(
            SuperResolutionBackend.from_str("realesr-general-x4v3"),
            SuperResolutionBackend.REAL_ESRGAN_X4V3,
        )
        self.assertEqual(
            SuperResolutionBackend.from_str("hat-s"),
            SuperResolutionBackend.HAT_S_X4,
        )
        self.assertEqual(
            SuperResolutionBackend.from_str("unknown_backend"),
            SuperResolutionBackend.REAL_ESRNET_X4PLUS,
        )


class TestReconstructionLock4XSpec(unittest.TestCase):
    """Test dataclass defaults, fields, and SceneInput integration."""

    def test_defaults(self) -> None:
        spec = ReconstructionLock4XSpec()
        self.assertEqual(spec.backend, SuperResolutionBackend.REAL_ESRNET_X4PLUS)
        self.assertAlmostEqual(spec.denoise_strength, 0.15)
        self.assertEqual(spec.tile_size, 256)
        self.assertEqual(spec.tile_pad, 16)
        self.assertAlmostEqual(spec.blend_ratio, 0.20)
        self.assertTrue(spec.protect_sky_haze)
        self.assertTrue(spec.anti_model_stacking)
        self.assertEqual(spec.linear_scale, 4)

    def test_to_dict(self) -> None:
        spec = ReconstructionLock4XSpec(
            backend=SuperResolutionBackend.SWINIR_M_X4,
            denoise_strength=0.10,
            blend_ratio=0.25,
        )
        d = spec.to_dict()
        self.assertEqual(d["backend"], "swinir_m_x4")
        self.assertEqual(d["denoise_strength"], 0.10)
        self.assertEqual(d["blend_ratio"], 0.25)
        self.assertEqual(d["linear_scale"], 4)
        self.assertTrue(d["anti_model_stacking"])

    def test_scene_input_has_recon_lock(self) -> None:
        scene = SceneInput(
            subject="Mountain Valley",
            reconstruction_lock=ReconstructionLock4XSpec(),
        )
        self.assertTrue(scene.has_reconstruction_lock_4x)

        ref_scene = SceneInput(
            subject="Landscape",
            reference=ReferenceImageInput(
                filename="mountain.png",
                mode=ReferenceMode.RECONSTRUCTION_LOCK_4X,
            ),
        )
        self.assertTrue(ref_scene.has_reconstruction_lock_4x)

        normal_scene = SceneInput(subject="Portrait")
        self.assertFalse(normal_scene.has_reconstruction_lock_4x)


class TestNegativeShieldReconstructionDrift(unittest.TestCase):
    """Test negative prompt tokens for reconstruction lock."""

    def test_reconstruction_drift_tokens(self) -> None:
        shield = NegativeShield()
        tokens = shield.all_tokens(include_reconstruction_drift=True)
        self.assertIn("generative hallucination", tokens)
        self.assertIn("diffusion drift", tokens)
        self.assertIn("model stacking artifacts", tokens)
        self.assertIn("sky grain", tokens)
        self.assertIn("sky halos", tokens)
        self.assertIn("atmospheric haze noise", tokens)
        self.assertIn("altered geology", tokens)

    def test_disabled_by_default(self) -> None:
        shield = NegativeShield()
        tokens = shield.all_tokens(include_reconstruction_drift=False)
        self.assertNotIn("generative hallucination", tokens)
        self.assertNotIn("model stacking artifacts", tokens)


class TestAdaptersReconstructionLock(unittest.TestCase):
    """Test all 7 adapters with 4X Reconstruction Lock enabled."""

    def setUp(self) -> None:
        self.compiler = OpticalCompiler()

    def test_gpt_images_adapter(self) -> None:
        payload = self.compiler.compile(
            "Majestic sandstone cliffs and pine forest at sunrise",
            target="gpt_images",
            reconstruction_lock=True,
            sr_backend="realesrnet_x4plus",
        )
        self.assertIn("Professional 4X Reconstruction Lock Protocol", payload.positive_prompt)
        self.assertIn("Exact 4X Linear Source-Locked Reconstruction", payload.positive_prompt)
        self.assertIn("generative hallucination", payload.negative_prompt)
        self.assertIn("model stacking artifacts", payload.negative_prompt)

    def test_imagen_adapter(self) -> None:
        payload = self.compiler.compile(
            "Majestic sandstone cliffs and pine forest at sunrise",
            target="imagen",
            reconstruction_lock=True,
            sr_backend="swinir_m_x4",
        )
        self.assertIn("Professional 4X Reconstruction Lock", payload.positive_prompt)
        self.assertIn("swinir_m_x4", payload.positive_prompt)
        self.assertIn("generative hallucination", payload.negative_prompt)

    def test_midjourney_adapter(self) -> None:
        payload = self.compiler.compile(
            "Majestic sandstone cliffs and pine forest at sunrise",
            target="midjourney",
            reconstruction_lock=True,
            reference={"filename": "canyon.png", "mode": "recon_4x"},
        )
        self.assertIn("--sref canyon.png", payload.positive_prompt)
        self.assertIn("--iw 2.0", payload.positive_prompt)
        self.assertIn("--cw 100", payload.positive_prompt)
        self.assertIn("--no", payload.positive_prompt)
        self.assertIn("generative hallucination", payload.positive_prompt)

    def test_flux_adapter(self) -> None:
        payload = self.compiler.compile(
            "Majestic sandstone cliffs and pine forest at sunrise",
            target="flux",
            reconstruction_lock=True,
            sr_backend="realesrgan_x4v3",
            sr_denoise=0.15,
            sr_blend=0.20,
        )
        self.assertIn("Professional 4X Reconstruction Lock", payload.positive_prompt)
        self.assertEqual(payload.parameters.get("reference_mode"), "reconstruction_lock_4x")
        self.assertEqual(payload.parameters.get("linear_scale"), 4)
        self.assertEqual(payload.parameters.get("backend"), "realesrgan_x4v3")
        self.assertAlmostEqual(payload.parameters.get("denoise_strength"), 0.15)
        self.assertIn("generative hallucination", payload.negative_prompt)

    def test_sdxl_adapter(self) -> None:
        payload = self.compiler.compile(
            "Majestic sandstone cliffs and pine forest at sunrise",
            target="sdxl",
            reconstruction_lock=True,
        )
        self.assertIn("Professional 4X Reconstruction Lock", payload.positive_prompt)
        self.assertEqual(payload.parameters.get("reference_mode"), "reconstruction_lock_4x")
        self.assertEqual(payload.parameters.get("linear_scale"), 4)
        self.assertIn("generative hallucination", payload.negative_prompt)

    def test_raw_adapter(self) -> None:
        payload = self.compiler.compile(
            "Majestic sandstone cliffs and pine forest at sunrise",
            target="raw",
            reconstruction_lock=True,
            sr_backend="hat_s_x4",
        )
        self.assertIn("--- Professional 4X Reconstruction Lock Protocol ---", payload.positive_prompt)
        self.assertIn("Super-Resolution Backend: hat_s_x4", payload.positive_prompt)
        self.assertIn("generative hallucination", payload.negative_prompt)

    def test_json_prompt_adapter(self) -> None:
        payload = self.compiler.compile(
            "Majestic sandstone cliffs and pine forest at sunrise",
            target="json",
            reconstruction_lock=True,
            sr_backend="realesrnet_x4plus",
        )
        data = json.loads(payload.positive_prompt)
        self.assertEqual(data["schema_version"], "3.6")
        self.assertIn("reconstruction_lock_4x", data)
        recon_dict = data["reconstruction_lock_4x"]
        self.assertEqual(recon_dict["linear_scale"], 4)
        self.assertEqual(recon_dict["backend"], "realesrnet_x4plus")
        self.assertTrue(recon_dict["anti_model_stacking"])
        self.assertIn("reconstruction_drift", data.get("negative_shield", {}))


@unittest.skipUnless(PILLOW_AVAILABLE, "Pillow is required for 4X reconstruction execution tests")
class TestExecution4XReconstructionLock(unittest.TestCase):
    """Test the Python execution engine for 4X Reconstruction Lock."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="recon_test_")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_execution_creates_4x_files_and_provenance(self) -> None:
        from PIL import Image, ImageDraw

        # Create synthetic test image (width: 120, height: 80)
        src_path = os.path.join(self.temp_dir, "test_landscape.png")
        img = Image.new("RGB", (120, 80), color=(135, 206, 235))  # sky blue
        draw = ImageDraw.Draw(img)
        # Add rock texture at bottom
        draw.rectangle([0, 50, 120, 80], fill=(139, 69, 19))
        for y in range(50, 80, 2):
            draw.line([(0, y), (120, y)], fill=(160, 82, 45), width=1)
        img.save(src_path)

        out_path = os.path.join(self.temp_dir, "reconstructed_4x.png")
        spec = ReconstructionLock4XSpec(
            backend=SuperResolutionBackend.REAL_ESRNET_X4PLUS,
            denoise_strength=0.15,
            blend_ratio=0.20,
            protect_sky_haze=True,
        )

        report, _ = execute_4x_reconstruction_lock(src_path, out_path, spec=spec)

        self.assertIsInstance(report, ReconstructionReport)
        self.assertEqual(report.original_dimensions, (120, 80))
        self.assertEqual(report.output_dimensions, (480, 320))
        self.assertEqual(report.linear_scale, 4)
        self.assertEqual(report.pixel_area_expansion, 16)
        self.assertEqual(report.output_pixels, 480 * 320)
        self.assertTrue(os.path.exists(out_path))

        # Check that TIFF and JPEG were also created
        tiff_path = os.path.join(self.temp_dir, "reconstructed_4x.tiff")
        jpeg_path = os.path.join(self.temp_dir, "reconstructed_4x.jpg")
        self.assertTrue(os.path.exists(tiff_path))
        self.assertTrue(os.path.exists(jpeg_path))

        # Check provenance JSON and Markdown report
        prov_path = os.path.join(self.temp_dir, "PROVENANCE.json")
        rep_md_path = os.path.join(self.temp_dir, "RECONSTRUCTION_REPORT.md")
        self.assertTrue(os.path.exists(prov_path))
        self.assertTrue(os.path.exists(rep_md_path))

        with open(prov_path, "r", encoding="utf-8") as f:
            pdata = json.load(f)
            self.assertEqual(pdata["pipeline"], "Professional 4X Reconstruction Lock Protocol")
            self.assertEqual(pdata["spec"]["linear_scale"], 4)
            self.assertTrue(len(pdata["source_sha256"]) == 64)
            self.assertTrue(len(pdata["output_sha256"]) == 64)

        with open(rep_md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
            self.assertIn("# Professional 4X Reconstruction Lock Report", md_content)
            self.assertIn("120 x 80", md_content)
            self.assertIn("480 x 320", md_content)
            self.assertIn("16x", md_content)
            self.assertIn("Decision Matrix", md_content)

    def test_nonexistent_image_raises_error(self) -> None:
        with self.assertRaises(FileNotFoundError):
            execute_4x_reconstruction_lock(
                os.path.join(self.temp_dir, "does_not_exist.png"),
                os.path.join(self.temp_dir, "out.png"),
            )


class TestCLIReconstructionLock(unittest.TestCase):
    """Test CLI flags and execution for 4X Reconstruction Lock."""

    def test_cli_recon_4x_flag(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main([
                "Alpine vista and pine ridges",
                "--recon-4x",
                "--sr-backend", "swinir_m_x4",
                "--sr-denoise", "0.12",
                "--sr-blend", "0.22",
                "--target", "flux",
                "--json",
            ])
        self.assertEqual(code, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["parameters"]["reference_mode"], "reconstruction_lock_4x")
        self.assertEqual(data["parameters"]["backend"], "swinir_m_x4")
        self.assertAlmostEqual(data["parameters"]["denoise_strength"], 0.12)
        self.assertAlmostEqual(data["parameters"]["blend_ratio"], 0.22)

    def test_recon_4x_main_help(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            with self.assertRaises(SystemExit) as cm:
                recon_4x_main(["--help"])
            self.assertEqual(cm.exception.code, 0)
        self.assertIn("Professional 4X Reconstruction Lock", buf.getvalue())


@unittest.skipUnless(PILLOW_AVAILABLE, "Pillow is required for 4X reconstruction execution tests")
class TestComfyNodeReconstructionLock(unittest.TestCase):
    """Test ComfyUI custom node execution."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="comfy_recon_test_")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_comfy_node_execution(self) -> None:
        from PIL import Image

        src = os.path.join(self.temp_dir, "comfy_src.png")
        img = Image.new("RGB", (64, 64), color=(100, 150, 200))
        img.save(src)

        node = Optical4XReconstructionLockNode()
        out_img, report_md = node.execute_reconstruction(
            image_path=src,
            backend="realesrnet_x4plus",
            denoise_strength=0.15,
            blend_ratio=0.20,
            protect_sky_haze="enabled",
            output_format="png",
            output_path="",
        )

        self.assertTrue(os.path.exists(out_img))
        self.assertIn("Professional 4X Reconstruction Lock Report", report_md)
        self.assertIn("256 x 256", report_md)


@unittest.skipUnless(PILLOW_AVAILABLE, "Pillow is required for 4X reconstruction execution tests")
class TestWebAPIReconstructionLock(unittest.TestCase):
    """Test /api/recon-4x and /api/compile with reconstruction lock."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="web_recon_test_")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_web_recon_4x_endpoint(self) -> None:
        from PIL import Image

        src = os.path.join(self.temp_dir, "web_src.png")
        img = Image.new("RGB", (50, 50), color=(120, 180, 220))
        img.save(src)

        handler = object.__new__(StudioAPIHandler)
        handler.headers = {"Content-Length": "100"}
        body_dict = {
            "image_path": src,
            "backend": "realesrnet_x4plus",
            "denoise_strength": 0.15,
            "blend_ratio": 0.20,
            "protect_sky_haze": True,
        }
        handler.rfile = io.BytesIO(json.dumps(body_dict).encode("utf-8"))
        handler.headers["Content-Length"] = str(len(json.dumps(body_dict)))

        responses = []

        def mock_send(data, status=200):
            responses.append((status, data))

        handler._send_json = mock_send
        handler.path = "/api/recon-4x"
        handler.do_POST()

        self.assertEqual(len(responses), 1)
        status, data = responses[0]
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["report"]["original_dimensions"], [50, 50])
        self.assertEqual(data["report"]["output_dimensions"], [200, 200])


if __name__ == "__main__":
    unittest.main()
