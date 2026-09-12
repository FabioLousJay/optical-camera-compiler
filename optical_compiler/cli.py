"""Command-line interface for the Optical Camera Compiler."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Optional

from .compiler import OpticalCompiler
from .models import TargetEngine


def copy_to_clipboard(text: str) -> bool:
    """Copy text to macOS clipboard using pbcopy if available."""
    try:
        process = subprocess.Popen(
            ["pbcopy"], stdin=subprocess.PIPE, close_fds=True
        )
        process.communicate(text.encode("utf-8"))
        return process.returncode == 0
    except Exception:
        return False


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI."""
    parser = argparse.ArgumentParser(
        prog="optical-compiler",
        description="Optical Camera Compiler: Hardware-level optical simulation for zero-artifact photorealism.",
    )

    parser.add_argument(
        "scene",
        nargs="?",
        help="Creative description of the subject or scene (e.g., 'Portrait of a master sculptor in a sunlit atelier').",
    )
    parser.add_argument(
        "-t",
        "--target",
        default="flux",
        choices=["gpt_images", "imagen", "midjourney", "flux", "sdxl", "raw", "json", "all"],
        help="Target generation model / engine (default: 'flux').",
    )
    parser.add_argument(
        "-p",
        "--profile",
        default="phase_one_iq4",
        help="Camera hardware profile ID or path (default: 'phase_one_iq4').",
    )
    parser.add_argument(
        "--framing",
        help="Framing description (e.g., 'tight macro headshot', 'three-quarter environmental portrait').",
    )
    parser.add_argument(
        "--environment",
        help="Background/environment setting.",
    )
    parser.add_argument(
        "--wardrobe",
        help="Styling and clothing details.",
    )
    parser.add_argument(
        "--mood",
        help="Atmospheric mood or tone.",
    )
    parser.add_argument(
        "--aperture",
        help="Override optical aperture sweet spot (e.g., 'f/4', 'f/2.8', 'f/8').",
    )
    parser.add_argument(
        "--lens",
        help="Override optical lens model.",
    )
    parser.add_argument(
        "--lighting",
        help="Override lighting configuration.",
    )
    parser.add_argument(
        "--ar",
        dest="aspect_ratio",
        default="4:5",
        help="Aspect ratio (default: '4:5').",
    )
    parser.add_argument(
        "--reference",
        "--ref",
        dest="reference",
        help="Path or name of reference image on local hardware for restoration or transformation.",
    )
    parser.add_argument(
        "--ref-mode",
        dest="ref_mode",
        choices=["restore", "transform", "depixelate", "depixelate_gfx100rf", "identity", "identity_lock", "product", "product_lock", "product_crop"],
        default="restore",
        help="Reference mode: 'restore' (optical remaster), 'transform' (re-shoot/adapt), 'identity_lock' (strict anatomical lock), 'depixelate_gfx100rf' (v3.1 102MP lock), or 'product_lock' (100%% SKU lock).",
    )
    parser.add_argument(
        "--depixelate",
        action="store_true",
        help="Shortcut for --ref-mode depixelate_gfx100rf (Universal De-Pixelate & 102MP Upscale Restoration).",
    )
    parser.add_argument(
        "--product-lock",
        action="store_true",
        help="Shortcut for --ref-mode product_lock (Commercial Product SKU & Packaging Fidelity Lock).",
    )
    parser.add_argument(
        "--product-crop",
        dest="product_crop",
        default=None,
        help="Path or identifier for the isolated product-reference crop image.",
    )
    parser.add_argument(
        "--sku-color",
        dest="sku_color",
        default=None,
        help="Commercial product SKU color (e.g. 'Pantone 19-4052 Classic Blue', '#0F4C81', 'Amber Glass').",
    )
    parser.add_argument(
        "--cap-geometry",
        dest="cap_geometry",
        default=None,
        help="Cap and closure form factor (e.g. 'Fluted 28mm black phenolic cap with 32 vertical knurling ribs').",
    )
    parser.add_argument(
        "--label-kerning",
        dest="label_kerning",
        default=None,
        help="Label typography and tracking lock (e.g. 'Helvetica Neue 75 Bold, letter tracking +15, zero typographic hallucination').",
    )
    parser.add_argument(
        "--material-finish",
        dest="material_finish",
        default=None,
        help="Product material finish (e.g. 'Frosted borosilicate glass, satin finish, 15%% specular roughness').",
    )
    parser.add_argument(
        "--seams",
        dest="seam_geometry",
        default=None,
        help="Manufacturing seams and mold parting lines (e.g. 'Dual vertical mold parting seams along container sides').",
    )
    parser.add_argument(
        "--no-approval-gate",
        dest="approval_gate",
        action="store_false",
        default=True,
        help="Disable the 100%% Commercial SKU Approval Gate.",
    )
    parser.add_argument(
        "--camera-angle",
        dest="camera_angle",
        default=None,
        help="Camera perspective angle (e.g. 'chest-level frontal angle', 'eye-level', 'low-angle').",
    )
    parser.add_argument(
        "--color-mode",
        dest="color_mode",
        default=None,
        help="Color mode / tonality (e.g. 'monochrome', 'black_and_white', 'indie_bw').",
    )
    parser.add_argument(
        "--bw",
        "--monochrome",
        dest="monochrome",
        action="store_true",
        help="Shortcut to force black-and-white indie-cinema monochrome tonality.",
    )
    parser.add_argument(
        "--crowd-action",
        dest="crowd_action",
        default=None,
        help="Crowd action description for multi-directional slow shutter motion-blur dynamics.",
    )
    parser.add_argument(
        "--content-type",
        dest="content_type",
        choices=[
            "photograph",
            "portrait",
            "product_photo",
            "document_scan",
            "poster_or_flyer",
            "meme_or_infographic",
            "ui_or_screenshot",
            "mixed_content",
        ],
        default="photograph",
        help="Input classification type for restoration (suppresses DoF, vignetting, and grain for document scans and screenshots).",
    )
    parser.add_argument(
        "--no-skin-realism",
        action="store_true",
        help="Disable the Human Skin Realism Override protocol.",
    )
    parser.add_argument(
        "--no-text-preservation",
        action="store_true",
        help="Disable strict OCR text and diagram preservation.",
    )
    parser.add_argument(
        "--fidelity-lock",
        dest="fidelity_lock",
        type=float,
        default=0.95,
        help="Anti-drift fidelity lock intensity from 0.5 to 1.0 (default: 0.95).",
    )
    parser.add_argument(
        "--denoise",
        dest="denoise",
        type=float,
        help="Denoising strength override (default: 0.35 for restore, 0.65 for transform).",
    )
    parser.add_argument(
        "--lighting-preset",
        choices=[
            "golden_hour",
            "blue_hour",
            "studio_soft",
            "studio_hard",
            "flash_freeze",
            "overcast",
            "dramatic",
            "neon",
        ],
        help="Photographic lighting preset from the High-End Master framework.",
    )
    parser.add_argument(
        "--capture-mode",
        choices=[
            "static_max_detail",
            "portrait_max_detail",
            "action_max_detail",
            "macro_max_detail",
            "landscape_architecture_max_detail",
        ],
        help="Photographic capture intent mode enforcing physical sensor/stability directives.",
    )
    parser.add_argument(
        "--upscale-102mp",
        metavar="IMAGE_PATH",
        help="Execute the PIL Conservative 102MP Restoration and Upscale Lock on the given image.",
    )
    parser.add_argument(
        "--upscale-out",
        metavar="OUTPUT_PATH",
        help="Output filepath for 102MP upscale.",
    )
    parser.add_argument(
        "--upscale-format",
        choices=["jpeg", "jpg", "png", "tiff", "tif"],
        help="Output format for 102MP upscale (default: PNG if alpha, JPEG otherwise).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON payload.",
    )
    parser.add_argument(
        "--pos-only",
        action="store_true",
        help="Print only the positive prompt (ideal for shell piping).",
    )
    parser.add_argument(
        "--neg-only",
        action="store_true",
        help="Print only the negative prompt.",
    )
    parser.add_argument(
        "-c",
        "--copy",
        action="store_true",
        help="Automatically copy positive prompt to macOS clipboard (via pbcopy).",
    )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # 1. Handle direct 102MP upscale request if provided
    if args.upscale_102mp:
        try:
            from .restoration import RestorationConfig, restore_and_upscale_102mp
            config = RestorationConfig(human_skin_realism=not args.no_skin_realism)
            report = restore_and_upscale_102mp(
                args.upscale_102mp,
                output_path=args.upscale_out,
                output_format=args.upscale_format,
                config=config,
            )
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print("=" * 80)
                print("PIL CONSERVATIVE 102MP RESTORATION AND UPSCALE LOCK")
                print(f"Profile: {report['profile']} (v{report['version']})")
                print("=" * 80)
                print(f"Input:       {report['input_path']} ({report['source_width']}x{report['source_height']}, {report['source_megapixels']} MP)")
                print(f"Output:      {report['output_path']} ({report['output_width']}x{report['output_height']}, {report['output_megapixels']} MP)")
                print(f"Ratio Lock:  Exact rational ratio preserved = {report['exact_aspect_ratio_preserved']}")
                print(f"Stages:      {' -> '.join(report['upscale_stages'])}")
                print(f"Skin Realism:{'ACTIVE (Protected organic micro-relief)' if report.get('human_skin_realism_active') else 'OFF'}")
                print(f"File Size:   {report['file_size_mib_standard']} MiB ({report['file_size_bytes']} bytes)")
                print(f"Validation:  {'PASSED (Zero-drift verified)' if report['validation_passed'] else 'FAILED'}")
            return 0 if report["validation_passed"] else 1
        except Exception as err:
            sys.stderr.write(f"102MP Upscale Error: {err}\n")
            return 1

    if not args.scene:
        parser.print_help()
        return 1

    try:
        compiler = OpticalCompiler(profile=args.profile)
    except Exception as err:
        sys.stderr.write(f"Error loading camera profile '{args.profile}': {err}\n")
        return 1

    ref_mode_choice = args.ref_mode
    if args.depixelate:
        ref_mode_choice = "depixelate_gfx100rf"
    elif getattr(args, "product_lock", False):
        ref_mode_choice = "product_lock"

    ref_dict = None
    ref_path = args.reference or getattr(args, "product_crop", None)
    if ref_path or ref_mode_choice in ("product_lock", "product", "product_crop"):
        if ref_mode_choice in ("depixelate", "depixelate_gfx100rf"):
            mode_str = "depixelate_gfx100rf"
            default_denoise = 0.25
        elif ref_mode_choice in ("identity", "identity_lock"):
            mode_str = "identity_lock"
            default_denoise = 0.30
        elif ref_mode_choice in ("product_lock", "product", "product_crop", "sku_lock", "packshot"):
            mode_str = "product_lock"
            default_denoise = 0.20
        elif ref_mode_choice == "restore":
            mode_str = "restore_upscale"
            default_denoise = 0.35
        else:
            mode_str = "transform_adapt"
            default_denoise = 0.65

        denoise_val = args.denoise if args.denoise is not None else default_denoise
        ref_dict = {
            "filename": ref_path or "product_reference_crop.png",
            "mode": mode_str,
            "fidelity_lock": args.fidelity_lock,
            "denoise_strength": denoise_val,
        }

    common_kwargs = {
        "framing": args.framing,
        "environment": args.environment,
        "wardrobe": args.wardrobe,
        "mood": args.mood,
        "aperture": args.aperture,
        "lens": args.lens,
        "lighting": args.lighting,
        "aspect_ratio": args.aspect_ratio,
        "reference": ref_dict,
        "product_crop": getattr(args, "product_crop", None),
        "sku_color": getattr(args, "sku_color", None),
        "cap_geometry": getattr(args, "cap_geometry", None),
        "label_kerning": getattr(args, "label_kerning", None),
        "material_finish": getattr(args, "material_finish", None),
        "seam_geometry": getattr(args, "seams", None),
        "approval_gate_100pct": not getattr(args, "no_approval_gate", False),
        "lighting_preset": args.lighting_preset,
        "capture_mode": args.capture_mode,
        "human_skin_realism": not args.no_skin_realism,
        "content_type": args.content_type,
        "text_preservation": not args.no_text_preservation,
        "camera_angle": args.camera_angle,
        "color_mode": "monochrome" if args.monochrome else args.color_mode,
        "crowd_action": args.crowd_action,
    }

    profile_title = (
        compiler.base_profile.title
        if compiler.base_profile
        else "Auto (Intelligent Camera Router)"
    )

    if args.target == "all":
        results = compiler.compile_all(args.scene, **common_kwargs)
        if args.json:
            print(json.dumps({k: v.to_dict() for k, v in results.items()}, indent=2))
        else:
            print("=" * 80)
            print(f"OPTICAL COMPILATION: {args.scene}")
            print(f"Base Profile: {profile_title}")
            print("=" * 80)
            for target_name, payload in results.items():
                print(f"\n--- [{target_name.upper()}] ---")
                print(payload.positive_prompt)
                if payload.negative_prompt:
                    print(f"\n[NEGATIVE / SUPPRESSION]:\n{payload.negative_prompt}")
        return 0

    try:
        payload = compiler.compile(
            args.scene,
            target=args.target,
            **common_kwargs,
        )
    except Exception as err:
        sys.stderr.write(f"Compilation error: {err}\n")
        return 1

    if args.pos_only:
        print(payload.positive_prompt)
    elif args.neg_only:
        print(payload.negative_prompt)
    elif args.json:
        print(payload.to_json())
    else:
        print("=" * 80)
        print(f"OPTICAL COMPILER [Target: {payload.target_engine.value.upper()}]")
        print(f"Profile: {profile_title}")
        print("=" * 80)
        print("\n[COMPILED PROMPT]:")
        print(payload.positive_prompt)

        if payload.negative_prompt and payload.target_engine != TargetEngine.MIDJOURNEY:
            print("\n[ARTIFACT SUPPRESSION SHIELD]:")
            print(payload.negative_prompt)

        if payload.parameters:
            print("\n[RECOMMENDED PARAMETERS]:")
            print(json.dumps(payload.parameters, indent=2))

    if args.copy:
        text_to_copy = (
            payload.positive_prompt
            if args.pos_only
            else (payload.negative_prompt if args.neg_only else payload.unified_prompt)
        )
        if copy_to_clipboard(text_to_copy):
            sys.stderr.write("\n[Copied unified prompt (with anti-artifact shield) to macOS clipboard]\n")
        else:
            sys.stderr.write("\n[Warning: Unable to copy to clipboard]\n")

    return 0


