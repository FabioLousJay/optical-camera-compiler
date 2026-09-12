"""Unit tests for Product-Reference Crop Anchor and 100% Commercial SKU Approval Gate."""

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from optical_compiler.cli import main
from optical_compiler.comfy_nodes import OpticalCameraCompilerNode
from optical_compiler.compiler import OpticalCompiler
from optical_compiler.models import (
    NegativeShield,
    ReferenceImageInput,
    ReferenceMode,
    SceneInput,
    TargetEngine,
)
from optical_compiler.profiles import auto_select_profile


class TestProductLockApprovalGate(unittest.TestCase):
    """Test suite validating product lock, 5-point approval gate, and anti-drift tokens."""

    def setUp(self) -> None:
        self.compiler = OpticalCompiler(profile="phase_one_iq4")
        self.product_scene = SceneInput(
            subject="Luxury cosmetic serum bottle on polished dark slate pedestal",
            product_crop="assets/serum_bottle_crop.png",
            sku_color="Amber pharmaceutical glass (#8B4513) with Pantone 116 C gold foil",
            cap_geometry="matte black anodized aluminum dropper cap with 48-ridge knurling collar and flush seal",
            label_kerning="crisp micro-typography, precise character tracking, zero character distortion",
            material_finish="heavy-base borosilicate glass, anti-reflective coating, tactile uncoated paper label",
            seam_geometry="flawless circular base without mold flash, hairline parting seam along shoulder",
            approval_gate_100pct=True,
            aperture="f/8.0",
        )

    def test_reference_mode_product_lock_parsing(self) -> None:
        """Verify ReferenceMode enum and alias parsing for product lock."""
        self.assertEqual(ReferenceMode.PRODUCT_LOCK.value, "product_lock")
        for alias in [
            "product_lock",
            "PRODUCT_LOCK",
            "product",
            "product_crop",
            "product_reference",
            "sku_lock",
            "packshot",
            "commercial_lock",
        ]:
            self.assertEqual(
                ReferenceMode.from_string(alias),
                ReferenceMode.PRODUCT_LOCK,
                f"Failed for alias {alias}",
            )
            self.assertEqual(
                ReferenceMode.from_str(alias),
                ReferenceMode.PRODUCT_LOCK,
                f"Failed for alias {alias}",
            )

    def test_scene_has_product_lock_property(self) -> None:
        """Verify has_product_lock property triggers on any product fidelity attribute."""
        # 1. Product crop
        scene1 = SceneInput(subject="Bottle", product_crop="crop.png")
        self.assertTrue(scene1.has_product_lock)

        # 2. ReferenceMode.PRODUCT_LOCK
        ref_input = ReferenceImageInput(filename="ref.png", mode=ReferenceMode.PRODUCT_LOCK)
        scene2 = SceneInput(subject="Bottle", reference=ref_input)
        self.assertTrue(scene2.has_product_lock)

        # 3. Cap geometry alone
        scene3 = SceneInput(subject="Bottle", cap_geometry="screw top")
        self.assertTrue(scene3.has_product_lock)

        # 4. SKU color alone
        scene4 = SceneInput(subject="Bottle", sku_color="Pantone 296 C")
        self.assertTrue(scene4.has_product_lock)

        # 5. Non-product scene
        scene_plain = SceneInput(subject="Portrait of a woman")
        self.assertFalse(scene_plain.has_product_lock)

    def test_negative_shield_product_drift_tokens(self) -> None:
        """Verify NegativeShield includes product drift tokens when requested."""
        shield = NegativeShield()
        tokens_with = shield.all_tokens(include_product_drift=True)
        tokens_without = shield.all_tokens(include_product_drift=False)

        expected_tokens = [
            "wrong cap geometry",
            "incorrect label kerning",
            "wrong sku color",
            "missing mold seams",
            "distorted parting lines",
            "hallucinated label text",
            "wrong closure form factor",
        ]
        for token in expected_tokens:
            self.assertIn(token, tokens_with, f"Missing token '{token}' in shield")
            self.assertNotIn(token, tokens_without, f"Unexpected token '{token}' when disabled")

    def test_camera_router_routes_product_lock_to_phase_one(self) -> None:
        """Verify intelligent camera router selects Phase One IQ4 150MP for commercial product lock."""
        profile_id = auto_select_profile(self.product_scene)
        self.assertEqual(profile_id, "phase_one_iq4")

    def test_gpt_images_adapter_5_point_approval_gate(self) -> None:
        """Verify GPT Images adapter generates full 5-Point Commercial SKU Approval Gate."""
        payload = self.compiler.compile(
            scene=self.product_scene.subject,
            target="gpt_images",
            product_crop=self.product_scene.product_crop,
            sku_color=self.product_scene.sku_color,
            cap_geometry=self.product_scene.cap_geometry,
            label_kerning=self.product_scene.label_kerning,
            material_finish=self.product_scene.material_finish,
            seam_geometry=self.product_scene.seam_geometry,
            approval_gate_100pct=True,
        )

        pos = payload.positive_prompt
        self.assertIn("100% Commercial SKU Approval Gate", pos)
        self.assertIn("GATE 1: CAP & CLOSURE GEOMETRY", pos)
        self.assertIn("GATE 2: LABEL KERNING & TYPOGRAPHY", pos)
        self.assertIn("GATE 3: PARTING SEAMS & MOLD LINES", pos)
        self.assertIn("GATE 4: MATERIAL FINISH & SPECULAR RESPONSE", pos)
        self.assertIn("GATE 5: SKU COLOR & CHROMATIC FIDELITY", pos)
        self.assertIn("48-ridge knurling", pos)
        self.assertIn("Pantone 116 C", pos)

        # Negative prompt
        self.assertIn("wrong cap geometry", payload.negative_prompt)
        self.assertIn("incorrect label kerning", payload.negative_prompt)

    def test_imagen_adapter_product_lock(self) -> None:
        """Verify Imagen 3 adapter produces cohesive commercial packshot prose with gate enforcement."""
        payload = self.compiler.compile(
            scene=self.product_scene.subject,
            target="imagen",
            product_crop=self.product_scene.product_crop,
            sku_color=self.product_scene.sku_color,
            cap_geometry=self.product_scene.cap_geometry,
            label_kerning=self.product_scene.label_kerning,
            material_finish=self.product_scene.material_finish,
            seam_geometry=self.product_scene.seam_geometry,
            approval_gate_100pct=True,
        )

        pos = payload.positive_prompt
        self.assertIn("Commercial SKU 100% Approval Gate", pos)
        self.assertIn("Cap geometry", pos)
        self.assertIn("SKU color", pos)
        self.assertIn("wrong cap geometry", payload.negative_prompt)

    def test_midjourney_adapter_product_lock(self) -> None:
        """Verify Midjourney adapter emits --sref, max weight, and --no product drift tokens."""
        payload = self.compiler.compile(
            scene=self.product_scene.subject,
            target="midjourney",
            product_crop=self.product_scene.product_crop,
            sku_color=self.product_scene.sku_color,
            cap_geometry=self.product_scene.cap_geometry,
            label_kerning=self.product_scene.label_kerning,
            material_finish=self.product_scene.material_finish,
            seam_geometry=self.product_scene.seam_geometry,
            approval_gate_100pct=True,
        )

        pos = payload.positive_prompt
        self.assertIn("--sref assets/serum_bottle_crop.png", pos)
        self.assertIn("--iw 2.0", pos)
        self.assertIn("--cw 100", pos)
        self.assertIn("100% SKU lock", pos)
        self.assertIn("--no", pos)
        self.assertIn("wrong cap", pos)
        self.assertIn("incorrect kerning", pos)

    def test_flux_adapter_product_lock(self) -> None:
        """Verify Flux.1 adapter includes narrative 100% SKU Gate directives."""
        payload = self.compiler.compile(
            scene=self.product_scene.subject,
            target="flux",
            product_crop=self.product_scene.product_crop,
            sku_color=self.product_scene.sku_color,
            cap_geometry=self.product_scene.cap_geometry,
            label_kerning=self.product_scene.label_kerning,
            material_finish=self.product_scene.material_finish,
            seam_geometry=self.product_scene.seam_geometry,
            approval_gate_100pct=True,
        )

        pos = payload.positive_prompt
        self.assertIn("100% Commercial SKU Approval Gate", pos)
        self.assertIn("Cap and closure geometry:", pos)
        self.assertIn("Label typography and kerning:", pos)
        self.assertIn("Manufacturing seams:", pos)
        self.assertIn("Material finish:", pos)
        self.assertIn("SKU color:", pos)

    def test_sdxl_adapter_product_lock(self) -> None:
        """Verify SDXL dual-channel tokens include commercial packshot and product fidelity."""
        payload = self.compiler.compile(
            scene=self.product_scene.subject,
            target="sdxl",
            product_crop=self.product_scene.product_crop,
            sku_color=self.product_scene.sku_color,
            cap_geometry=self.product_scene.cap_geometry,
            label_kerning=self.product_scene.label_kerning,
            material_finish=self.product_scene.material_finish,
            seam_geometry=self.product_scene.seam_geometry,
            approval_gate_100pct=True,
        )

        pos = payload.positive_prompt
        self.assertIn("commercial product packshot", pos)
        self.assertIn("100% SKU lock", pos)
        self.assertIn("exact cap geometry", pos)
        self.assertIn("exact SKU color", pos)
        self.assertIn("wrong cap geometry", payload.negative_prompt)

    def test_raw_spec_adapter_product_lock(self) -> None:
        """Verify Raw Spec adapter outputs dedicated Commercial Product Fidelity section."""
        payload = self.compiler.compile(
            scene=self.product_scene.subject,
            target="raw",
            product_crop=self.product_scene.product_crop,
            sku_color=self.product_scene.sku_color,
            cap_geometry=self.product_scene.cap_geometry,
            label_kerning=self.product_scene.label_kerning,
            material_finish=self.product_scene.material_finish,
            seam_geometry=self.product_scene.seam_geometry,
            approval_gate_100pct=True,
        )

        pos = payload.positive_prompt
        self.assertIn("--- Commercial Product Fidelity & 100% Approval Gate ---", pos)
        self.assertIn("Product Crop Reference: assets/serum_bottle_crop.png", pos)
        self.assertIn("Cap & Closure Geometry:", pos)
        self.assertIn("Label Kerning & Typography:", pos)
        self.assertIn("Manufacturing Seams:", pos)
        self.assertIn("Material Finish:", pos)
        self.assertIn("SKU Color:", pos)

    def test_json_schema_3_2_product_lock(self) -> None:
        """Verify JSON prompt adapter upgrades to Schema 3.2 with product_fidelity object."""
        payload = self.compiler.compile(
            scene=self.product_scene.subject,
            target="json",
            product_crop=self.product_scene.product_crop,
            sku_color=self.product_scene.sku_color,
            cap_geometry=self.product_scene.cap_geometry,
            label_kerning=self.product_scene.label_kerning,
            material_finish=self.product_scene.material_finish,
            seam_geometry=self.product_scene.seam_geometry,
            approval_gate_100pct=True,
        )

        data = json.loads(payload.positive_prompt)
        self.assertEqual(data["schema_version"], "3.2")
        self.assertIn("product_fidelity", data)
        pf = data["product_fidelity"]
        self.assertEqual(pf["product_crop_reference"], "assets/serum_bottle_crop.png")
        self.assertIn("commercial_sku_approval_gate", data)
        gate = data["commercial_sku_approval_gate"]
        self.assertTrue(gate["active"])
        self.assertIn("gate_1_cap_geometry", gate)
        self.assertIn("gate_2_label_kerning", gate)
        self.assertIn("gate_3_parting_seams", gate)
        self.assertIn("gate_4_material_finish", gate)
        self.assertIn("gate_5_sku_color", gate)

    def test_cli_product_lock_flags(self) -> None:
        """Verify CLI execution with --product-lock and fidelity flags."""
        f = io.StringIO()
        with redirect_stdout(f):
            rc = main([
                "Luxury perfume bottle",
                "--product-lock",
                "--product-crop",
                "perfume_hero.png",
                "--cap-geometry",
                "faceted crystal stopper with ground-glass taper",
                "--sku-color",
                "Pale amber liquid with rose-gold metallic lettering",
                "--label-kerning",
                "monospaced geometric letterforms locked",
                "--material-finish",
                "heavy lead crystal glass with sharp beveled facets",
                "--seams",
                "seamless hand-blown crystal finish",
                "--target",
                "gpt_images",
                "--pos-only",
            ])
        self.assertEqual(rc, 0)
        out = f.getvalue()
        self.assertIn("100% Commercial SKU Approval Gate", out)
        self.assertIn("faceted crystal stopper", out)
        self.assertIn("rose-gold metallic lettering", out)

    def test_comfy_node_product_lock(self) -> None:
        """Verify ComfyUI node handles product_lock mode and product fidelity parameters."""
        node = OpticalCameraCompilerNode()
        pos, neg, unified = node.compile_optical_prompt(
            camera_rig="Phase One XF IQ4 150MP Trichromatic",
            model_target="gpt_images",
            subject="Studio packshot of a beverage can",
            reference_mode="product_lock",
            product_crop="can_crop.png",
            sku_color="Matte vibrant red #E60012",
            cap_geometry="brushed aluminum stay-on-tab closure with laser-etched logo",
            label_kerning="strict sans-serif logotype kerning",
            material_finish="brushed aluminum with condensation drops",
            seam_geometry="rolled top rim seam with microscopic crimp line",
            approval_gate_100pct="enabled",
        )
        self.assertIn("100% Commercial SKU Approval Gate", pos)
        self.assertIn("brushed aluminum stay-on-tab closure", pos)
        self.assertIn("wrong cap geometry", neg)
        self.assertIn("wrong sku color", neg)


if __name__ == "__main__":
    unittest.main()
