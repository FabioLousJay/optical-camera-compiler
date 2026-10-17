"""Comprehensive unit, regression, and acceptance-matrix tests for PhotonQC / PhotoPipe Lab.

Compatible with both `pytest` (`python -m pytest -q`) and `unittest` (`python -m unittest discover -s tests`).
"""

from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
import pytest
from PIL import Image, ImageCms

from photopipe.cli import main
from photopipe.sizing import (
    PrintSpec,
    apply_crop_or_pad,
    check_aspect_ratio,
    inches_to_pixels,
    resolve_target_dimensions,
    validate_input_security,
)
from photonqc.assets import generate_rights_cleared_heart_example
from photonqc.benchmark import DegradationSpec, run_benchmark
from photonqc.calibration import (
    apply_output_sharpening,
    create_srgb_icc_bytes,
    evaluate_series_cohesion,
    load_print_profile,
    soft_proof_icc,
)
from photonqc.evaluation import (
    compute_edge_fidelity,
    compute_psnr,
    compute_ssim,
    evaluate_flat_black_background,
    evaluate_heart_gold_case,
    evaluate_pair,
)
from photonqc.licensing import verify_model_license
from photonqc.report import sha256
from photonqc.restoration import restore_source_locked


# ==============================================================================
# Section 6 Authoritative Seed Tests (Pytest Function Style)
# ==============================================================================


def test_print_geometry():
    assert inches_to_pixels(PrintSpec(Decimal("16"), Decimal("24"), 300)) == (4800, 7200)
    assert inches_to_pixels(PrintSpec(Decimal("24"), Decimal("36"), 240)) == (5760, 8640)
    with pytest.raises(ValueError):
        inches_to_pixels(PrintSpec(Decimal("0"), Decimal("4"), 300))


def test_aspect_ratio_guard():
    with pytest.raises(ValueError):
        check_aspect_ratio((300, 300), (300, 500))


def test_export_verify_and_source_unchanged(tmp_path: Path):
    source = tmp_path / "input.png"
    output = tmp_path / "out.png"
    Image.new("RGB", (40, 60), (112, 45, 90)).save(source)
    before = source.read_bytes()
    main(
        [
            "export",
            "--input",
            str(source),
            "--output",
            str(output),
            "--width-in",
            "2",
            "--height-in",
            "3",
            "--ppi",
            "100",
            "--min-mib",
            "0.001",
            "--report-dir",
            str(tmp_path / "report"),
        ]
    )
    assert source.read_bytes() == before
    with Image.open(output) as image:
        assert image.size == (200, 300)
        assert abs(image.info["dpi"][0] - 100) < 0.5
    report = json.loads((tmp_path / "report" / "report.json").read_text())
    assert report["validation"] == "passed"
    assert report["sr_backend"] == "lanczos_reference_not_ai"


def test_impossible_minimum_fails_without_fake_noise(tmp_path: Path):
    source = tmp_path / "small.png"
    Image.new("RGB", (10, 10), (0, 0, 0)).save(source)
    with pytest.raises(RuntimeError, match="No lossless PNG encoding"):
        main(
            [
                "export",
                "--input",
                str(source),
                "--output",
                str(tmp_path / "x.png"),
                "--width-in",
                "1",
                "--height-in",
                "1",
                "--ppi",
                "10",
                "--min-mib",
                "8",
            ]
        )


# ==============================================================================
# Section 15 Acceptance Matrix & Full PhotonQC Suite (Unittest + Pytest Compatible)
# ==============================================================================


