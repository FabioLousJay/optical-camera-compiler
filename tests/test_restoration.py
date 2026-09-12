"""Unit tests for PIL Conservative 102MP Restoration and Upscale Lock engine."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

from optical_compiler.restoration import (
    PILLOW_AVAILABLE,
    RestorationConfig,
    calculate_exact_ratio_102mp_dimensions,
    compute_staged_upscale_dimensions,
    restore_and_upscale_102mp,
)

if PILLOW_AVAILABLE:
    from PIL import Image


class TestRestorationMath(unittest.TestCase):
    """Test GCD rational dimension calculation and aspect ratio preservation."""

    def test_standard_aspect_ratios_exact_lock(self):
        cases = [
            (4000, 3000, 11660, 8745),  # 4:3
            (6000, 4000, 12369, 8246),  # 3:2
            (1000, 1000, 10100, 10100), # 1:1
            (1920, 1080, 13472, 7578),  # 16:9
            (900, 1100, 9135, 11165),   # 9:11
            (2560, 1080, 15552, 6561),  # 64:27 (~21:9)
        ]
        target_pixels = 102_000_000

        for w0, h0, expected_w, expected_h in cases:
            w, h, pixels, within_tol = calculate_exact_ratio_102mp_dimensions(w0, h0, target_pixels)
            # Mathematical truth: exact rational cross-multiplication
            self.assertEqual(
                w * h0,
                h * w0,
                f"Aspect ratio drifted for {w0}x{h0}: output {w}x{h}",
            )
            # Tolerance check (<= 1.5% from 102M)
            deviation = abs(pixels - target_pixels) / target_pixels
            self.assertLessEqual(
                deviation,
                0.015,
                f"Pixel count {pixels} exceeds 1.5% tolerance for {w0}x{h0}",
            )
            self.assertTrue(within_tol)
            self.assertEqual(w, expected_w)
            self.assertEqual(h, expected_h)

    def test_staged_scaling_constraints(self):
        w0, h0 = 1000, 1000
        target_w, target_h = 10100, 10100
        stages = compute_staged_upscale_dimensions(w0, h0, target_w, target_h, max_growth=2.0)
        
        self.assertTrue(len(stages) >= 3, "Staged scaling should require multiple steps for 10x upscale")
        self.assertEqual(stages[-1], (target_w, target_h), "Final stage must match exact target")
        
        prev_w = w0
        for sw, sh in stages:
            ratio = sw / prev_w
            self.assertLessEqual(ratio, 2.0001, f"Stage linear growth {ratio:.3f} exceeded 2.0x limit")
            self.assertEqual(sw * h0, sh * w0, "Intermediate stage aspect ratio drifted")
            prev_w = sw


@unittest.skipUnless(PILLOW_AVAILABLE, "Pillow is required for restoration tests")
class TestRestorationExecution(unittest.TestCase):
    """Test actual image restoration and upscale pipeline execution."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_restore_and_upscale_rgb_fast(self):
        in_path = os.path.join(self.temp_dir.name, "sample_rgb.jpg")
        out_path = os.path.join(self.temp_dir.name, "sample_out.jpg")
        
        # Create a 4:3 test image
        img = Image.new("RGB", (120, 90), color=(180, 140, 100))
        img.save(in_path, "JPEG", quality=95)

        # Use 1MP target for fast testing
        cfg = RestorationConfig(target_pixels=1_000_000, target_megapixels=1.0)
        report = restore_and_upscale_102mp(in_path, out_path, config=cfg, output_format="JPEG")

        self.assertTrue(os.path.exists(out_path))
        self.assertTrue(report["validation_passed"])
        self.assertTrue(report["exact_aspect_ratio_preserved"])
        self.assertEqual(report["output_format"], "JPEG")
        self.assertIn("1.0.0", report["version"])
        self.assertIn("PLATINUM_NO_DRIFT", report["profile"])
        self.assertEqual(len(report["validation_failures"]), 0)

        # Verify reopened image dimensions and mode
        with Image.open(out_path) as verified:
            vw, vh = verified.size
            self.assertEqual(vw * 90, vh * 120)
            self.assertEqual(verified.mode, "RGB")

    def test_restore_and_upscale_rgba_transparency(self):
        in_path = os.path.join(self.temp_dir.name, "sample_alpha.png")
        out_path = os.path.join(self.temp_dir.name, "sample_alpha_out.png")

        # Create RGBA test image with transparency
        img = Image.new("RGBA", (100, 100), color=(50, 100, 150, 180))
        img.save(in_path, "PNG")

        cfg = RestorationConfig(target_pixels=500_000, target_megapixels=0.5)
        report = restore_and_upscale_102mp(in_path, out_path, config=cfg, output_format="PNG")

        self.assertTrue(os.path.exists(out_path))
        self.assertTrue(report["validation_passed"])
        self.assertTrue(report["alpha_preserved"])
        self.assertEqual(report["output_mode"], "RGBA")

        with Image.open(out_path) as verified:
            self.assertEqual(verified.mode, "RGBA")
            self.assertEqual(verified.size, (report["output_width"], report["output_height"]))

    def test_prohibited_dependencies_lock(self):
        """Verify strict implementation lock: NO deep learning / generative libraries imported."""
        forbidden = [
            "cv2",
            "torch",
            "tensorflow",
            "basicsr",
            "gfpgan",
            "codeformer",
            "diffusers",
        ]
        for lib in forbidden:
            self.assertNotIn(
                lib,
                sys.modules,
                f"Forbidden dependency '{lib}' was loaded in violation of PIL_ONLY lock!",
            )

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            restore_and_upscale_102mp("non_existent_file_xyz123.jpg")


if __name__ == "__main__":
    unittest.main()
