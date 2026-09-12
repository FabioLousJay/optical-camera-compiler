"""Unit and integration tests for PFEP v1.0 and Closed-Loop Resolution Engine (v3.5)."""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from optical_compiler import (
    EXPORT_PROFILES,
    LightingEnvironmentSpec,
    OpticalCompiler,
    PrintSpec,
    RendererScorecard,
    RunReport,
    SceneInput,
    SeriesCohesionSpec,
    StressProbe,
    TargetEngine,
    add_micro_noise,
    compile_scene,
    export_closed_loop,
    inches_to_pixels,
    init_pfep_project,
    scale_multiplier_for_size,
    sha256_file,
    viewing_distance_inches,
)
from optical_compiler.cli import build_parser, main
from optical_compiler.comfy_nodes import (
    OpticalCameraCompilerNode,
    OpticalClosedLoopExporterNode,
)
from optical_compiler.restoration import PILLOW_AVAILABLE
from optical_compiler.web import StudioAPIHandler

if PILLOW_AVAILABLE:
    from PIL import Image


class TestPFEPModelsAndScorecard(unittest.TestCase):
    """Test StressProbe Enum and RendererScorecard hard-gated evaluation."""

    def test_stress_probe_aliases_and_directives(self) -> None:
        """Test parsing of all 10 canonical stress probes, aliases, and directives."""
        probes = [
            ("master_portrait_lock", StressProbe.MASTER_PORTRAIT_LOCK),
            ("master_lock", StressProbe.MASTER_PORTRAIT_LOCK),
            ("master", StressProbe.MASTER_PORTRAIT_LOCK),
            ("outpaint_lens_honest", StressProbe.OUTPAINT_LENS_HONEST),
            ("outpaint", StressProbe.OUTPAINT_LENS_HONEST),
            ("stress_hard_key", StressProbe.STRESS_HARD_KEY),
            ("hard_key", StressProbe.STRESS_HARD_KEY),
            ("stress_cross_polarized", StressProbe.STRESS_CROSS_POLARIZED),
            ("cross_polarized", StressProbe.STRESS_CROSS_POLARIZED),
            ("stress_glasses_reflections", StressProbe.STRESS_GLASSES_REFLECTIONS),
            ("glasses", StressProbe.STRESS_GLASSES_REFLECTIONS),
            ("stress_seated_compression", StressProbe.STRESS_SEATED_COMPRESSION),
            ("seated", StressProbe.STRESS_SEATED_COMPRESSION),
            ("stress_standing_compression", StressProbe.STRESS_STANDING_COMPRESSION),
            ("standing", StressProbe.STRESS_STANDING_COMPRESSION),
            ("stress_background_scale", StressProbe.STRESS_BACKGROUND_SCALE),
            ("background_scale", StressProbe.STRESS_BACKGROUND_SCALE),
            ("stress_hair_specular", StressProbe.STRESS_HAIR_SPECULAR),
            ("hair", StressProbe.STRESS_HAIR_SPECULAR),
            ("stress_shadow_color", StressProbe.STRESS_SHADOW_COLOR),
            ("shadow", StressProbe.STRESS_SHADOW_COLOR),
            ("none", StressProbe.NONE),
            ("", StressProbe.NONE),
            ("invalid_name", StressProbe.NONE),
        ]
        for name, expected in probes:
            self.assertEqual(StressProbe.from_str(name), expected)
            self.assertEqual(StressProbe.from_string(name), expected)

        # Verify directives are present and non-empty for all active probes
        for member in StressProbe:
            if member != StressProbe.NONE:
                self.assertTrue(len(member.directive_text) > 30)
                self.assertIn("PFEP Diagnostic Probe", member.directive_text)

    def test_renderer_scorecard_identity_hard_gate(self) -> None:
        """Test 8-axis scorecard and verify that identity == 2 is a non-negotiable hard gate."""
        # Case 1: High total score (14/16) but identity == 1 -> MUST FAIL
        card_fail = RendererScorecard(
            identity=1,
            focus=2,
            skin_texture=2,
            lighting_honesty=2,
            glasses=2,
            hair=2,
            geometry=2,
            background_scale=1,
        )
        self.assertEqual(card_fail.total_score, 14)
        self.assertFalse(card_fail.passed, "Scorecard must fail if identity != 2 even with 14/16")

        # Case 2: Zero identity (0/2) with otherwise perfect scores (14/16) -> MUST FAIL
        card_zero_id = RendererScorecard(
            identity=0,
            focus=2,
            skin_texture=2,
            lighting_honesty=2,
            glasses=2,
            hair=2,
            geometry=2,
            background_scale=2,
        )
        self.assertEqual(card_zero_id.total_score, 14)
        self.assertFalse(card_zero_id.passed)

        # Case 3: Identity == 2 and total == 11 -> MUST FAIL (< 12)
        card_low_total = RendererScorecard(
            identity=2,
            focus=2,
            skin_texture=1,
            lighting_honesty=1,
            glasses=1,
            hair=1,
            geometry=2,
            background_scale=1,
        )
        self.assertEqual(card_low_total.total_score, 11)
        self.assertFalse(card_low_total.passed)

        # Case 4: Identity == 2 and total == 12 -> PASS (Minimum threshold)
        card_pass_min = RendererScorecard(
            identity=2,
            focus=2,
            skin_texture=1,
            lighting_honesty=2,
            glasses=1,
            hair=1,
            geometry=2,
            background_scale=1,
        )
        self.assertEqual(card_pass_min.total_score, 12)
        self.assertTrue(card_pass_min.passed)

        # Case 5: Perfect run (16/16) -> PASS
        card_perfect = RendererScorecard(
            identity=2, focus=2, skin_texture=2, lighting_honesty=2,
            glasses=2, hair=2, geometry=2, background_scale=2,
        )
        self.assertEqual(card_perfect.total_score, 16)
        self.assertTrue(card_perfect.passed)

    def test_renderer_scorecard_aliases_and_formatting(self) -> None:
        """Test backward-compatible kwargs, property aliases, and markdown output."""
        card = RendererScorecard(
            identity=2,
            material_acutance=2,
            skin_micro_texture=2,
            lighting=2,
            optical_physics=2,
            hair_dynamics=2,
            geometry=2,
            color_fidelity=2,
            notes="Exquisite studio baseline test.",
        )
        self.assertEqual(card.total_score, 16)
        self.assertEqual(card.focus, 2)
        self.assertEqual(card.skin_texture, 2)
        self.assertEqual(card.lighting_honesty, 2)
        self.assertEqual(card.glasses, 2)
        self.assertEqual(card.hair, 2)
        self.assertEqual(card.background_scale, 2)

        data = card.to_dict()
        self.assertEqual(data["max_score"], 16)
        self.assertEqual(data["identity_gate_passed"], True)
        self.assertEqual(data["passed"], True)

        md = card.to_markdown()
        self.assertIn("### PFEP v1.0 Renderer Scorecard: **PASSED**", md)
        self.assertIn("16 / 16", md)
        self.assertIn("Exquisite studio baseline test", md)


