"""CLI: python -m photonqc [export|inspect|restore|evaluate|benchmark|calibrate] ...
Also exposed as `photopipe` and `photonqc` console scripts.
"""

from __future__ import annotations

import argparse
from decimal import Decimal
import json
from pathlib import Path
from PIL import Image

from .backends import render, render_with_provenance
from .benchmark import DegradationSpec, run_benchmark
from .calibration import (
    apply_output_sharpening,
    evaluate_series_cohesion,
    inspect_icc_profile,
    load_print_profile,
    soft_proof_icc,
    viewing_distance_for_print,
)
from .evaluation import evaluate_flat_black_background, evaluate_heart_gold_case, evaluate_pair
from .export import save_png_verified
from .report import sha256, verify_and_report
from .restoration import SourcePreservingRestorer, restore_source_locked
from .sizing import (
    PrintSpec,
    apply_crop_or_pad,
    check_aspect_ratio,
    inches_to_pixels,
    resolve_target_dimensions,
    validate_input_security,
)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="photopipe",
        description="PhotonQC / PhotoPipe Lab: Constraint-validated AI photography & print export engine",
    )
    sub = parser.add_subparsers(dest="operation", required=True)

    # 1. export
    exp = sub.add_parser("export", help="Generate validated print-calibrated or exact-pixel PNG")
    exp.add_argument("--input", type=Path, required=True)
    exp.add_argument("--output", type=Path, required=True)
    exp.add_argument("--width-in", type=Decimal, default=None, help="Physical print width in inches")
    exp.add_argument("--height-in", type=Decimal, default=None, help="Physical print height in inches")
    exp.add_argument("--width-px", type=int, default=None, help="Exact target pixel width (mutually exclusive with --width-in)")
    exp.add_argument("--height-px", type=int, default=None, help="Exact target pixel height (mutually exclusive with --height-in)")
    exp.add_argument("--ppi", type=int, default=300)
    exp.add_argument("--min-mib", type=float, default=0.0)
    exp.add_argument("--max-mib", type=float, default=None)
    exp.add_argument(
        "--backend",
        choices=("lanczos", "realesrgan", "realesrgan_native", "realesrgan_antidrift"),
        default="lanczos",
    )
    exp.add_argument("--realesrgan-repo", type=Path, default=None)
    exp.add_argument("--weights", type=Path, default=None)
    exp.add_argument("--model-name", type=str, default="RealESRGAN_x4plus")
    exp.add_argument("--tile-size", type=int, default=0)
    exp.add_argument("--crop-policy", choices=("reject", "center-crop", "pad-black"), default="reject")
    exp.add_argument("--profile", type=str, default=None, help="Optional print profile name or JSON path")
    exp.add_argument("--destination-icc", type=Path, default=None, help="Optional measured printer/paper ICC profile")
    exp.add_argument("--output-sharpen", action="store_true", help="Apply post-resize medium-specific output sharpening")
    exp.add_argument("--report-dir", type=Path, default=Path("outputs/report"))

    # 2. inspect
    insp = sub.add_parser("inspect", help="Inspect an existing image")
    insp.add_argument("--input", type=Path, required=True)
    insp.add_argument("--json", action="store_true", help="Emit machine-readable JSON inspection")

    # 3. restore
    rest = sub.add_parser("restore", help="Run source-preserving restoration with gradient and flat-black lock")
    rest.add_argument("--input", type=Path, required=True)
    rest.add_argument("--output", type=Path, required=True)
    rest.add_argument("--width-in", type=Decimal, default=None)
    rest.add_argument("--height-in", type=Decimal, default=None)
    rest.add_argument("--width-px", type=int, default=None)
    rest.add_argument("--height-px", type=int, default=None)
    rest.add_argument("--ppi", type=int, default=300)
    rest.add_argument("--min-mib", type=float, default=0.0)
    rest.add_argument("--max-mib", type=float, default=None)
    rest.add_argument(
        "--backend",
        choices=("lanczos", "realesrgan", "realesrgan_native", "realesrgan_antidrift"),
        default="lanczos",
    )
    rest.add_argument("--realesrgan-repo", type=Path, default=None)
    rest.add_argument("--weights", type=Path, default=None)
    rest.add_argument("--report-dir", type=Path, default=Path("outputs/restore-report"))

    # 4. evaluate
    ev = sub.add_parser("evaluate", help="Evaluate candidate output against optional ground-truth reference and gold cases")
    ev.add_argument("--candidate", type=Path, required=True)
    ev.add_argument("--reference", type=Path, default=None)
    ev.add_argument("--check-heart", action="store_true", help="Run Frontal Red Cubic Heart symmetry/containment check")
    ev.add_argument("--check-flat-black", action="store_true", help="Run flat-black border integrity check")
    ev.add_argument("--report-dir", type=Path, default=Path("outputs/evaluation"))

    # 5. benchmark
    bm = sub.add_parser("benchmark", help="Run controlled degradation SR benchmark with registered crop panel")
    bm.add_argument("--ground-truth", type=Path, required=True)
    bm.add_argument("--output-dir", type=Path, default=Path("outputs/benchmark"))
    bm.add_argument("--scale", type=int, default=4)
    bm.add_argument("--blur-sigma", type=float, default=1.0)
    bm.add_argument("--noise-sigma", type=float, default=1.5)
    bm.add_argument("--realesrgan-repo", type=Path, default=None)
    bm.add_argument("--weights", type=Path, default=None)

    # 6. calibrate
    cal = sub.add_parser("calibrate", help="Run print/paper ICC soft-proof analysis or series cohesion check")
    cal.add_argument("--input", type=Path, required=True)
    cal.add_argument("--profile", type=str, default="matte_300ppi")
    cal.add_argument("--destination-icc", type=Path, default=None)
    cal.add_argument("--series", type=Path, nargs="*", default=None, help="Optional series images to compare against --input as anchor")
    cal.add_argument("--report-dir", type=Path, default=Path("outputs/calibration"))

    args = parser.parse_args(argv)

    if args.operation == "inspect":
        validate_input_security(args.input)
        with Image.open(args.input) as im:
            im.load()
            w, h = im.size
            mode = im.mode
            fmt = im.format
            dpi = im.info.get("dpi")
            icc_info = inspect_icc_profile(im.info.get("icc_profile"))
        mib = args.input.stat().st_size / (1024 * 1024)
        digest = sha256(args.input)
        if args.json:
            print(
                json.dumps(
                    {
                        "path": str(args.input),
                        "width": w,
                        "height": h,
                        "mode": mode,
                        "format": fmt,
                        "dpi": list(dpi) if dpi else None,
                        "size_bytes": args.input.stat().st_size,
                        "size_mib": round(mib, 6),
                        "sha256": digest,
                        "icc": icc_info,
                    },
                    indent=2,
                )
            )
        else:
            print(f"{w}x{h} {mode} {fmt} {dpi}")
            print(f"{mib:.6f} MiB")
            print(f"sha256: {digest}")
        return

    if args.operation == "export":
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Refusing to overwrite input image")
        validate_input_security(args.input)

        prof_data = load_print_profile(args.profile) if args.profile else None
        ppi = int(prof_data.get("ppi", args.ppi)) if (prof_data and args.ppi == 300) else args.ppi

        requested = resolve_target_dimensions(
            width_in=args.width_in,
            height_in=args.height_in,
            ppi=ppi,
            width_px=args.width_px,
            height_px=args.height_px,
        )

        with Image.open(args.input) as src:
            if args.crop_policy == "reject":
                check_aspect_ratio(src.size, requested)
            if src.mode != "RGB":
                raise ValueError("MVP expects RGB input")
            icc = src.info.get("icc_profile")

        # Keep exact compatibility with tests that patch or inspect `render` when default options are used
        if (
            args.crop_policy == "reject"
            and args.model_name == "RealESRGAN_x4plus"
            and args.tile_size == 0
            and args.backend in ("lanczos", "realesrgan")
        ):
            image, backend_info = render(
                args.input,
                requested,
                args.backend,
                args.realesrgan_repo,
                args.weights,
            )
            prov_dict = None
        else:
            image, prov = render_with_provenance(
                args.input,
                requested,
                args.backend,
                args.realesrgan_repo,
                args.weights,
                model_name=args.model_name,
                crop_policy=args.crop_policy,
                tile_size=args.tile_size,
            )
            backend_info = prov.backend_label
            prov_dict = prov.to_dict()

        cal_info = None
        if args.output_sharpen or args.profile or args.destination_icc:
            w_in = float(args.width_in) if args.width_in is not None else requested[0] / float(ppi)
            h_in = float(args.height_in) if args.height_in is not None else requested[1] / float(ppi)
            v_dist = viewing_distance_for_print(w_in, h_in)
            medium_name = prof_data.get("medium", args.profile or "matte") if prof_data else (args.profile or "matte")
            if args.output_sharpen:
                image, sharpen_meta = apply_output_sharpening(image, medium=str(medium_name), viewing_distance_in=v_dist)
            else:
                sharpen_meta = {"applied": False}
            proof_meta = soft_proof_icc(image, args.destination_icc, source_icc_bytes=icc)
            cal_info = {
                "profile": prof_data or args.profile,
                "viewing_distance_in": v_dist,
                "output_sharpening": sharpen_meta,
                "soft_proof": proof_meta,
            }

        level, _ = save_png_verified(
            image,
            args.output,
            ppi,
            args.min_mib,
            args.max_mib,
            icc,
        )
        report = verify_and_report(
            args.input,
            args.output,
            requested,
            ppi,
            args.min_mib,
            backend_info,
            level,
            args.report_dir,
            maximum_mib=args.max_mib,
            provenance=prov_dict,
            calibration_info=cal_info,
        )
        print(f"PASS {report['pixels']} {report['size_mib']:.3f} MiB {report['sr_backend']}")
        return

    if args.operation == "restore":
        requested = resolve_target_dimensions(
            width_in=args.width_in,
            height_in=args.height_in,
            ppi=args.ppi,
            width_px=args.width_px,
            height_px=args.height_px,
        )
        report = restore_source_locked(
            input_path=args.input,
            output_path=args.output,
            target_size=requested,
            ppi=args.ppi,
            minimum_mib=args.min_mib,
            maximum_mib=args.max_mib,
            backend=args.backend,
            repo=args.realesrgan_repo,
            weights=args.weights,
            report_dir=args.report_dir,
        )
        print(f"PASS RESTORE {report['pixels']} {report['size_mib']:.3f} MiB {report['sr_backend']}")
        return

    if args.operation == "evaluate":
        metrics = evaluate_pair(args.reference, args.candidate)
        with Image.open(args.candidate) as cand_im:
            cand_im.load()
            if args.check_heart:
                metrics["heart_gold_case"] = evaluate_heart_gold_case(cand_im)
            if args.check_flat_black:
                metrics["flat_black_background"] = evaluate_flat_black_background(cand_im)
        args.report_dir.mkdir(parents=True, exist_ok=True)
        (args.report_dir / "evaluation.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(metrics, indent=2))
        return

    if args.operation == "benchmark":
        deg = DegradationSpec(
            scale_factor=args.scale,
            gaussian_blur_sigma=args.blur_sigma,
            noise_sigma=args.noise_sigma,
        )
        summary = run_benchmark(
            ground_truth_path=args.ground_truth,
            output_dir=args.output_dir,
            degradation=deg,
            realesrgan_repo=args.realesrgan_repo,
            weights_path=args.weights,
        )
        base_psnr = summary["methods"]["lanczos_baseline"]["psnr_db"]
        rest_psnr = summary["methods"]["source_locked_cpu_restoration"]["psnr_db"]
        sr_status = summary["methods"]["realesrgan_x4plus"]["status"]
        print(f"BENCHMARK PASS lanczos_psnr={base_psnr:.2f}dB restored_cpu_psnr={rest_psnr:.2f}dB realesrgan={sr_status}")
        return

    if args.operation == "calibrate":
        validate_input_security(args.input)
        prof_data = load_print_profile(args.profile)
        with Image.open(args.input) as im:
            im.load()
            icc = im.info.get("icc_profile")
            proof = soft_proof_icc(im, args.destination_icc, source_icc_bytes=icc)
        result: dict[str, object] = {
            "input": str(args.input),
            "profile": prof_data,
            "soft_proof": proof,
        }
        if args.series:
            cohesion = evaluate_series_cohesion(args.input, list(args.series))
            result["series_cohesion"] = cohesion.to_dict()
        args.report_dir.mkdir(parents=True, exist_ok=True)
        (args.report_dir / "calibration.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return


if __name__ == "__main__":
    main()
