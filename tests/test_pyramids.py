from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from PIL import Image

from optical_compiler.comfy_nodes import NODE_CLASS_MAPPINGS, PhotonQCLaplacianPyramidNode
from photonqc.cli import main as photonqc_cli_main
from photonqc.pyramids import (
    BURT_ADELSON_1D,
    BURT_ADELSON_2D,
    LaplacianPyramidConfig,
    build_gaussian_pyramid,
    build_laplacian_pyramid,
    evaluate_laplacian_frequency_spectrum,
    frequency_separate_portrait_lighting,
    laplacian_pyramid_antidrift_fusion,
    laplacian_pyramid_blend,
    pyr_down,
    pyr_up,
    reconstruct_from_laplacian_pyramid,
)
from photonqc.restoration import SourcePreservingRestorer


class TestLaplacianPyramidsAndFrequencySeparation(unittest.TestCase):
    """Comprehensive verification of Burt & Adelson / OpenCV 5x5 Gaussian & Laplacian Pyramids."""

    def test_burt_adelson_kernel_invariants(self) -> None:
        self.assertAlmostEqual(float(BURT_ADELSON_1D.sum()), 1.0, places=12)
        self.assertAlmostEqual(float(BURT_ADELSON_2D.sum()), 1.0, places=12)
        self.assertEqual(BURT_ADELSON_2D.shape, (5, 5))
        # Equal Contribution / Equal-Weight Parity Rule:
        # Even taps: 1/16 + 6/16 + 1/16 = 8/16 = 0.5
        # Odd taps:  4/16 + 4/16 = 8/16 = 0.5
        self.assertAlmostEqual(float(BURT_ADELSON_1D[0::2].sum()), 0.5, places=12)
        self.assertAlmostEqual(float(BURT_ADELSON_1D[1::2].sum()), 0.5, places=12)

    def test_exact_laplacian_pyramid_invertibility_even_and_odd_shapes(self) -> None:
        rng = np.random.default_rng(2026)
        for shape in [(64, 64, 3), (127, 93, 3), (105, 140, 3), (81, 79)]:
            arr = rng.uniform(0.0, 255.0, size=shape)
            lap_pyr = build_laplacian_pyramid(arr, levels=4, use_cv2=False)
            recon = reconstruct_from_laplacian_pyramid(lap_pyr, use_cv2=False)
            self.assertEqual(recon.shape, arr.shape)
            mse = float(np.mean((arr - recon) ** 2))
            self.assertLess(mse, 1e-18, f"Expected lossless invertibility for {shape}, got MSE={mse}")

    def test_seamless_multiband_laplacian_blend_reduces_seam(self) -> None:
        h, w = 128, 128
        # Left portrait lighting warm (215, 170, 145), right cool shadow (55, 75, 105)
        arr_a = np.full((h, w, 3), [215, 170, 145], dtype=np.uint8)
        arr_b = np.full((h, w, 3), [55, 75, 105], dtype=np.uint8)
        img_a = Image.fromarray(arr_a, mode="RGB")
        img_b = Image.fromarray(arr_b, mode="RGB")

        mask = np.zeros((h, w), dtype=np.float64)
        mask[:, : w // 2] = 1.0

        blended_img, meta = laplacian_pyramid_blend(img_a, img_b, mask, levels=4)
        self.assertEqual(blended_img.size, (w, h))
        self.assertGreater(meta["seam_harshness_reduction_pct"], 80.0)
        self.assertLess(meta["seam_gradient_pyramid"], meta["seam_gradient_naive"])

    def test_halo_free_portrait_frequency_separation_and_flat_black_lock(self) -> None:
        h, w = 128, 128
        arr = np.zeros((h, w, 3), dtype=np.uint8)
        # Create a synthetic portrait-like center region with dermal pore micro-texture and a sharp step edge
        yy, xx = np.ogrid[:h, :w]
        subject_mask = ((yy - 64) ** 2 + (xx - 64) ** 2) <= 40**2
        rng = np.random.default_rng(7)
        pores = rng.integers(-4, 5, size=(h, w, 3))
        skin_base = np.clip(np.array([195, 152, 132]) + pores, 0, 255).astype(np.uint8)
        arr[subject_mask] = skin_base[subject_mask]

        src_img = Image.fromarray(arr, mode="RGB")
        cfg = LaplacianPyramidConfig(
            levels=4,
            lighting_smooth_blend=0.30,
            pore_band_gain=1.12,
            meso_band_gain=1.05,
            protect_flat_black=True,
        )
        out_img, meta = frequency_separate_portrait_lighting(src_img, config=cfg)
        self.assertEqual(out_img.size, src_img.size)
        spec = meta["spectrum"]
        self.assertTrue(spec["halo_free_certified"])
        self.assertEqual(spec["reconstruction_psnr_db"], 100.0)

        # Verify flat-black border remained exact (0, 0, 0)
        out_arr = np.asarray(out_img, dtype=np.uint8)
        self.assertEqual(int(out_arr[:8, :, :].max()), 0)

    def test_laplacian_antidrift_sr_fusion_locks_low_frequency_anchor(self) -> None:
        lr = Image.new("RGB", (32, 32), (0, 0, 0))
        lr_arr = np.asarray(lr, dtype=np.uint8).copy()
        lr_arr[8:24, 8:24] = [200, 40, 40]
        lr_img = Image.fromarray(lr_arr, mode="RGB")

        # Simulate a 4x SR output that has an artificial color/exposure shift (+25 brightness) + crisp edges
        sr_anchor = lr_img.resize((128, 128), Image.Resampling.LANCZOS)
        sr_shifted_arr = np.clip(np.asarray(sr_anchor, dtype=np.int32) + 25, 0, 255).astype(np.uint8)
        sr_shifted_img = Image.fromarray(sr_shifted_arr, mode="RGB")

        fused_img, ops, spec = laplacian_pyramid_antidrift_fusion(
            lr_img,
            sr_shifted_img,
            levels=4,
            low_freq_anchor_lock=1.0,
        )
        self.assertEqual(fused_img.size, (128, 128))
        self.assertIn("low_freq_base_anchor_lock_1.00", ops)
        self.assertIn("bilateral_symmetry_multiband_lock", ops)
        self.assertTrue(spec["halo_free_certified"])

    def test_source_preserving_restorer_with_laplacian_pyramid(self) -> None:
        img = Image.new("RGB", (96, 96), (0, 0, 0))
        arr = np.asarray(img, dtype=np.uint8).copy()
        arr[20:76, 20:76] = [180, 140, 120]
        src = Image.fromarray(arr, mode="RGB")

        restorer = SourcePreservingRestorer(use_laplacian_pyramid=True, pyramid_levels=3)
        restored, ops = restorer.restore_image(src)
        self.assertEqual(restored.size, src.size)
        self.assertTrue(any("laplacian_pyramid_decompose" in op for op in ops))

    def test_comfyui_node_and_cli_integration(self) -> None:
        self.assertIn("PhotonQCLaplacianPyramid", NODE_CLASS_MAPPINGS)
        node = PhotonQCLaplacianPyramidNode()

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            in_p = tmp / "in.png"
            out_p = tmp / "out.png"
            blend_p = tmp / "blend.png"

            arr = np.full((64, 64, 3), [180, 145, 130], dtype=np.uint8)
            Image.fromarray(arr, mode="RGB").save(in_p, format="PNG")

            res_path, digest, telemetry_json, halo_free = node.execute_pyramid(
                input_path=str(in_p),
                output_path=str(out_p),
                operation_mode="frequency_separate_portrait (Halo-Free Lighting & Pore Separation)",
                pyramid_levels=3,
            )
            self.assertTrue(Path(res_path).is_file())
            self.assertEqual(len(digest), 64)
            self.assertTrue(halo_free)
            telemetry = json.loads(telemetry_json)
            self.assertIn("spectrum", telemetry)

            # Test CLI pyramid-blend
            photonqc_cli_main(
                [
                    "pyramid-blend",
                    "--image-a",
                    str(in_p),
                    "--image-b",
                    str(in_p),
                    "--output",
                    str(blend_p),
                    "--levels",
                    "3",
                ]
            )
            self.assertTrue(blend_p.is_file())

    def test_web_studio_pyramid_endpoints(self) -> None:
        try:
            from tests.test_web import TestWebStudioHandler
        except ImportError:
            from test_web import TestWebStudioHandler  # type: ignore[import-not-found]

        helper = TestWebStudioHandler()
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            in_p = tmp / "web_in.png"
            fs_out = tmp / "web_fs.png"
            pb_out = tmp / "web_pb.png"

            arr = np.full((64, 64, 3), [190, 150, 135], dtype=np.uint8)
            Image.fromarray(arr, mode="RGB").save(in_p, format="PNG")

            for endpoint, payload, expected_out in [
                (
                    "/api/photonqc/frequency-separate",
                    {"input_path": str(in_p), "output_path": str(fs_out), "levels": 3},
                    fs_out,
                ),
                (
                    "/api/photonqc/pyramid-blend",
                    {"image_a": str(in_p), "image_b": str(in_p), "output_path": str(pb_out), "levels": 3},
                    pb_out,
                ),
            ]:
                body = json.dumps(payload).encode("utf-8")
                status_code, _headers, body_bytes = helper._execute_request("POST", endpoint, body)
                self.assertEqual(status_code, 200)
                data = json.loads(body_bytes.decode("utf-8"))
                self.assertTrue(expected_out.is_file())
                self.assertEqual(len(data["output_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
