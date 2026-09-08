"""Comprehensive test suite for the Optical Camera Compiler."""

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from optical_compiler.cli import main
from optical_compiler.compiler import OpticalCompiler
from optical_compiler.models import SceneInput, TargetEngine
from optical_compiler.profiles import apply_overrides, load_profile


class TestOpticalCompiler(unittest.TestCase):
    """Test suite for compiler models, profile loaders, and target adapters."""

    def setUp(self) -> None:
        self.compiler = OpticalCompiler(profile="phase_one_iq4")

    def test_load_default_profile(self) -> None:
        """Verify Phase One IQ4 profile is properly loaded with all hardware specs."""
        profile = load_profile("phase_one_iq4")
        self.assertEqual(profile.profile_id, "phase_one_iq4")
        self.assertIn("Phase One XF IQ4", profile.sensor_and_optics.camera_system)
        self.assertEqual(profile.sensor_and_optics.aperture_sweet_spot, "f/8")
        self.assertIn("1/1600s", profile.sensor_and_optics.shutter)
        self.assertIn("CGI", profile.negative_embeddings.render_defects)
        self.assertIn("airbrushed skin", profile.negative_embeddings.skin_and_lighting_drift)

    def test_apply_overrides(self) -> None:
        """Verify optical and scene overrides cleanly update profile without mutating original."""
        base = load_profile("phase_one_iq4")
        scene = SceneInput(
            subject="Studio model",
            aperture="f/2.8",
            lens="Schneider Kreuznach 150mm LS f/3.5",
            lighting="Daylight soft diffusion through north-facing skylight",
            custom_negatives=["harsh neon glare"],
        )

        overridden = apply_overrides(base, scene)
        self.assertEqual(overridden.sensor_and_optics.aperture_sweet_spot, "f/2.8")
        self.assertEqual(overridden.sensor_and_optics.lens, "Schneider Kreuznach 150mm LS f/3.5")
        self.assertEqual(overridden.lighting_and_exposure.primary_lighting, scene.lighting)
        self.assertIn("harsh neon glare", overridden.negative_embeddings.render_defects)

        # Confirm original base was not mutated
        self.assertEqual(base.sensor_and_optics.aperture_sweet_spot, "f/8")

    def test_imagen_compilation(self) -> None:
        """Verify Imagen 3 adapter produces cohesive photographic prose."""
        payload = self.compiler.compile(
            "Architect examining blueprints",
            target="imagen",
            framing="waist-up portrait",
            environment="concrete Brutalist library",
            aperture="f/5.6",
        )

        self.assertEqual(payload.target_engine, TargetEngine.IMAGEN)
        self.assertIn("Phase One XF IQ4", payload.positive_prompt)
        self.assertIn("f/5.6", payload.positive_prompt)
        self.assertIn("concrete Brutalist library", payload.positive_prompt)
        self.assertIn("Natural epidermal skin texture", payload.positive_prompt)
        self.assertIn("subsurface scattering", payload.positive_prompt)
        self.assertIn("airbrushed skin", payload.negative_prompt)
        self.assertEqual(payload.parameters["aspect_ratio"], "4:5")

    def test_flux_compilation(self) -> None:
        """Verify Flux adapter produces technical direct physical declarations."""
        payload = self.compiler.compile(
            "Sculptor with marble dust on hands",
            target="flux",
            framing="tight macro headshot",
            mood="intense contemplation",
        )

        self.assertEqual(payload.target_engine, TargetEngine.FLUX)
        self.assertIn("Photo of tight macro headshot of Sculptor", payload.positive_prompt)
        self.assertIn("Phase One XF IQ4", payload.positive_prompt)
        self.assertIn("Schneider Kreuznach 80mm", payload.positive_prompt)
        self.assertIn("1/1600s", payload.positive_prompt)
        # Verify negative assertions woven directly into the positive text
        self.assertIn("Eliminate plastic or poreless airbrushed skin", payload.positive_prompt)
        self.assertEqual(payload.parameters["guidance_scale"], 3.5)

    def test_sdxl_compilation(self) -> None:
        """Verify SDXL dual-channel positive and negative prompt construction."""
        payload = self.compiler.compile(
            "Watchmaker repairing mechanical tourbillon",
            target="sdxl",
            aspect_ratio="16:9",
        )

        self.assertEqual(payload.target_engine, TargetEngine.SDXL)
        self.assertIn("raw photograph captured on Phase One XF IQ4", payload.positive_prompt)
        self.assertIn("resolved epidermal skin pores", payload.positive_prompt)
        self.assertIn("computational bokeh", payload.negative_prompt)
        self.assertIn("airbrushed skin", payload.negative_prompt)
        self.assertEqual(payload.parameters["width"], 1344)
        self.assertEqual(payload.parameters["height"], 768)

    def test_midjourney_compilation(self) -> None:
        """Verify Midjourney adapter includes --style raw, --v 6.1, --ar, and --no flags."""
        payload = self.compiler.compile(
            "Ballet dancer in rehearsal",
            target="midjourney",
            aspect_ratio="1:1",
        )

        self.assertEqual(payload.target_engine, TargetEngine.MIDJOURNEY)
        self.assertIn("--style raw", payload.positive_prompt)
        self.assertIn("--v 6.1", payload.positive_prompt)
        self.assertIn("--ar 1:1", payload.positive_prompt)
        self.assertIn("--no", payload.positive_prompt)
        self.assertIn("plastic skin", payload.positive_prompt)

    def test_raw_spec_compilation(self) -> None:
        """Verify Raw Spec adapter outputs structured hardware profile."""
        payload = self.compiler.compile(
            "Ceramist at pottery wheel",
            target="raw",
        )

        self.assertEqual(payload.target_engine, TargetEngine.RAW)
        self.assertIn("=== OPTICAL RIG SPECIFICATION", payload.positive_prompt)
        self.assertIn("Phase One XF IQ4 150MP", payload.positive_prompt)
        self.assertIn("Sensor & Optics", payload.positive_prompt)

    def test_compile_all(self) -> None:
        """Verify compile_all generates payloads for all four major target engines."""
        results = self.compiler.compile_all("Surgeon in sterile scrub room")
        self.assertIn("imagen", results)
        self.assertIn("flux", results)
        self.assertIn("sdxl", results)
        self.assertIn("midjourney", results)
        self.assertEqual(results["flux"].target_engine, TargetEngine.FLUX)

    def test_cli_execution(self) -> None:
        """Verify CLI outputs expected JSON and text formatted results."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = main(["Elderly fisherman with weathered face", "--target", "flux", "--json"])

        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        data = json.loads(output)
        self.assertEqual(data["target_engine"], "flux")
        self.assertIn("Phase One XF IQ4", data["positive_prompt"])

    def test_unified_prompt(self) -> None:
        """Verify unified_prompt appends the anti-artifact shield across target engines."""
        # Imagen
        p_imagen = self.compiler.compile("Test subject", target="imagen")
        self.assertIn("[ANTI-ARTIFACT NEGATIVE SHIELD]:", p_imagen.unified_prompt)
        self.assertTrue(p_imagen.unified_prompt.startswith(p_imagen.positive_prompt))
        self.assertIn(p_imagen.negative_prompt, p_imagen.unified_prompt)

        # Flux
        p_flux = self.compiler.compile("Test subject", target="flux")
        self.assertIn("[ANTI-ARTIFACT NEGATIVE SHIELD]:", p_flux.unified_prompt)
        self.assertTrue(p_flux.unified_prompt.startswith(p_flux.positive_prompt))

        # SDXL
        p_sdxl = self.compiler.compile("Test subject", target="sdxl")
        self.assertIn("Negative prompt:", p_sdxl.unified_prompt)
        self.assertTrue(p_sdxl.unified_prompt.startswith(p_sdxl.positive_prompt))
        self.assertIn(p_sdxl.negative_prompt, p_sdxl.unified_prompt)

        # Midjourney
        p_mj = self.compiler.compile("Test subject", target="midjourney")
        self.assertEqual(p_mj.unified_prompt, p_mj.positive_prompt)
        self.assertIn("--no", p_mj.unified_prompt)


if __name__ == "__main__":
    unittest.main()