def upscaler_main(argv: Optional[list[str]] = None) -> int:
    """Dedicated CLI entrypoint for PIL Conservative 102MP Restoration and Upscale Lock."""
    parser = argparse.ArgumentParser(
        prog="optical-upscaler",
        description="PIL Conservative 102MP Restoration and Upscale Lock (PLATINUM_NO_DRIFT).",
    )
    parser.add_argument("image", help="Path to input image file.")
    parser.add_argument("-o", "--output", help="Optional destination output path.")
    parser.add_argument(
        "-f",
        "--format",
        choices=["jpeg", "jpg", "png", "tiff", "tif"],
        help="Target output format.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON execution report.",
    )
    args = parser.parse_args(argv)

    try:
        from .restoration import restore_and_upscale_102mp
        report = restore_and_upscale_102mp(
            args.image,
            output_path=args.output,
            output_format=args.format,
        )
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("=" * 80)
            print("PIL CONSERVATIVE 102MP RESTORATION AND UPSCALE LOCK")
            print(f"Profile: {report['profile']} (v{report['version']})")
            print("=" * 80)
            print(f"Input:       {report['input_path']} ({report['source_width']}x{report['source_height']}, {report['source_megapixels']} MP)")
            print(f"Output:      {report['output_path']} ({report['output_width']}x{report['output_height']}, {report['output_megapixels']} MP)")
            print(f"Ratio Lock:  Exact rational ratio preserved = {report['exact_aspect_ratio_preserved']}")
            print(f"Stages:      {' -> '.join(report['upscale_stages'])}")
            print(f"File Size:   {report['file_size_mib_standard']} MiB ({report['file_size_bytes']} bytes)")
            print(f"Validation:  {'PASSED (Zero-drift verified)' if report['validation_passed'] else 'FAILED'}")
            if report.get("validation_failures"):
                print(f"Failures:    {report['validation_failures']}")
        return 0 if report["validation_passed"] else 1
    except Exception as err:
        sys.stderr.write(f"102MP Upscale Error: {err}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