class TestSizingAndClosedLoopExport(unittest.TestCase):
    """Test physical print sizing, heuristics, and closed-loop export engine."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_print_spec_and_sizing_formulas(self) -> None:
        """Test PrintSpec, inches_to_pixels, viewing distance, and scale multiplier."""
        # 1. PrintSpec and inches_to_pixels
        spec = PrintSpec(width_in=16.0, height_in=24.0, ppi=300)
        w, h = inches_to_pixels(spec)
        self.assertEqual((w, h), (4800, 7200))

        # Direct float call
        w2, h2 = inches_to_pixels(24.0, 36.0, ppi=240)
        self.assertEqual((w2, h2), (5760, 8640))

        # 2. Viewing distance (1.5x diagonal)
        vd = viewing_distance_inches(16.0, 24.0, 1.5)
        self.assertAlmostEqual(vd, 43.27, places=1)

        # 3. Sizing heuristic multiplier: sqrt(target / current)
        mult = scale_multiplier_for_size(8.0, 2.0)
        self.assertEqual(mult, 2.0)
        self.assertEqual(scale_multiplier_for_size(8.0, 8.0), 1.0)
        self.assertEqual(scale_multiplier_for_size(0.0, 2.0), 1.0)

        # 4. Export profiles
        self.assertEqual(EXPORT_PROFILES["A"]["dimensions"], (4000, 6000))
        self.assertEqual(EXPORT_PROFILES["B"]["dimensions"], (5000, 7500))
        self.assertEqual(EXPORT_PROFILES["C"]["dimensions"], (6000, 9000))

    def test_sha256_file(self) -> None:
        """Test SHA-256 digest computation."""
        import hashlib

        test_data = b"Optical Camera Compiler Provenance Engine"
        test_file = Path(self.temp_dir) / "test_data.bin"
        test_file.write_bytes(test_data)
        digest = sha256_file(test_file)
        self.assertEqual(len(digest), 64)
        self.assertEqual(digest, hashlib.sha256(test_data).hexdigest())

    @unittest.skipUnless(PILLOW_AVAILABLE, "Pillow is required for image operations")
    def test_add_micro_noise(self) -> None:
        """Test micro-noise entropy injection."""
        img = Image.new("RGB", (64, 64), color=(128, 128, 128))
        noisy = add_micro_noise(img, strength=2)
        self.assertEqual(noisy.size, (64, 64))
        self.assertEqual(noisy.mode, "RGB")

    @unittest.skipUnless(PILLOW_AVAILABLE, "Pillow is required for closed-loop export tests")
    def test_export_closed_loop_execution(self) -> None:
        """Test closed-loop export with machine-verifiable constraints, reports, and provenance."""
        in_path = Path(self.temp_dir) / "source.png"
        img = Image.new("RGB", (100, 150), color=(200, 50, 50))
        img.save(in_path, format="PNG")

        out_path = Path(self.temp_dir) / "out" / "result.png"

        run_report, rep_dict = export_closed_loop(
            input_path=in_path,
            output_path=out_path,
            target_width=400,
            target_height=600,
            ppi=300,
            min_mb=0.01,
            output_format="PNG",
            add_noise=True,
            generate_report=True,
        )

        self.assertTrue(out_path.exists())
        self.assertTrue(run_report.passed_constraints)
        self.assertEqual(run_report.output_dimensions, (400, 600))
        self.assertEqual(run_report.target_ppi, 300)
        self.assertEqual(run_report.sha256, sha256_file(out_path))

        report_md = out_path.parent / "EXPORT_REPORT.md"
        prov_json = out_path.parent / "PROVENANCE.json"
        self.assertTrue(report_md.exists())
        self.assertTrue(prov_json.exists())

        md_content = report_md.read_text(encoding="utf-8")
        self.assertIn("Closed-Loop Export & Provenance Report", md_content)
        self.assertIn(run_report.sha256, md_content)

        prov_data = json.loads(prov_json.read_text(encoding="utf-8"))
        self.assertEqual(prov_data["output_dimensions"], [400, 600])
        self.assertEqual(prov_data["sha256"], run_report.sha256)

    @unittest.skipUnless(PILLOW_AVAILABLE, "Pillow is required for closed-loop export tests")
    def test_export_closed_loop_profile(self) -> None:
        """Test export_closed_loop using predefined export profiles."""
        in_path = Path(self.temp_dir) / "profile_src.png"
        img = Image.new("RGB", (50, 50), color=(10, 20, 30))
        img.save(in_path, format="PNG")

        out_path = Path(self.temp_dir) / "out_profile" / "profile_a.png"
        run_report, _ = export_closed_loop(
            input_path=in_path,
            output_path=out_path,
            profile="A",
            generate_report=False,
        )
        self.assertEqual(run_report.output_dimensions, (400, 600))
        self.assertTrue(out_path.exists())


class TestPFEPProjectScaffolding(unittest.TestCase):
    """Test PFEP project directory scaffolding and compact prompt pack."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_pfep_project(self) -> None:
        """Test init_pfep_project creates all 15 files and canonical prompt packs."""
        workspace = Path(self.temp_dir) / "pfep_test_workspace"
        created_files = init_pfep_project(workspace)
        self.assertEqual(len(created_files), 15)

        # Check directories
        self.assertTrue((workspace / "00_inputs").is_dir())
        self.assertTrue((workspace / "01_prompts").is_dir())
        self.assertTrue((workspace / "02_runs" / "run_001").is_dir())
        self.assertTrue((workspace / "03_selected").is_dir())
        self.assertTrue((workspace / "04_converged").is_dir())

        # Check PFEP README
        self.assertTrue((workspace / "PFEP_README.md").exists())
        readme_text = (workspace / "PFEP_README.md").read_text(encoding="utf-8")
        self.assertIn("Portrait Fidelity Engineering Protocol (PFEP v1.0)", readme_text)
        self.assertIn("Identity Is a Hard Gate", readme_text)

        # Check prompt files
        prompts = list((workspace / "01_prompts").glob("*.txt"))
        self.assertEqual(len(prompts), 10)
        master_prompt = (workspace / "01_prompts" / "01_MASTER_PORTRAIT_LOCK.txt").read_text(encoding="utf-8")
        self.assertIn("MASTER PORTRAIT LOCK", master_prompt)
        self.assertIn("Sony a1 II", master_prompt)
        self.assertIn("Phase One XF", master_prompt)

        # Check run log
        run_log = workspace / "02_runs" / "run_001" / "notes.md"
        self.assertTrue(run_log.exists())
        log_text = run_log.read_text(encoding="utf-8")
        self.assertIn("8-Axis Renderer Scorecard", log_text)


