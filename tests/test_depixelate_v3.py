"""Tests for Universal De-Pixelate + Upscale Restoration v3.1 (GFX100RF & Skin Realism)."""

import json
import unittest
from pathlib import Path

from optical_compiler import (
    ContentType,
    OpticalCompiler,
    ReferenceImageInput,
    ReferenceMode,
    SceneInput,
    TargetEngine,
    compile_scene,
    load_profile,
)
from optical_compiler.profiles import auto_select_profile
from optical_compiler.restoration import RestorationConfig, restore_and_upscale_102mp, PILLOW_AVAILABLE


class TestDepixelateGFX100RFv3(unittest.TestCase):
    """Test suite validating GFX100RF 102MP Signature Lock and Skin Realism Override v3.1."""

    def test_gfx100rf_profile_specifications(self) -> None:
        """Verify the Fujifilm GFX100RF profile contains the exact hardware and color science specs."""
        profile = load_profile("fujifilm_gfx100rf")
        self.assertEqual(profile.profile_id, "fujifilm_gfx100rf")
        self.assertIn("Fujifilm GFX100RF", profile.sensor_and_optics.camera_system)
        self.assertIn("102 megapixels", profile.sensor_and_optics.sensor_dimensions)
        self.assertIn("Fujinon 35mm f/4", profile.sensor_and_optics.lens)
        self.assertIn("Reala Ace", profile.sensor_and_optics.dynamic_range)
        self.assertIn("Leaf shutter", profile.sensor_and_optics.shutter)

        # Check negative embeddings include skin realism protections
        all_negs = " ".join(profile.negative_embeddings.all_tokens(include_skin_realism=True)).lower()
        self.assertIn("pore stamping", all_negs)
        self.assertIn("plastic skin", all_negs)
        self.assertIn("wax skin", all_negs)
        self.assertIn("ai skin grain", all_negs)

    def test_router_depixelate_lock(self) -> None:
        """Verify intelligent router selects fujifilm_gfx100rf on depixelate mode or keywords."""
        # Keyword test
        routed = auto_select_profile("street documentary candid portrait depixelate upscale")
        self.assertEqual(routed, "fujifilm_gfx100rf")

        # ReferenceMode test
        scene = SceneInput(
            subject="Archived low-res headshot",
            reference=ReferenceImageInput(
                filename="archived_sample.jpg",
                mode=ReferenceMode.DEPIXELATE_GFX100RF,
            ),
        )
        routed_mode = auto_select_profile(scene)
        self.assertEqual(routed_mode, "fujifilm_gfx100rf")

    def test_compiler_automatic_profile_override(self) -> None:
        """Verify compiler forces fujifilm_gfx100rf when DEPIXELATE_GFX100RF mode is active."""
        compiler = OpticalCompiler(profile="sony_a1_ii")  # start with different profile
        payload = compiler.compile(
            scene="Portrait of a young architect",
            target="gpt_images",
            reference={
                "filename": "low_res_portrait.jpg",
                "mode": "depixelate_gfx100rf",
                "fidelity_lock": 0.95,
            },
        )
        self.assertEqual(payload.metadata.get("hardware_profile"), "fujifilm_gfx100rf")
        self.assertIn("Fujifilm GFX100RF", payload.positive_prompt)
        self.assertIn("102MP", payload.positive_prompt)
        self.assertIn("Human skin realism override protocol", payload.positive_prompt)

    def test_gpt_images_depixelate_adapter(self) -> None:
        """Verify GPT Images adapter produces the v3.1 restoration protocol."""
        compiler = OpticalCompiler(profile="fujifilm_gfx100rf")
        payload = compiler.compile(
            scene="Editorial portrait with low-resolution compression",
            target="gpt_images",
            reference={
                "filename": "ref.png",
                "mode": "depixelate_gfx100rf",
            },
            human_skin_realism=True,
            content_type="portrait",
        )
        prompt = payload.positive_prompt
        self.assertIn("Universal De-Pixelate + Upscale Restoration v3.1 – GFX100RF Signature Lock", prompt)
        self.assertIn("Human skin realism override protocol", prompt)
        self.assertIn("11648 x 8736", prompt)
        self.assertIn("Fujinon 35mm f/4", prompt)
        self.assertIn("Reala Ace", prompt)
        self.assertIn("Hard negative constraints (MUST ELIMINATE)", prompt)

    def test_imagen_depixelate_adapter(self) -> None:
        """Verify Imagen/Gemini adapter produces 102MP GFX100RF directives and skin realism."""
        compiler = OpticalCompiler(profile="fujifilm_gfx100rf")
        payload = compiler.compile(
            scene="Studio portrait with pixelation",
            target="imagen",
            reference={
                "filename": "ref.png",
                "mode": "depixelate_gfx100rf",
            },
            human_skin_realism=True,
        )
        self.assertIn("Fujifilm GFX100RF 102MP", payload.positive_prompt)
        self.assertIn("Human skin realism strictly overrides sharpness", payload.positive_prompt)
        self.assertIn("pore stamping", payload.negative_prompt)

    def test_midjourney_depixelate_adapter(self) -> None:
        """Verify Midjourney adapter produces --sref, --iw 2.0 --cw 100, and skin realism --no tokens."""
        compiler = OpticalCompiler(profile="fujifilm_gfx100rf")
        payload = compiler.compile(
            scene="Vintage portrait restoration",
            target="midjourney",
            reference={
                "filename": "face.jpg",
                "mode": "depixelate_gfx100rf",
            },
            human_skin_realism=True,
        )
        self.assertIn("--sref face.jpg", payload.positive_prompt)
        self.assertIn("--iw 2.0", payload.positive_prompt)
        self.assertIn("--cw 100", payload.positive_prompt)
        self.assertIn("Fujifilm GFX100RF", payload.positive_prompt)
        self.assertIn("102 megapixels", payload.positive_prompt)
        self.assertIn("--no", payload.positive_prompt)
        self.assertIn("plastic skin", payload.positive_prompt)
        self.assertIn("pore stamping", payload.positive_prompt)

    def test_flux_depixelate_adapter(self) -> None:
        """Verify Flux adapter produces narrative photographic description and skin realism rules."""
        compiler = OpticalCompiler(profile="fujifilm_gfx100rf")
        payload = compiler.compile(
            scene="Close up headshot with compression artifacts",
            target="flux",
            reference={
                "filename": "shot.png",
                "mode": "depixelate_gfx100rf",
            },
            human_skin_realism=True,
        )
        self.assertIn("Fujifilm GFX100RF 102MP", payload.positive_prompt)
        self.assertIn("Human skin realism override", payload.positive_prompt)
        self.assertIn("pore stamping", payload.negative_prompt)

    def test_sdxl_depixelate_adapter(self) -> None:
        """Verify SDXL adapter outputs structured tokens and comprehensive negative suppression."""
        compiler = OpticalCompiler(profile="fujifilm_gfx100rf")
        payload = compiler.compile(
            scene="Detailed portrait restoration",
            target="sdxl",
            reference={
                "filename": "portrait.png",
                "mode": "depixelate_gfx100rf",
            },
            human_skin_realism=True,
        )
        self.assertIn("Fujifilm GFX100RF 102MP", payload.positive_prompt)
        self.assertIn("organic human skin realism", payload.positive_prompt)
        self.assertIn("pore stamping", payload.negative_prompt)

    def test_json_all_in_one_prompt_adapter(self) -> None:
        """Verify JSON All-in-One Prompt includes schema 3.1 and skin realism block."""
        compiler = OpticalCompiler(profile="fujifilm_gfx100rf")
        payload = compiler.compile(
            scene="Historical photograph restoration",
            target="json",
            reference={
                "filename": "historical.png",
                "mode": "depixelate_gfx100rf",
            },
            human_skin_realism=True,
            content_type="portrait",
        )
        data = json.loads(payload.positive_prompt)
        self.assertIn("human_skin_realism_override_protocol", data)
        self.assertEqual(data["content_classification"]["type"], "portrait")
        self.assertTrue(data["human_skin_realism_override_protocol"]["enforced"])
        self.assertIn("Fujifilm GFX100RF", data["hardware_rendering_target"]["camera_system"])

    def test_flat_reproduction_content_types(self) -> None:
        """Verify non-photographic types enforce flat copy reproduction and suppress optical DoF/grain."""
        compiler = OpticalCompiler(profile="fujifilm_gfx100rf")
        for ct in ["document_scan", "ui_or_screenshot", "meme_or_infographic"]:
            payload = compiler.compile(
                scene="Technical diagram document scan",
                target="gpt_images",
                reference={
                    "filename": "diagram.png",
                    "mode": "depixelate_gfx100rf",
                },
                content_type=ct,
            )
            self.assertIn("flat reproduction capture", payload.positive_prompt.lower())
            self.assertIn("suppress optical depth-of-field falloff", payload.positive_prompt.lower())

    @unittest.skipUnless(PILLOW_AVAILABLE, "Pillow required for restoration test")
    def test_restoration_skin_realism_config(self) -> None:
        """Verify RestorationConfig has human_skin_realism and updates unsharp threshold."""
        from PIL import Image

        cfg = RestorationConfig(human_skin_realism=True)
        self.assertTrue(cfg.human_skin_realism)

        # Create a tiny test image in scratch dir
        test_dir = Path(__file__).resolve().parent.parent / "scratch_test"
        test_dir.mkdir(exist_ok=True)
        test_img_path = test_dir / "test_input.png"
        out_img_path = test_dir / "test_output.jpg"

        # Create 100x100 test image
        img = Image.new("RGB", (100, 100), color=(180, 150, 130))
        img.save(test_img_path)

        # Run test upscale (with tiny target to test pipeline execution fast)
        cfg_test = RestorationConfig(
            target_pixels=40_000, # small for unit test speed
            human_skin_realism=True,
        )
        report = restore_and_upscale_102mp(
            input_path=str(test_img_path),
            output_path=str(out_img_path),
            config=cfg_test,
        )
        self.assertTrue(report["validation_passed"])
        self.assertTrue(report["human_skin_realism_active"])

        # Clean up test files
        if test_img_path.exists():
            test_img_path.unlink()
        if out_img_path.exists():
            out_img_path.unlink()
        if test_dir.exists():
            test_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