class TestPhotonQCAcceptanceMatrix(unittest.TestCase):
    """Verifies all gates in Section 15 of ANTIGRAVITY_PHOTOGRAPHY_AI_PIPELINE_MASTER_HANDOFF.md."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_seed_contracts_in_unittest(self) -> None:
        test_print_geometry()
        test_aspect_ratio_guard()
        s1 = self.tmp_path / "seed1"
        s2 = self.tmp_path / "seed2"
        s1.mkdir(parents=True, exist_ok=True)
        s2.mkdir(parents=True, exist_ok=True)
        test_export_verify_and_source_unchanged(s1)
        test_impossible_minimum_fails_without_fake_noise(s2)

    def test_exact_pixel_mode_and_mutual_exclusion(self) -> None:
        self.assertEqual(resolve_target_dimensions(width_px=4000, height_px=6000, ppi=300), (4000, 6000))
        with self.assertRaises(ValueError):
            resolve_target_dimensions(
                width_in=Decimal("16"),
                height_in=Decimal("24"),
                width_px=4000,
                height_px=6000,
            )
        with self.assertRaises(ValueError):
            resolve_target_dimensions()

    def test_crop_and_pad_policies(self) -> None:
        sq = Image.new("RGB", (300, 300), (120, 40, 60))
        with self.assertRaises(ValueError):
            apply_crop_or_pad(sq, (200, 300), policy="reject")

        cropped, rec_crop = apply_crop_or_pad(sq, (200, 300), policy="center-crop")
        self.assertEqual(cropped.size, (200, 300))
        self.assertIn("explicit_center_crop", rec_crop)

        padded, rec_pad = apply_crop_or_pad(sq, (200, 300), policy="pad-black")
        self.assertEqual(padded.size, (300, 450))
        self.assertIn("explicit_pad_black", rec_pad)

    def test_alpha_input_rejected_explicitly(self) -> None:
        rgba_src = self.tmp_path / "alpha.png"
        Image.new("RGBA", (100, 150), (255, 0, 0, 128)).save(rgba_src)
        with self.assertRaises(ValueError):
            main(
                [
                    "export",
                    "--input",
                    str(rgba_src),
                    "--output",
                    str(self.tmp_path / "out.png"),
                    "--width-px",
                    "200",
                    "--height-px",
                    "300",
                ]
            )

    def test_source_overwrite_refused_and_security_limit(self) -> None:
        src = self.tmp_path / "same.png"
        Image.new("RGB", (50, 50), (10, 20, 30)).save(src)
        with self.assertRaises(ValueError):
            main(
                [
                    "export",
                    "--input",
                    str(src),
                    "--output",
                    str(src),
                    "--width-px",
                    "100",
                    "--height-px",
                    "100",
                ]
            )
        with self.assertRaises(ValueError):
            validate_input_security(src, max_pixels=100)

    def test_realesrgan_missing_weights_never_falls_back_to_lanczos(self) -> None:
        src = self.tmp_path / "rgb.png"
        Image.new("RGB", (40, 60), (80, 90, 100)).save(src)
        with self.assertRaises(ValueError):
            main(
                [
                    "export",
                    "--input",
                    str(src),
                    "--output",
                    str(self.tmp_path / "sr.png"),
                    "--width-px",
                    "160",
                    "--height-px",
                    "240",
                    "--backend",
                    "realesrgan",
                ]
            )

    def test_realesrgan_subprocess_adapter_and_4x_ceiling(self) -> None:
        src = self.tmp_path / "in.png"
        Image.new("RGB", (30, 45), (180, 30, 40)).save(src)

        fake_repo = self.tmp_path / "Real-ESRGAN"
        fake_repo.mkdir()
        weights = fake_repo / "RealESRGAN_x4plus.pth"
        weights.write_bytes(b"verified_mock_checkpoint_weights")

        script = fake_repo / "inference_realesrgan.py"
        script.write_text(
            "import argparse\n"
            "from pathlib import Path\n"
            "from PIL import Image\n"
            "p = argparse.ArgumentParser()\n"
            "p.add_argument('-i', required=True)\n"
            "p.add_argument('-o', required=True)\n"
            "p.add_argument('-n')\n"
            "p.add_argument('--model_path')\n"
            "p.add_argument('--outscale', type=int, default=4)\n"
            "p.add_argument('--suffix', default='sr')\n"
            "p.add_argument('--ext', default='png')\n"
            "p.add_argument('--fp32', action='store_true')\n"
            "args = p.parse_args()\n"
            "inp = Path(args.i)\n"
            "with Image.open(inp) as im:\n"
            "    out = im.resize((im.width * 4, im.height * 4))\n"
            "    out.save(Path(args.o) / f'{inp.stem}_{args.suffix}.{args.ext}')\n",
            encoding="utf-8",
        )

        # Requesting > 4x must fail with explicit error
        with self.assertRaises(ValueError):
            main(
                [
                    "export",
                    "--input",
                    str(src),
                    "--output",
                    str(self.tmp_path / "too_big.png"),
                    "--width-px",
                    "200",
                    "--height-px",
                    "300",
                    "--backend",
                    "realesrgan",
                    "--realesrgan-repo",
                    str(fake_repo),
                    "--weights",
                    str(weights),
                ]
            )

        # Requesting 100x150 (within 4x of 30x45 = 120x180) must record native 120x180 + final_lanczos_True
        out_sr = self.tmp_path / "sr_100x150.png"
        rep_dir = self.tmp_path / "sr_rep"
        main(
            [
                "export",
                "--input",
                str(src),
                "--output",
                str(out_sr),
                "--width-px",
                "100",
                "--height-px",
                "150",
                "--backend",
                "realesrgan",
                "--realesrgan-repo",
                str(fake_repo),
                "--weights",
                str(weights),
                "--report-dir",
                str(rep_dir),
            ]
        )
        rep = json.loads((rep_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(rep["pixels"], [100, 150])
        self.assertEqual(
            rep["sr_backend"],
            "real_esrgan_x4plus_fp32_native_120x180_final_lanczos_True",
        )

    def test_licensing_gate(self) -> None:
        spec = verify_model_license("RealESRGAN_x4plus")
        self.assertTrue(spec.commercial_allowed)
        with self.assertRaises(PermissionError):
            verify_model_license("SUPIR", allow_non_commercial=False)
        supir_research = verify_model_license("SUPIR", allow_non_commercial=True)
        self.assertFalse(supir_research.commercial_allowed)

    def test_icc_roundtrip_and_soft_proofing(self) -> None:
        src = self.tmp_path / "icc_in.png"
        icc_bytes = create_srgb_icc_bytes()
        img = Image.new("RGB", (60, 90), (200, 40, 50))
        img.save(src, format="PNG", icc_profile=icc_bytes, dpi=(300, 300))

        # 1. Without destination ICC -> planning_only_no_measured_icc
        plan_proof = soft_proof_icc(img, destination_icc_path=None, source_icc_bytes=icc_bytes)
        self.assertEqual(plan_proof["calibration_mode"], "planning_only_no_measured_icc")
        self.assertFalse(plan_proof["icc_soft_proof_executed"])

        # 2. With real destination ICC file -> color_managed_icc_cmm via LittleCMS2
        dst_icc_file = self.tmp_path / "dest_srgb.icc"
        dst_icc_file.write_bytes(icc_bytes)
        cmm_proof = soft_proof_icc(img, destination_icc_path=dst_icc_file, source_icc_bytes=icc_bytes)
        self.assertEqual(cmm_proof["calibration_mode"], "color_managed_icc_cmm")
        self.assertTrue(cmm_proof["icc_soft_proof_executed"])
        self.assertIsNotNone(cmm_proof["rendering_intent_comparison"])

        # 3. Export preserves embedded ICC
        out = self.tmp_path / "icc_out.png"
        rep_dir = self.tmp_path / "icc_rep"
        main(
            [
                "export",
                "--input",
                str(src),
                "--output",
                str(out),
                "--width-px",
                "120",
                "--height-px",
                "180",
                "--profile",
                "matte_300ppi",
                "--output-sharpen",
                "--destination-icc",
                str(dst_icc_file),
                "--report-dir",
                str(rep_dir),
            ]
        )
        rep = json.loads((rep_dir / "report.json").read_text(encoding="utf-8"))
        self.assertTrue(rep["embedded_icc"])
        self.assertEqual(rep["calibration"]["soft_proof"]["calibration_mode"], "color_managed_icc_cmm")

    def test_evaluation_metrics_and_no_gt_honesty(self) -> None:
        cand_path = self.tmp_path / "cand.png"
        ref_path = self.tmp_path / "ref.png"
        arr = np.zeros((80, 80, 3), dtype=np.uint8)
        arr[20:60, 20:60] = [220, 30, 40]
        ref_im = Image.fromarray(arr, mode="RGB")
        ref_im.save(ref_path)

        cand_arr = arr.copy()
        cand_arr[20:60, 20:60, 0] = 215
        cand_im = Image.fromarray(cand_arr, mode="RGB")
        cand_im.save(cand_path)

        # No GT -> must return null metrics, never fabricated numbers
        no_gt = evaluate_pair(None, cand_path)
        self.assertIsNone(no_gt["psnr_db"])
        self.assertIsNone(no_gt["ssim"])
        self.assertIsNone(no_gt["lpips"])
        self.assertEqual(no_gt["notes"], "requires aligned GT")

        # Aligned GT -> valid PSNR, SSIM, and edge metrics
        with_gt = evaluate_pair(ref_path, cand_path)
        self.assertGreater(with_gt["psnr_db"], 30.0)
        self.assertGreater(with_gt["ssim"], 0.95)
        self.assertIn("edge_gradient_rmse", with_gt)

        # Flat-black border check
        fb = evaluate_flat_black_background(ref_im, border_px=10)
        self.assertTrue(fb["passed"])

    def test_source_preserving_restoration_and_benchmark(self) -> None:
        gt_path = self.tmp_path / "heart_gt.png"
        generate_rights_cleared_heart_example(gt_path, width=128, height=192)
        with Image.open(gt_path) as heart_im:
            heart_im.load()
            heart_eval = evaluate_heart_gold_case(heart_im)
            self.assertTrue(heart_eval["passed"])
            self.assertEqual(heart_eval["bilateral_symmetry_iou"], 1.0)

        rest_out = self.tmp_path / "restored.png"
        rest_rep = restore_source_locked(
            input_path=gt_path,
            output_path=rest_out,
            target_size=(256, 384),
            report_dir=self.tmp_path / "rest_rep",
        )
        self.assertEqual(rest_rep["validation"], "passed")
        self.assertEqual(rest_rep["sr_backend"], "lanczos_reference_not_ai")

        bm_dir = self.tmp_path / "bm"
        bm = run_benchmark(gt_path, bm_dir, degradation=DegradationSpec(scale_factor=4))
        self.assertTrue((bm_dir / "benchmark_report.json").is_file())
        self.assertTrue((bm_dir / "benchmark_report.md").is_file())
        self.assertTrue((bm_dir / "registered_comparison_panel.png").is_file())
        self.assertEqual(bm["methods"]["realesrgan_x4plus"]["status"], "BLOCKED")

    def test_series_cohesion(self) -> None:
        p1 = self.tmp_path / "anchor.png"
        p2 = self.tmp_path / "cohesive.png"
        p3 = self.tmp_path / "divergent.png"
        Image.new("RGB", (60, 60), (100, 100, 100)).save(p1)
        Image.new("RGB", (60, 60), (108, 108, 108)).save(p2)
        Image.new("RGB", (60, 60), (240, 240, 240)).save(p3)

        rep_pass = evaluate_series_cohesion(p1, [p2])
        self.assertTrue(rep_pass.cohesion_passed)

        rep_fail = evaluate_series_cohesion(p1, [p2, p3])
        self.assertFalse(rep_fail.cohesion_passed)

    def test_antidrift_neural_stabilizer_and_symmetry_lock(self) -> None:
        from photonqc.neural_sr import apply_antidrift_neural_stabilizer

        gt_path = self.tmp_path / "heart_sym.png"
        generate_rights_cleared_heart_example(gt_path, width=64, height=96)
        with Image.open(gt_path) as lr_im:
            lr_im.load()
            lr_src = lr_im.copy()

        # Simulate a noisy/haloed 4x GAN prediction with broken left-right symmetry and non-zero black border
        hr_base = lr_src.resize((256, 384), Image.Resampling.LANCZOS)
        gan_arr = np.asarray(hr_base, dtype=np.float32).copy()
        gan_arr[:, :128, 0] = np.clip(gan_arr[:, :128, 0] + 18.0, 0, 255)  # asymmetric GAN drift
        gan_arr[:16, :, :] = 12.0  # polluted studio black border
        sr_gan = Image.fromarray(gan_arr.astype(np.uint8))

        stabilized, ops = apply_antidrift_neural_stabilizer(lr_src, sr_gan, sr_net_img=hr_base)
        self.assertIn("bilateral_symmetry_residual_lock", ops)
        self.assertIn("flat_black_backdrop_zero_lock", ops)
        fb = evaluate_flat_black_background(stabilized, border_px=8)
        self.assertTrue(fb["passed"])
        self.assertEqual(fb["border_max_rgb"], 0)
        heart = evaluate_heart_gold_case(stabilized)
        self.assertTrue(heart["passed"])
        self.assertEqual(heart["bilateral_symmetry_iou"], 1.0)


if __name__ == "__main__":
    unittest.main()