class TestTargetAdaptersPFEPAndExhibition(unittest.TestCase):
    """Test all 7 target adapters for PFEP probe and exhibition lighting injection."""

    def setUp(self) -> None:
        self.scene = SceneInput(
            subject="Senior architect portrait with titanium spectacles",
            aspect_ratio="4:5",
            stress_probe=StressProbe.STRESS_GLASSES_REFLECTIONS,
            min_file_mb=8.0,
            lighting_environment=LightingEnvironmentSpec(
                cct_kelvin=5500,
                illuminance_lux=450,
                spectral_cri=99.0,
                wall_surround="Neutral Matte Gray 18%",
            ),
            series_cohesion=SeriesCohesionSpec(
                anchor_image_id="PORTRAIT_ANCHOR_01",
                gallery_zone="Gallery Zone A (North Atrium)",
            ),
        )

    def test_gpt_images_adapter(self) -> None:
        payload = compile_scene(self.scene, target_model=TargetEngine.GPT_IMAGES)
        prompt = payload.positive_prompt
        self.assertIn("PFEP Diagnostic Probe [05: Glasses Reflections Stress]", prompt)
        self.assertIn("Exhibition Lighting Calibration", prompt)
        self.assertIn("5500K", prompt)
        self.assertIn("450 lux", prompt)
        self.assertIn("Series Cohesion Protocol", prompt)
        self.assertIn("PORTRAIT_ANCHOR_01", prompt)
        self.assertIn("Closed-Loop Output Constraint", prompt)
        self.assertIn("8.0 MB", prompt)

    def test_imagen_adapter(self) -> None:
        payload = compile_scene(self.scene, target_model=TargetEngine.IMAGEN)
        prompt = payload.positive_prompt
        self.assertIn("PFEP Diagnostic Probe [05: Glasses Reflections Stress]", prompt)
        self.assertIn("Exhibition lighting calibrated", prompt)
        self.assertIn("5500K", prompt)
        self.assertIn("Series visual cohesion anchored to PORTRAIT_ANCHOR_01", prompt)
        self.assertIn("Minimum uncompressed output target: 8.0 MB", prompt)

    def test_midjourney_adapter(self) -> None:
        payload = compile_scene(self.scene, target_model=TargetEngine.MIDJOURNEY)
        prompt = payload.positive_prompt
        self.assertIn("PFEP Diagnostic Probe [05: Glasses Reflections Stress]", prompt)
        self.assertIn("gallery exhibition lighting 450 lux 5500K CRI 99.0", prompt)
        self.assertIn("series cohesion anchor PORTRAIT_ANCHOR_01", prompt)

    def test_flux_adapter(self) -> None:
        payload = compile_scene(self.scene, target_model=TargetEngine.FLUX)
        prompt = payload.positive_prompt
        self.assertIn("PFEP Diagnostic Probe [05: Glasses Reflections Stress]", prompt)
        self.assertIn("Exhibition lighting calibrated for gallery display", prompt)
        self.assertIn("Series visual cohesion anchored to PORTRAIT_ANCHOR_01", prompt)

    def test_sdxl_adapter(self) -> None:
        payload = compile_scene(self.scene, target_model=TargetEngine.SDXL)
        prompt = payload.positive_prompt
        self.assertIn("PFEP Diagnostic Probe [05: Glasses Reflections Stress]", prompt)
        self.assertIn("gallery lighting 450 lux, 5500K CCT, CRI 99.0", prompt)
        self.assertIn("series cohesion anchor PORTRAIT_ANCHOR_01", prompt)

    def test_raw_spec_adapter(self) -> None:
        payload = compile_scene(self.scene, target_model=TargetEngine.RAW)
        prompt = payload.positive_prompt
        self.assertIn("--- PFEP v1.0 Diagnostic Stress Probe ---", prompt)
        self.assertIn("PFEP Diagnostic Probe [05: Glasses Reflections Stress]", prompt)
        self.assertIn("--- Exhibition Lighting Environment & Spectral Calibration ---", prompt)
        self.assertIn("Color Temperature: 5500K CCT", prompt)
        self.assertIn("--- Exhibition Series Visual Cohesion Matrix ---", prompt)
        self.assertIn("Anchor Image ID: PORTRAIT_ANCHOR_01", prompt)
        self.assertIn("Minimum File Size: 8.0 MB", prompt)

    def test_json_prompt_adapter(self) -> None:
        payload = compile_scene(self.scene, target_model=TargetEngine.JSON_PROMPT)
        data = json.loads(payload.positive_prompt)
        self.assertEqual(data["schema_version"], "3.5")
        self.assertIn("PFEP v1.0", data["protocol"])
        self.assertIn("pfep_diagnostic_probe", data)
        self.assertEqual(data["pfep_diagnostic_probe"]["probe_id"], "stress_glasses_reflections")
        self.assertIn("exhibition_lighting_environment", data)
        self.assertEqual(data["exhibition_lighting_environment"]["cct_kelvin"], 5500)
        self.assertIn("series_visual_cohesion", data)
        self.assertEqual(data["series_visual_cohesion"]["anchor_image_id"], "PORTRAIT_ANCHOR_01")
        self.assertIn("closed_loop_constraints", data)
        self.assertEqual(data["closed_loop_constraints"]["min_file_mb"], 8.0)


