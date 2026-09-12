"""Command-line interface for the Optical Camera Compiler."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
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
        "--scene",
        dest="scene_flag",
        help="Creative description of the subject or scene (flag alternative).",
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
        choices=[
            "restore", "transform", "depixelate", "depixelate_gfx100rf", "identity", "identity_lock",
            "product", "product_lock", "product_crop", "recon_4x", "reconstruction_lock_4x", "4x_recon", "p4x_lock"
        ],
        default="restore",
        help="Reference mode: 'restore', 'transform', 'identity_lock', 'depixelate_gfx100rf', 'product_lock', or 'recon_4x' (4X Reconstruction Lock).",
    )
    parser.add_argument(
        "--depixelate",
        action="store_true",
        help="Shortcut for --ref-mode depixelate_gfx100rf (Universal De-Pixelate & 102MP Upscale Restoration).",
    )
    parser.add_argument(
        "--recon-4x",
        "--reconstruction-lock-4x",
        dest="recon_4x",
        nargs="?",
        const=True,
        default=None,
        help="Activate Professional 4X Reconstruction Lock Protocol (exact 4X linear expansion, source lock, multi-model blend). Optionally pass an image path to execute reconstruction directly.",
    )
    parser.add_argument(
        "--sr-backend",
        dest="sr_backend",
        choices=["realesrnet_x4plus", "swinir_m_x4", "realesrgan_x4v3", "realesrgan_x4plus", "hat_s_x4", "pil_conservative"],
        default="realesrnet_x4plus",
        help="Super-resolution model backend for 4X Reconstruction Lock (default: 'realesrnet_x4plus').",
    )
    parser.add_argument(
        "--sr-denoise",
        dest="sr_denoise",
        type=float,
        default=0.15,
        help="Denoising strength for SR backend (0.0 to 1.0, default: 0.15 for controlled detail without texture wipe).",
    )
    parser.add_argument(
        "--sr-blend",
        dest="sr_blend",
        type=float,
        default=0.20,
        help="High-frequency detail blend ratio (0.0 to 1.0, default: 0.20 for 15%%-30%% detail composite on textured regions).",
    )
    parser.add_argument(
        "--no-protect-sky",
        dest="protect_sky_haze",
        action="store_false",
        default=True,
        help="Disable automatic sky, cloud, and atmospheric haze protection masking during 4X reconstruction.",
    )
    parser.add_argument(
        "--recon-out",
        dest="recon_out",
        default=None,
        help="Output destination path for 4X reconstruction execution.",
    )
    parser.add_argument(
        "--recon-format",
        dest="recon_format",
        choices=["png", "tiff", "tif", "jpeg", "jpg"],
        default=None,
        help="Target output format for 4X reconstruction.",
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
    # --- Tool 1: Biomechanical Hand & Finger Precision Gate ---
    parser.add_argument(
        "--hand-lock",
        action="store_true",
        help="Activate 5-Point Grip Lock and Biomechanical Hand Precision Gate (enforces 5-ray metacarpals, joint creases, cuticle beds, contact tissue blanching).",
    )
    parser.add_argument(
        "--grip-type",
        dest="grip_type",
        choices=["palm_support", "precision_pinch", "cylindrical_wrap", "relaxed_rest", "open_palm"],
        default=None,
        help="Grip type for biomechanical hand lock.",
    )
    parser.add_argument(
        "--hand-details",
        dest="hand_details",
        default=None,
        help="Specific hand/finger anatomical details or grip description.",
    )
    # --- Tool 2: Cinema Anamorphic Optics & Flare Engine ---
    parser.add_argument(
        "--anamorphic",
        action="store_true",
        help="Activate Cinema Anamorphic Optics & Flare Engine (forces 2:1 elliptical oval bokeh and widescreen ratio).",
    )
    parser.add_argument(
        "--squeeze",
        dest="squeeze",
        choices=["1.0x", "1.33x", "1.5x", "1.8x", "2.0x"],
        default=None,
        help="Anamorphic horizontal squeeze factor.",
    )
    parser.add_argument(
        "--streak-flare",
        dest="streak_flare",
        choices=["cyan_blue", "warm_gold", "neutral_silver", "vintage_magenta"],
        default=None,
        help="Anamorphic horizontal streak flare color profile.",
    )
    parser.add_argument(
        "--iris-blades",
        dest="iris_blades",
        choices=["14_blade_circular", "9_blade_rounded", "8_blade_octagonal", "6_blade_hexagonal"],
        default=None,
        help="Aperture diaphragm iris blade count and diffraction geometry.",
    )
    # --- Tool 3: Commercial Advertising Suite ---
    parser.add_argument(
        "--gobo",
        dest="gobo",
        choices=["venetian_blinds", "dappled_foliage", "window_panes", "geometric_slits", "prism_fracture"],
        default=None,
        help="Gobo projection mask / cookie pattern.",
    )
    parser.add_argument(
        "--grip",
        dest="grip_modifier",
        choices=["beauty_dish_honeycomb", "butterfly_8x8_silk", "snoot_pinpoint", "solid_black_floppy"],
        default=None,
        help="Professional studio grip modifier.",
    )
    parser.add_argument(
        "--lighting-ratio",
        dest="lighting_ratio",
        choices=["1:1", "2:1", "4:1", "8:1", "16:1"],
        default=None,
        help="Key-to-fill lighting contrast ratio.",
    )
    parser.add_argument(
        "--copy-space",
        dest="copy_space",
        choices=["left_third", "right_third", "top_third", "bottom_third"],
        default=None,
        help="Ad-safe copy-space negative space placement for typography/billboard.",
    )
    parser.add_argument(
        "--ad-safe-zone",
        dest="ad_safe_zone",
        choices=["tiktok_reels_9_16", "instagram_feed_4_5", "ecommerce_catalog_1_1"],
        default=None,
        help="Social media ad UI safe-zone exclusion overlay.",
    )
    # --- Tool 4: Body Morphology & Proportional Volume Calibration Engine ---
    parser.add_argument(
        "--body-volume",
        dest="body_volume",
        default=None,
        help="Body volume enhancement regions (e.g. 'biceps, chest, gut' or 'legs, waist').",
    )
    parser.add_argument(
        "--weight-lb",
        dest="weight_lb",
        type=int,
        default=None,
        help="Calibrated target body mass in pounds (e.g. 240).",
    )
    # --- Tool 5: 4D Volumetric & Premium Material Engine ---
    parser.add_argument(
        "--material",
        dest="material",
        choices=[
            "latex_gloss",
            "glossy_latex",
            "liquid_glass",
            "dielectric_acrylic",
            "polished_vinyl",
            "anodized_aluminum",
            "brushed_titanium",
            "matte_silicone",
            "high_gloss_plastic",
            "metallic_flake",
            "translucent_resin",
            "volumetric_4d",
        ],
        default=None,
        help="Premium material finish for 4D volumetric rendering.",
    )
    parser.add_argument(
        "--background-style",
        dest="background_style",
        choices=[
            "default",
            "pure_black_blur",
            "opaque_black_blur",
            "opaque_black_blurred",
            "minimalist_studio_grey",
            "clean_high_key_white",
            "pure_black_matte",
            "studio_cyclorama",
            "negative_void",
            "environmental_natural",
        ],
        default=None,
        help="Background isolation style for dimensional foreground separation.",
    )
    parser.add_argument(
        "--volumetric-4d",
        dest="volumetric_4d",
        action="store_true",
        help="Activate 4D volumetric rendering with contour rim lighting and deep tonal separation.",
    )
    parser.add_argument(
        "--remove-text",
        dest="remove_text",
        action="store_true",
        help="Activate conditional text removal engine when letters or captions are present in reference.",
    )
    # --- Tool 6: Print-Calibrated Prepress & Exhibition Lab Matrix ---
    parser.add_argument(
        "--paper",
        dest="paper",
        choices=["matte_cotton", "luster", "glossy", "baryta", "canvas"],
        default=None,
        help="Fine art exhibition paper profile for print calibration.",
    )
    parser.add_argument(
        "--print-size",
        dest="print_size",
        default=None,
        help="Target physical print dimension and resolution (e.g. '16x24@300', '24x36@240', '9x12@640').",
    )
    # --- Tool 7: Policy-Safe Compliance Recovery Layer ---
    parser.add_argument(
        "--policy-safe",
        dest="policy_safe",
        action="store_true",
        help="Enforce policy-safe compliance layer preventing refusal loops while locking camera physics and anatomy.",
    )
    # --- Tool 8: PFEP v1.0 Diagnostic Stress Probes ---
    parser.add_argument(
        "--probe",
        "-k",
        dest="probe",
        choices=[
            "master_portrait_lock",
            "outpaint_lens_honest",
            "stress_hard_key",
            "stress_cross_polarized",
            "stress_glasses_reflections",
            "stress_seated_compression",
            "stress_standing_compression",
            "stress_background_scale",
            "stress_hair_specular",
            "stress_shadow_color",
        ],
        default=None,
        help="PFEP v1.0 canonical stress diagnostic probe.",
    )
    # --- Tool 9: Closed-Loop Output Constraints & Exhibition Systems ---
    parser.add_argument(
        "--min-mb",
        dest="min_mb",
        type=float,
        default=None,
        help="Non-negotiable minimum file size in MB for closed-loop super-resolution export.",
    )
    parser.add_argument(
        "--cct",
        dest="cct_kelvin",
        type=int,
        default=None,
        help="Gallery exhibition correlated color temperature in Kelvin (e.g. 5000).",
    )
    parser.add_argument(
        "--lux",
        dest="illuminance_lux",
        type=int,
        default=None,
        help="Gallery exhibition illuminance in lux (e.g. 500).",
    )
    parser.add_argument(
        "--cri",
        dest="spectral_cri",
        type=float,
        default=None,
        help="Gallery exhibition lighting CRI / TM-30 spectral fidelity (e.g. 98.0).",
    )
    parser.add_argument(
        "--wall-surround",
        dest="wall_surround",
        default=None,
        help="Gallery surround / wall reflectance (e.g. 'Neutral Gray 18%%', 'Deep Charcoal').",
    )
    parser.add_argument(
        "--gallery-zone",
        dest="gallery_zone",
        default=None,
        help="Gallery exhibition wing or zone for series cohesion (e.g. 'Zone A - North Wing').",
    )
    parser.add_argument(
        "--anchor-id",
        dest="anchor_image_id",
        default=None,
        help="Anchor image ID for exhibition series visual cohesion calibration.",
    )
    parser.add_argument(
        "--export-closed-loop",
        metavar="IMAGE_PATH",
        help="Execute closed-loop super-resolution export with machine-verifiable constraints on an image.",
    )
    parser.add_argument(
        "--export-out",
        metavar="OUTPUT_PATH",
        help="Output filepath for closed-loop export.",
    )
    parser.add_argument(
        "--export-format",
        choices=["png", "tiff", "jpeg"],
        help="Output format for closed-loop export (default: PNG).",
    )
    parser.add_argument(
        "--target-width",
        type=int,
        default=None,
        help="Exact output raster width in pixels.",
    )
    parser.add_argument(
        "--target-height",
        type=int,
        default=None,
        help="Exact output raster height in pixels.",
    )
    parser.add_argument(
        "--print-width",
        type=float,
        default=None,
        help="Physical print width in inches.",
    )
    parser.add_argument(
        "--print-height",
        type=float,
        default=None,
        help="Physical print height in inches.",
    )
    parser.add_argument(
        "--ppi",
        type=int,
        default=300,
        help="Target print raster PPI (default: 300).",
    )
    parser.add_argument(
        "--add-micro-noise",
        action="store_true",
        help="Inject subtle micro-noise entropy for lossless compression benchmarking experiment.",
    )
    parser.add_argument(
        "--report-md",
        metavar="REPORT_PATH",
        help="Save closed-loop execution report markdown to custom path.",
    )
    parser.add_argument(
        "--export-profile",
        "-ep",
        choices=["A", "B", "C", "a", "b", "c"],
        help="Practical export profile (A: 4000x6000 24MP, B: 5000x7500 37.5MP, C: 6000x9000 54MP).",
    )
    parser.add_argument(
        "--init-pfep",
        nargs="?",
        const="pfep_workspace",
        metavar="DIR",
        help="Initialize a complete PFEP v1.0 project directory with 10 diagnostic prompt packs and run logs.",
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

    # 0. Handle PFEP project initialization if requested
    if getattr(args, "init_pfep", None):
        try:
            from .pfep import init_pfep_project
            target_dir = args.init_pfep if args.init_pfep != "default" else "pfep_workspace"
            created = init_pfep_project(target_dir)
            if args.json:
                print(json.dumps({"target_dir": str(target_dir), "files_created": [str(p) for p in created]}, indent=2))
            else:
                print("=" * 80)
                print(f"PFEP v1.0 WORKSPACE INITIALIZED: {target_dir}")
                print("=" * 80)
                for p in created:
                    print(f"  + {p.relative_to(Path(target_dir).resolve()) if Path(target_dir).resolve() in p.parents else p.name}")
                print(f"\nSuccessfully generated {len(created)} protocol assets, 10 diagnostic prompt packs, and run logs.")
            return 0
        except Exception as err:
            sys.stderr.write(f"PFEP Initialization Error: {err}\n")
            return 1

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

    # 1b. Handle direct closed-loop export request if provided
    if getattr(args, "export_closed_loop", None):
        try:
            from .restoration import export_closed_loop
            run_rep, rep_dict = export_closed_loop(
                args.export_closed_loop,
                output_path=args.export_out or "export_output.png",
                target_width=args.target_width,
                target_height=args.target_height,
                width_in=args.print_width,
                height_in=args.print_height,
                ppi=args.ppi or 300,
                min_mb=args.min_mb,
                output_format=args.export_format,
                profile=getattr(args, "export_profile", None),
                add_noise=args.add_micro_noise,
                generate_report=True,
            )
            if args.report_md:
                Path(args.report_md).write_text(run_rep.to_markdown(), encoding="utf-8")
            if args.json:
                print(json.dumps(rep_dict, indent=2))
            else:
                print("=" * 80)
                print("CLOSED-LOOP SUPER-RESOLUTION EXPORT & PROVENANCE REPORT")
                print("=" * 80)
                print(f"Status:       {'PASSED' if run_rep.passed_constraints else 'FAILED'}")
                print(f"Input:        {run_rep.input_path} ({run_rep.source_dimensions[0]}x{run_rep.source_dimensions[1]})")
                print(f"Output:       {run_rep.output_path} ({run_rep.output_dimensions[0]}x{run_rep.output_dimensions[1]} @ {run_rep.target_ppi} PPI)")
                print(f"File Size:    {run_rep.file_size_mb:.2f} MB ({run_rep.file_size_bytes:,} bytes)")
                print(f"SHA-256:      {run_rep.sha256}")
                print(f"Time:         {run_rep.execution_seconds:.3f}s")
                if run_rep.failure_reasons:
                    print(f"Failures:     {', '.join(run_rep.failure_reasons)}")
            return 0 if run_rep.passed_constraints else 1
        except Exception as err:
            sys.stderr.write(f"Closed-Loop Export Error: {err}\n")
            return 1

    # 1c. Handle direct 4X reconstruction request if an image path was provided to --recon-4x
    if isinstance(getattr(args, "recon_4x", None), str) and Path(args.recon_4x).exists():
        try:
            from .restoration import execute_4x_reconstruction_lock
            rep, rep_d = execute_4x_reconstruction_lock(
                args.recon_4x,
                output_path=getattr(args, "recon_out", None),
                backend=getattr(args, "sr_backend", "realesrnet_x4plus"),
                denoise_strength=getattr(args, "sr_denoise", 0.15),
                blend_ratio=getattr(args, "sr_blend", 0.20),
                protect_sky_haze=getattr(args, "protect_sky_haze", True),
                output_format=getattr(args, "recon_format", None),
                generate_report=True,
            )
            if args.json:
                print(json.dumps(rep_d, indent=2))
            else:
                print("=" * 80)
                print("PROFESSIONAL 4X RECONSTRUCTION LOCK ENGINE")
                print("=" * 80)
                print(f"Status:       {'PASSED (Verified 4X Linear Source Lock)' if rep.validation_passed else 'FAILED'}")
                print(f"Input:        {rep.input_path} ({rep.source_dimensions[0]}x{rep.source_dimensions[1]}, {rep.source_megapixels} MP)")
                print(f"Output:       {rep.output_path} ({rep.output_dimensions[0]}x{rep.output_dimensions[1]}, {rep.output_megapixels} MP)")
                print(f"Multiplier:   {rep.linear_multiplier}X linear ({rep.area_multiplier}X pixel area)")
                print(f"Backend:      {rep.backend} (denoise: {rep.denoise_strength}, detail blend: {rep.blend_ratio})")
                print(f"Sky & Haze:   {'PROTECTED (Gradient Mask)' if rep.sky_haze_protected else 'UNMASKED'}")
                print(f"File Size:    {rep.file_size_mb:.2f} MB ({rep.file_size_bytes:,} bytes)")
                print(f"SHA-256:      {rep.sha256}")
                print(f"Time:         {rep.execution_seconds:.4f}s")
                if rep.validation_failures:
                    print(f"Failures:     {', '.join(rep.validation_failures)}")
            return 0 if rep.validation_passed else 1
        except Exception as err:
            sys.stderr.write(f"4X Reconstruction Error: {err}\n")
            return 1

    if not args.scene and getattr(args, "scene_flag", None):
        args.scene = args.scene_flag

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
    elif getattr(args, "recon_4x", None) is not None:
        ref_mode_choice = "recon_4x"

    ref_dict = None
    ref_path = args.reference or getattr(args, "product_crop", None)
    if ref_path or ref_mode_choice in ("product_lock", "product", "product_crop", "recon_4x", "reconstruction_lock_4x", "4x_recon", "p4x_lock"):
        if ref_mode_choice in ("depixelate", "depixelate_gfx100rf"):
            mode_str = "depixelate_gfx100rf"
            default_denoise = 0.25
        elif ref_mode_choice in ("identity", "identity_lock"):
            mode_str = "identity_lock"
            default_denoise = 0.30
        elif ref_mode_choice in ("product_lock", "product", "product_crop", "sku_lock", "packshot"):
            mode_str = "product_lock"
            default_denoise = 0.20
        elif ref_mode_choice in ("recon_4x", "reconstruction_lock_4x", "4x_recon", "p4x_lock"):
            mode_str = "reconstruction_lock_4x"
            default_denoise = getattr(args, "sr_denoise", 0.15)
        elif ref_mode_choice == "restore":
            mode_str = "restore_upscale"
            default_denoise = 0.35
        else:
            mode_str = "transform_adapt"
            default_denoise = 0.65

        denoise_val = args.denoise if args.denoise is not None else default_denoise
        ref_dict = {
            "filename": ref_path or (str(args.recon_4x) if isinstance(args.recon_4x, str) else "source_reference.png"),
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
        "reconstruction_lock": bool(getattr(args, "recon_4x", None) is not None or ref_mode_choice in ("recon_4x", "reconstruction_lock_4x", "4x_recon", "p4x_lock")),
        "sr_backend": getattr(args, "sr_backend", "realesrnet_x4plus"),
        "sr_denoise": getattr(args, "sr_denoise", 0.15),
        "sr_blend": getattr(args, "sr_blend", 0.20),
        "protect_sky_haze": getattr(args, "protect_sky_haze", True),
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
        "hand_lock": getattr(args, "hand_lock", False),
        "grip_type": getattr(args, "grip_type", None),
        "hand_details": getattr(args, "hand_details", None),
        "anamorphic": getattr(args, "anamorphic", False),
        "anamorphic_squeeze": getattr(args, "squeeze", None),
        "streak_flare": getattr(args, "streak_flare", None),
        "iris_blades": getattr(args, "iris_blades", None),
        "gobo": getattr(args, "gobo", None),
        "grip_modifier": getattr(args, "grip_modifier", None),
        "lighting_ratio": getattr(args, "lighting_ratio", None),
        "copy_space": getattr(args, "copy_space", None),
        "ad_safe_zone": getattr(args, "ad_safe_zone", None),
        "body_volume": getattr(args, "body_volume", None),
        "weight_lb": getattr(args, "weight_lb", None),
        "material_style": getattr(args, "material", None),
        "background_style": getattr(args, "background_style", None),
        "is_4d_volumetric": getattr(args, "volumetric_4d", False),
        "remove_text_when_present": getattr(args, "remove_text", False),
        "paper_profile": getattr(args, "paper", None),
        "print_spec": None,
        "policy_safe": getattr(args, "policy_safe", False),
        "stress_probe": getattr(args, "probe", None),
        "min_mb": getattr(args, "min_mb", None),
        "cct_kelvin": getattr(args, "cct_kelvin", None),
        "illuminance_lux": getattr(args, "illuminance_lux", None),
        "spectral_cri": getattr(args, "spectral_cri", None),
        "wall_surround": getattr(args, "wall_surround", None),
        "gallery_zone": getattr(args, "gallery_zone", None),
        "anchor_image_id": getattr(args, "anchor_image_id", None),
    }

    if getattr(args, "print_size", None):
        ps = args.print_size
        from .restoration import STANDARD_PRINT_SIZES
        from .models import PaperProfile, PrintSpec
        if ps in STANDARD_PRINT_SIZES:
            w, h, ppi = STANDARD_PRINT_SIZES[ps]
        elif "x" in ps and "@" in ps:
            dims, ppi_str = ps.split("@")
            w_str, h_str = dims.split("x")
            w, h, ppi = float(w_str), float(h_str), int(ppi_str)
        elif "x" in ps:
            w_str, h_str = ps.split("x")
            w, h, ppi = float(w_str), float(h_str), 300
        else:
            w, h, ppi = 16.0, 24.0, 300
        paper_enum = PaperProfile.from_str(getattr(args, "paper", None)) if getattr(args, "paper", None) else PaperProfile.LUSTER
        common_kwargs["print_spec"] = PrintSpec(width_in=w, height_in=h, ppi=ppi, paper=paper_enum)

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


def recon_4x_main(argv: Optional[list[str]] = None) -> int:
    """Dedicated CLI entrypoint for Professional 4X Reconstruction Lock Protocol."""
    parser = argparse.ArgumentParser(
        prog="optical-recon-4x",
        description="Professional 4X Reconstruction Lock and Super-Resolution Engine.",
    )
    parser.add_argument("image", help="Path to input image file.")
    parser.add_argument("-o", "--output", help="Optional destination output path.")
    parser.add_argument(
        "--backend",
        choices=["realesrnet_x4plus", "swinir_m_x4", "realesrgan_x4v3", "realesrgan_x4plus", "hat_s_x4", "pil_conservative"],
        default="realesrnet_x4plus",
        help="Super-resolution backend (default: realesrnet_x4plus).",
    )
    parser.add_argument("--denoise", type=float, default=0.15, help="Denoising strength (default: 0.15).")
    parser.add_argument("--blend", type=float, default=0.20, help="Detail blend ratio (default: 0.20).")
    parser.add_argument("--no-protect-sky", dest="protect_sky", action="store_false", default=True, help="Disable sky protection mask.")
    parser.add_argument("-f", "--format", choices=["png", "tiff", "tif", "jpeg", "jpg"], help="Output format.")
    parser.add_argument("--json", action="store_true", help="Output raw JSON execution report.")
    args = parser.parse_args(argv)

    try:
        from .restoration import execute_4x_reconstruction_lock
        rep, rep_d = execute_4x_reconstruction_lock(
            args.image,
            output_path=args.output,
            backend=args.backend,
            denoise_strength=args.denoise,
            blend_ratio=args.blend,
            protect_sky_haze=args.protect_sky,
            output_format=args.format,
            generate_report=True,
        )
        if args.json:
            print(json.dumps(rep_d, indent=2))
        else:
            print("=" * 80)
            print("PROFESSIONAL 4X RECONSTRUCTION LOCK ENGINE")
            print("=" * 80)
            print(f"Status:       {'PASSED (Verified 4X Linear Source Lock)' if rep.validation_passed else 'FAILED'}")
            print(f"Input:        {rep.input_path} ({rep.source_dimensions[0]}x{rep.source_dimensions[1]}, {rep.source_megapixels} MP)")
            print(f"Output:       {rep.output_path} ({rep.output_dimensions[0]}x{rep.output_dimensions[1]}, {rep.output_megapixels} MP)")
            print(f"Multiplier:   {rep.linear_multiplier}X linear ({rep.area_multiplier}X pixel area)")
            print(f"Backend:      {rep.backend} (denoise: {rep.denoise_strength}, detail blend: {rep.blend_ratio})")
            print(f"Sky & Haze:   {'PROTECTED (Gradient Mask)' if rep.sky_haze_protected else 'UNMASKED'}")
            print(f"File Size:    {rep.file_size_mb:.2f} MB ({rep.file_size_bytes:,} bytes)")
            print(f"SHA-256:      {rep.sha256}")
            print(f"Time:         {rep.execution_seconds:.4f}s")
            if rep.validation_failures:
                print(f"Failures:     {', '.join(rep.validation_failures)}")
        return 0 if rep.validation_passed else 1
    except Exception as err:
        sys.stderr.write(f"4X Reconstruction Error: {err}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
