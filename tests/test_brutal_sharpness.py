"""Unit tests for the Brutal Sharpness Protocol, new 2026 profiles, and GPT Images adapter."""

from __future__ import annotations

import unittest

from optical_compiler.compiler import OpticalCompiler, compile_ab_harness
from optical_compiler.comfy_nodes import OpticalCameraCompilerNode
from optical_compiler.models import ReferenceImageInput, ReferenceMode, SceneInput, TargetEngine
from optical_compiler.profiles import list_available_profiles, load_profile


class TestBrutalSharpnessKit(unittest.TestCase):
    """Test coverage for all features introduced from the Brutal Sharpness Portrait Kit."""

    def setUp(self) -> None:
        self.compiler = OpticalCompiler()

    def test_new_profiles_exist_and_load(self) -> None:
        """Verify Sony a1 II, Canon EOS R5 Mark II, and Nikon Z 9 profiles load properly."""
        available = list_available_profiles()
        profile_ids = [p["id"] for p in available]
        self.assertIn("sony_a1_ii", profile_ids)
        self.assertIn("canon_eos_r5_ii", profile_ids)
        self.assertIn("nikon_z9", profile_ids)
        self.assertIn("sony_fx_series", profile_ids)
        self.assertGreaterEqual(len(available), 14)

        # Verify Sony FX Cinema Line
        fx = load_profile("sony_fx_series")
        self.assertIn("Sony FX Cinema Line", fx.sensor_and_optics.camera_system)
        self.assertIn("f/2.8", fx.sensor_and_optics.aperture_sweet_spot)
        self.assertIn("180-degree", fx.sensor_and_optics.shutter)
        self.assertIn("broadcast video sharpness", fx.negative_embeddings.skin_and_lighting_drift)

        # Verify Sony a1 II
        sony = load_profile("sony_a1_ii")
        self.assertIn("Sony a1 II", sony.sensor_and_optics.camera_system)
        self.assertIn("50.1MP", sony.sensor_and_optics.sensor_dimensions)
        self.assertIn("1/400s", sony.sensor_and_optics.shutter)
        self.assertIn("FE 85mm F1.4 GM II", sony.sensor_and_optics.lens)

        # Verify Canon EOS R5 Mark II
        canon = load_profile("canon_eos_r5_ii")
        self.assertIn("Canon EOS R5 Mark II", canon.sensor_and_optics.camera_system)
        self.assertIn("45.0MP", canon.sensor_and_optics.sensor_dimensions)
        self.assertIn("RF 85mm F1.2L USM", canon.sensor_and_optics.lens)

        # Verify Nikon Z 9
        nikon = load_profile("nikon_z9")
        self.assertIn("Nikon Z 9", nikon.sensor_and_optics.camera_system)
        self.assertIn("45.7MP", nikon.sensor_and_optics.sensor_dimensions)
        self.assertIn("NIKKOR Z 135mm f/1.8 S Plena", nikon.sensor_and_optics.lens)

    def test_all_13_profiles_compile_across_targets(self) -> None:
        """Verify that all profiles compile without error across all supported engines."""
        available = list_available_profiles()
        profile_ids = [p["id"] for p in available]
        self.assertGreaterEqual(len(profile_ids), 14)
        targets = [
            TargetEngine.GPT_IMAGES,
            TargetEngine.IMAGEN,
            TargetEngine.MIDJOURNEY,
            TargetEngine.FLUX,
            TargetEngine.SDXL,
            TargetEngine.RAW,
            TargetEngine.JSON_PROMPT,
        ]

        for p_id in profile_ids:
            c = OpticalCompiler(profile=p_id)
            for t in targets:
                payload = c.compile("Editorial fashion portrait of a model", target=t)
                self.assertIsNotNone(payload.positive_prompt)
                self.assertGreater(len(payload.positive_prompt), 20)
                self.assertEqual(payload.target_engine, t)

    def test_gpt_images_master_execution_structure(self) -> None:
        """Verify the GPT Images adapter produces the Page 17 Master Execution Prompt layout."""
        c = OpticalCompiler(profile="sony_a1_ii")
        payload = c.compile(
            "Sculptor with clay-dusted hands looking directly into lens",
            target="gpt_images",
            output_resolution="12MP PNG (3132x3828, 9:11)",
            sharpness_protocol=True,
            suppress_text_branding=True,
        )

        prompt = payload.positive_prompt
        self.assertIn("Subject: Sculptor with clay-dusted hands", prompt)
        self.assertIn("Focus discipline: Focus locked on the near eye", prompt)
        self.assertIn("Surface rendering: Natural human skin with visible pores", prompt)
        self.assertIn("Lighting geometry:", prompt)
        self.assertIn("Camera hardware: Shot on Sony a1 II", prompt)
        self.assertIn("Output specification: 12MP PNG (3132x3828, 9:11)", prompt)
        self.assertIn("Hard negative constraints (MUST ELIMINATE):", prompt)
        self.assertIn("watermark, logo, brand name, typography", prompt)
        self.assertIn("plastic skin, oversmoothed skin, airbrushed skin", prompt)

    def test_gpt_images_custom_resolutions(self) -> None:
        """Verify GPT Images handles 8K UHD and common aspect ratio resolutions."""
        c = OpticalCompiler(profile="canon_eos_r5_ii")
        payload_8k = c.compile(
            "Architect in studio",
            target="gpt_images",
            output_resolution="8K UHD (7680x4320, 16:9)",
        )
        self.assertIn("Output specification: 8K UHD (7680x4320, 16:9)", payload_8k.positive_prompt)

        payload_4k = c.compile(
            "Architect in studio",
            target="gpt_images",
            output_resolution="4K UHD (3840x2160, 16:9)",
        )
        self.assertIn("Output specification: 4K UHD (3840x2160, 16:9)", payload_4k.positive_prompt)

    def test_brutal_sharpness_protocol_injections(self) -> None:
        """Verify near-eye focus lock and optical stability cues are injected."""
        c = OpticalCompiler(profile="nikon_z9")
        
        # Test SDXL target with sharpness protocol
        payload_sdxl = c.compile(
            "Elderly watchmaker inspecting clockwork",
            target="sdxl",
            sharpness_protocol=True,
        )
        self.assertIn("focus locked on near eye, iris and eyelashes tack sharp", payload_sdxl.positive_prompt)
        self.assertIn("resolved epidermal skin pores", payload_sdxl.positive_prompt)

        # Test Midjourney target with sharpness protocol
        payload_mj = c.compile(
            "Elderly watchmaker inspecting clockwork",
            target="midjourney",
            sharpness_protocol=True,
        )
        self.assertIn("focus locked on near eye", payload_mj.positive_prompt)
        self.assertIn("eyelashes tack sharp", payload_mj.positive_prompt)

    def test_anti_brand_shield_suppression(self) -> None:
        """Verify that suppress_text_branding removes logos, text, and typography drift."""
        c = OpticalCompiler(profile="phase_one_iq4")
        
        # Test Midjourney --no parameter
        payload_mj = c.compile(
            "Athlete in sportswear",
            target="midjourney",
            suppress_text_branding=True,
        )
        self.assertIn("--no", payload_mj.positive_prompt)
        self.assertIn("watermark", payload_mj.positive_prompt)
        self.assertIn("logo", payload_mj.positive_prompt)
        self.assertIn("brand", payload_mj.positive_prompt)
        self.assertIn("typography", payload_mj.positive_prompt)

        # Test SDXL negative prompt
        payload_sdxl = c.compile(
            "Athlete in sportswear",
            target="sdxl",
            suppress_text_branding=True,
        )
        self.assertIn("watermark", payload_sdxl.negative_prompt)
        self.assertIn("trademark", payload_sdxl.negative_prompt)
        self.assertIn("brand name", payload_sdxl.negative_prompt)
        self.assertIn("logo", payload_sdxl.negative_prompt)

    def test_mode_c_outpaint_full_body(self) -> None:
        """Verify Mode C outpainting instructions across adapters."""
        c = OpticalCompiler(profile="sony_a1_ii")
        ref = ReferenceImageInput(mode=ReferenceMode.OUTPAINT_FULL_BODY)

        # GPT Images outpainting
        payload_gpt = c.compile(
            "Close-up headshot of a ballerina",
            target="gpt_images",
            reference=ref,
        )
        self.assertIn("Outpaint and extend the frame downward into a full-body portrait", payload_gpt.positive_prompt)
        self.assertIn("Full body head-to-toe visible including shoes", payload_gpt.positive_prompt)

        # Imagen outpainting
        payload_imagen = c.compile(
            "Close-up headshot of a ballerina",
            target="imagen",
            reference=ref,
        )
        self.assertIn("Outpaint and extend the frame downward to a full-body portrait", payload_imagen.positive_prompt)
        self.assertIn("Preserve the subject's face, identity", payload_imagen.positive_prompt)

        # Midjourney outpainting
        payload_mj = c.compile(
            "Close-up headshot of a ballerina",
            target="midjourney",
            reference=ref,
        )
        self.assertIn("full body downward outpaint extension", payload_mj.positive_prompt)

        # Flux outpainting
        payload_flux = c.compile(
            "Close-up headshot of a ballerina",
            target="flux",
            reference=ref,
        )
        self.assertIn("Outpaint and extend the frame downward to a full-body portrait", payload_flux.positive_prompt)

    def test_compile_ab_harness(self) -> None:
        """Verify side-by-side Module A vs Module B harness generation."""
        harness = compile_ab_harness(
            scene="Surgeon in sterile scrub room",
            module_a="sony_a1_ii",
            module_b="canon_eos_r5_ii",
            target="gpt_images",
            sharpness_protocol=True,
            output_resolution="12MP PNG (3132x3828, 9:11)",
        )

        self.assertIn("module_a", harness)
        self.assertIn("module_b", harness)
        self.assertEqual(harness["camera_a"], "Sony a1 II Stacked Full-Frame (ILCE-1M2)")
        self.assertEqual(harness["camera_b"], "Canon EOS R5 Mark II Stacked Full-Frame")
        self.assertIn("Sony a1 II (ILCE-1M2)", harness["module_a"].positive_prompt)
        self.assertIn("Canon EOS R5 Mark II", harness["module_b"].positive_prompt)
        self.assertIn("Output specification: 12MP PNG", harness["module_a"].positive_prompt)
        self.assertIn("Output specification: 12MP PNG", harness["module_b"].positive_prompt)

    def test_comfy_node_registration(self) -> None:
        """Verify ComfyUI node exposes all new cameras, targets, and options."""
        input_types = OpticalCameraCompilerNode.INPUT_TYPES()
        required = input_types["required"]
        optional = input_types["optional"]

        camera_list = required["camera_rig"][0]
        self.assertIn("Sony a1 II Stacked Full-Frame (ILCE-1M2)", camera_list)
        self.assertIn("Canon EOS R5 Mark II Stacked Full-Frame", camera_list)
        self.assertIn("Nikon Z 9 Stacked Flagship Full-Frame", camera_list)
        self.assertIn("Sony FX Cinema Line Full-Frame (Venice S-Log3)", camera_list)

        target_list = required["model_target"][0]
        self.assertEqual(target_list[0], "gpt_images")
        self.assertIn("imagen", target_list)
        self.assertIn("midjourney", target_list)
        self.assertIn("json", target_list)

        ref_mode_list = optional["reference_mode"][0]
        self.assertIn("outpaint_full_body", ref_mode_list)

        aspect_ratios = optional["aspect_ratio"][0]
        self.assertIn("9:11", aspect_ratios)

        self.assertIn("brutal_sharpness_protocol", optional)
        self.assertIn("suppress_text_branding", optional)


if __name__ == "__main__":
    unittest.main()
