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
        choices=["restore", "transform"],
        default="restore",
        help="Reference mode: 'restore' (optical remaster & upscale) or 'transform' (context adaptation with identity lock).",
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

    if not args.scene:
        parser.print_help()
        return 1

    try:
        compiler = OpticalCompiler(profile=args.profile)
    except Exception as err:
        sys.stderr.write(f"Error loading camera profile '{args.profile}': {err}\n")
        return 1

    ref_dict = None
    if args.reference:
        mode_str = "restore_upscale" if args.ref_mode == "restore" else "transform_adapt"
        default_denoise = 0.35 if args.ref_mode == "restore" else 0.65
        denoise_val = args.denoise if args.denoise is not None else default_denoise
        ref_dict = {
            "filename": args.reference,
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
        "lighting_preset": args.lighting_preset,
        "capture_mode": args.capture_mode,
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


if __name__ == "__main__":
    sys.exit(main())