class TestCLIAndComfyNodes(unittest.TestCase):
    """Test CLI flags and ComfyUI node integration."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_parser_and_flags(self) -> None:
        """Verify new CLI flags parse cleanly."""
        parser = build_parser()
        args = parser.parse_args([
            "Studio portrait of sculptor",
            "--probe", "stress_hard_key",
            "--min-mb", "8.5",
            "--cct", "5200",
            "--lux", "600",
            "--cri", "98.5",
            "--wall-surround", "Deep Neutral Gray",
            "--gallery-zone", "Zone C",
            "--anchor-id", "ANCHOR_09",
            "--export-profile", "B",
        ])
        self.assertEqual(args.probe, "stress_hard_key")
        self.assertEqual(args.min_mb, 8.5)
        self.assertEqual(args.cct_kelvin, 5200)
        self.assertEqual(args.illuminance_lux, 600)
        self.assertEqual(args.spectral_cri, 98.5)
        self.assertEqual(args.wall_surround, "Deep Neutral Gray")
        self.assertEqual(args.gallery_zone, "Zone C")
        self.assertEqual(args.anchor_image_id, "ANCHOR_09")
        self.assertEqual(args.export_profile, "B")

    def test_comfy_compiler_node(self) -> None:
        """Test OpticalCameraCompilerNode compiles scene with probe and exhibition settings."""
        node = OpticalCameraCompilerNode()
        pos, neg, unified = node.compile_optical_prompt(
            subject="Gallery portrait",
            model_target="gpt_images",
            camera_rig="Phase One IQ4 150MP Commercial",
            stress_probe="stress_cross_polarized",
            min_mb=12.0,
            cct_kelvin=5000,
            illuminance_lux=500,
            gallery_zone="Zone B",
            anchor_image_id="ANCHOR_42",
        )
        self.assertIn("PFEP Diagnostic Probe [04: Cross-Polarized Surface Stress]", pos)
        self.assertIn("Exhibition Lighting Calibration", pos)
        self.assertIn("5000K", pos)
        self.assertIn("12.0 MB", pos)

    @unittest.skipUnless(PILLOW_AVAILABLE, "Pillow is required for ComfyUI exporter node test")
    def test_comfy_closed_loop_exporter_node(self) -> None:
        """Test OpticalClosedLoopExporterNode executes export."""
        in_path = Path(self.temp_dir) / "comfy_src.png"
        Image.new("RGB", (80, 80), color=(100, 150, 200)).save(in_path, format="PNG")
        out_path = Path(self.temp_dir) / "comfy_out.png"

        node = OpticalClosedLoopExporterNode()
        res_path, sha, md, mb, passed = node.export_image(
            image_path=str(in_path),
            output_path=str(out_path),
            target_width=160,
            target_height=160,
            ppi=300,
            output_format="PNG",
        )
        self.assertTrue(Path(res_path).exists())
        self.assertEqual(len(sha), 64)
        self.assertTrue(passed)
        self.assertIn("Closed-Loop Export & Provenance Report", md)


if __name__ == "__main__":
    unittest.main()
