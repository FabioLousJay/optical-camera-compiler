"""Unit tests for the Sequential Reconstruction-to-4x Export Orchestrator v1.0."""

from __future__ import annotations

import json
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch

from optical_compiler.compiler import OpticalCompiler
from optical_compiler.models import (
    NegativeShield,
    ProcessingPath,
    ReferenceImageInput,
    ReferenceMode,
    SceneInput,
    SequentialReconstructionOrchestratorSpec,
    TargetEngine,
)
from optical_compiler.restoration import (
    PILLOW_AVAILABLE,
    SequentialReconstructionReport,
    execute_sequential_reconstruction_workflow,
)
from optical_compiler.web import StudioAPIHandler


class TestSequentialReconstructionOrchestrator(unittest.TestCase):
    """Test suite validating Prompt 1 and Prompt 2 integration across compiler, models, adapters, and web endpoints."""

    def setUp(self) -> None:
        self.compiler = OpticalCompiler(profile="sony_a1_ii")

    def test_processing_path_enum_and_aliases(self) -> None:
        """Verify ProcessingPath parsing and alias resolution."""
        self.assertEqual(ProcessingPath.from_str("path_a"), ProcessingPath.PATH_A_CLEAN)
        self.assertEqual(ProcessingPath.from_str("clean"), ProcessingPath.PATH_A_CLEAN)
        self.assertEqual(ProcessingPath.from_str("path_b"), ProcessingPath.PATH_B_GENERATIVE)
        self.assertEqual(ProcessingPath.from_str("generative"), ProcessingPath.PATH_B_GENERATIVE)
        self.assertEqual(ProcessingPath.from_str("path_c"), ProcessingPath.PATH_C_TEXT)
        self.assertEqual(ProcessingPath.from_str("text"), ProcessingPath.PATH_C_TEXT)
        self.assertEqual(ProcessingPath.from_str("path_d"), ProcessingPath.PATH_D_IDENTITY)
        self.assertEqual(ProcessingPath.from_str("face"), ProcessingPath.PATH_D_IDENTITY)
        self.assertIsNone(ProcessingPath.from_str("unknown_fallback"))

    def test_reference_mode_sequential_recon_aliases(self) -> None:
        """Verify ReferenceMode alias mapping for sequential reconstruction workflow."""
        self.assertEqual(ReferenceMode.from_str("sequential_recon_4x"), ReferenceMode.SEQUENTIAL_RECON_4X)
        self.assertEqual(ReferenceMode.from_str("sequential_recon"), ReferenceMode.SEQUENTIAL_RECON_4X)
        self.assertEqual(ReferenceMode.from_str("Apply the Sequential Reconstruction-to-4x Workflow."), ReferenceMode.SEQUENTIAL_RECON_4X)
        self.assertEqual(ReferenceMode.from_str("Apply Professional 4x Reconstruction Lock."), ReferenceMode.SEQUENTIAL_RECON_4X)

    def test_orchestrator_spec_defaults(self) -> None:
        """Verify SequentialReconstructionOrchestratorSpec default values and serialization."""
        spec = SequentialReconstructionOrchestratorSpec()
        self.assertEqual(spec.title, "Sequential Reconstruction-to-4x Export Orchestrator v1.0")
        self.assertEqual(spec.processing_path, ProcessingPath.PATH_B_GENERATIVE)
        self.assertIn("Fujifilm GFX 100 II", spec.camera_quality_target)
        self.assertEqual(spec.linear_scale, 4)
        self.assertEqual(spec.format, "PNG")
        self.assertEqual(spec.color_mode, "RGB")
        self.assertEqual(spec.compress_level, 0)
        self.assertTrue(spec.staged_sharpening)
        self.assertTrue(spec.enforce_stage_order)
        self.assertTrue(spec.truth_labeling)

        d = spec.to_dict()
        self.assertIn("title", d)
        self.assertIn("workflow_identity", d)
        self.assertIn("stage_1_contract", d)
        self.assertIn("quality_gate_checks", d["stage_1_contract"])
        self.assertIn("stage_2_contract", d)
        self.assertIn("truth_labeling_policy", d)
        self.assertEqual(len(d["stage_1_contract"]["quality_gate_checks"]), 8)

    def test_negative_shield_sequential_drift_tokens(self) -> None:
        """Verify NegativeShield includes anti-false-enlargement and sequential drift shield tokens."""
        shield = NegativeShield()
        tokens = shield.all_tokens(include_sequential_orchestrator=True)
        self.assertGreaterEqual(len(shield.sequential_orchestrator_drift), 20)
        self.assertIn("bicubic enlargement blur", tokens)
        self.assertIn("mathematical upscale masquerading as reconstruction", tokens)
        self.assertIn("skipping stage 1 generative reconstruction", tokens)

    def test_compiler_auto_detection_from_prompt_command(self) -> None:
        """Verify compiler auto-detects short command trigger in user scene prompt and routes to GFX 100 II."""
        user_prompt = "Portrait of a vintage watchmaker. Apply the Sequential Reconstruction-to-4x Workflow."
        payload = self.compiler.compile(scene=user_prompt, target=TargetEngine.GPT_IMAGES)

        self.assertIn("Fujifilm GFX 100 II", payload.positive_prompt)
        self.assertIn("Sequential Reconstruction-to-4x Orchestrator", payload.positive_prompt)
        self.assertIn("Stage 1", payload.positive_prompt)
        self.assertIn("Stage 2", payload.positive_prompt)
        self.assertIn("Quality Gate", payload.positive_prompt)

    def test_compiler_explicit_spec_and_routing(self) -> None:
        """Verify compiler handles explicit sequential_recon_orchestrator flag and processing_path."""
        payload = self.compiler.compile(
            scene="Architectural blueprint and high-contrast typography",
            target=TargetEngine.RAW,
            sequential_recon_orchestrator=True,
            processing_path=ProcessingPath.PATH_C_TEXT,
        )

        self.assertIn("Sequential Reconstruction-to-4x Export Orchestrator v1.0", payload.positive_prompt)
        self.assertIn("path_c_text", payload.positive_prompt)
        self.assertIn("Fujifilm GFX 100 II", payload.positive_prompt)

    def test_json_adapter_schema_version_3_9(self) -> None:
        """Verify JSON All-in-One adapter emits schema_version 3.9 and complete orchestrator structure."""
        payload = self.compiler.compile(
            scene="Vintage botanical sketch with handwritten text",
            target=TargetEngine.JSON_PROMPT,
            sequential_recon_orchestrator=True,
            processing_path="path_c",
        )

        data = json.loads(payload.positive_prompt)
        self.assertEqual(data["schema_version"], "3.9")
        self.assertIn("sequential_reconstruction_orchestrator", data)
        orch = data["sequential_reconstruction_orchestrator"]
        self.assertTrue(orch["active"])
        self.assertEqual(orch["active_router_path"], "path_c_text")
        self.assertIn("Fujifilm GFX 100 II", orch["camera_quality_target"])
        self.assertIn("bicubic enlargement blur", data["negative_shield"]["sequential_orchestrator_drift"])

    def test_midjourney_adapter_sequential_recon(self) -> None:
        """Verify Midjourney adapter includes sequential recon flags, optical camera target, and negative tokens."""
        payload = self.compiler.compile(
            scene="Weathered maritime navigation chart",
            target=TargetEngine.MIDJOURNEY,
            sequential_recon_orchestrator=True,
        )

        self.assertIn("Sequential Reconstruction-to-4x Export Orchestrator", payload.positive_prompt)
        self.assertIn("GFX 100 II 102MP medium-format", payload.positive_prompt)
        self.assertIn("staged sharpening without edge halos", payload.positive_prompt)
        self.assertIn("false enlargement", payload.negative_prompt)
        self.assertIn("bicubic blur", payload.negative_prompt)

    def test_flux_adapter_sequential_recon(self) -> None:
        """Verify Flux adapter outputs declarative two-stage reconstruction prose."""
        payload = self.compiler.compile(
            scene="Weathered stone temple relief with intricate moss detail",
            target=TargetEngine.FLUX,
            sequential_recon_orchestrator=True,
        )

        self.assertIn("Sequential Reconstruction-to-4x Export Orchestrator", payload.positive_prompt)
        self.assertIn("Fujifilm GFX 100 II", payload.positive_prompt)
        self.assertEqual(payload.parameters.get("stage_1"), "True Generative Reconstruction First Pass")
        self.assertEqual(payload.parameters.get("stage_2"), "4x RGB PNG Export Lock")
        self.assertEqual(payload.parameters.get("linear_scale"), 4)

    def test_sdxl_adapter_sequential_recon(self) -> None:
        """Verify SDXL adapter outputs weighted camera chunks, 4x RGB PNG tag, and negative prompt tokens."""
        payload = self.compiler.compile(
            scene="Studio portrait with authentic skin texture",
            target=TargetEngine.SDXL,
            sequential_recon_orchestrator=True,
            processing_path=ProcessingPath.PATH_D_IDENTITY,
        )

        self.assertIn("Fujifilm GFX 100 II 102MP medium-format tonal depth", payload.positive_prompt)
        self.assertIn("Stage 2 4x RGB PNG export lock", payload.positive_prompt)
        self.assertIn("bicubic enlargement blur", payload.negative_prompt)

    def test_imagen_adapter_sequential_recon(self) -> None:
        """Verify Imagen 3 adapter outputs natural photographic narrative for two-stage workflow."""
        payload = self.compiler.compile(
            scene="Ancient illuminated manuscript page",
            target=TargetEngine.IMAGEN,
            sequential_recon_orchestrator=True,
        )

        self.assertIn("Sequential Reconstruction-to-4x Export Orchestrator", payload.positive_prompt)
        self.assertIn("Fujifilm GFX 100 II", payload.positive_prompt)
        self.assertEqual(payload.parameters.get("stage_1"), "True Generative Reconstruction First Pass")
        self.assertEqual(payload.parameters.get("stage_2"), "4x RGB PNG Export Lock")

    def test_web_api_sequential_recon_compile(self) -> None:
        """Verify Web Studio /api/compile accepts sequential_recon_orchestrator and processing_path."""
        handler = StudioAPIHandler.__new__(StudioAPIHandler)
        handler.compiler_cache = {}

        req_body = json.dumps({
            "scene": "Antique mechanical chronometer dial",
            "target": "gpt_images",
            "sequential_recon_orchestrator": True,
            "processing_path": "path_c",
        }).encode("utf-8")

        handler.path = "/api/compile"
        handler.headers = {"Content-Length": str(len(req_body))}
        handler.rfile = BytesIO(req_body)
        handler.wfile = BytesIO()

        with patch.object(handler, "send_response") as mock_resp, \
             patch.object(handler, "send_header") as mock_hdr, \
             patch.object(handler, "end_headers") as mock_end:
            handler.do_POST()
            mock_resp.assert_called_with(200)

        response_bytes = handler.wfile.getvalue()
        res_data = json.loads(response_bytes.decode("utf-8"))

        self.assertIn("positive_prompt", res_data)
        self.assertIn("Sequential Reconstruction-to-4x Orchestrator", res_data["positive_prompt"])
        self.assertIn("path_c_text", res_data["positive_prompt"])

    def test_web_api_sequential_recon_endpoint_missing_input(self) -> None:
        """Verify /api/sequential-recon-4x returns 400 when input_path is missing."""
        handler = StudioAPIHandler.__new__(StudioAPIHandler)
        handler.compiler_cache = {}

        req_body = json.dumps({}).encode("utf-8")
        handler.path = "/api/sequential-recon-4x"
        handler.headers = {"Content-Length": str(len(req_body))}
        handler.rfile = BytesIO(req_body)
        handler.wfile = BytesIO()

        with patch.object(handler, "send_response") as mock_resp, \
             patch.object(handler, "send_header"), \
             patch.object(handler, "end_headers"):
            handler.do_POST()
            mock_resp.assert_called_with(400)

    def test_web_studio_html_contains_sequential_elements(self) -> None:
        """Verify root HTML contains btnModeSequentialRecon, seqReconPanel, and processingPathSelect."""
        handler = StudioAPIHandler.__new__(StudioAPIHandler)
        handler.path = "/"
        handler.headers = {}
        handler.wfile = BytesIO()

        with patch.object(handler, "send_response") as mock_resp, \
             patch.object(handler, "send_header"), \
             patch.object(handler, "end_headers"):
            handler.do_GET()
            mock_resp.assert_called_with(200)

        html = handler.wfile.getvalue().decode("utf-8")
        self.assertIn("btnModeSequentialRecon", html)
        self.assertIn("seqReconPanel", html)
        self.assertIn("processingPathSelect", html)
        self.assertIn("Sequential Reconstruction-to-4x Orchestrator v1.0", html)

    def test_sequential_reconstruction_report_structure(self) -> None:
        """Verify SequentialReconstructionReport dataclass fields, markdown formatting, and dictionary export."""
        report = SequentialReconstructionReport(
            input_path="/tmp/source.png",
            output_path="/tmp/master_4x.png",
            source_dimensions=(512, 512),
            stage_1_dimensions=(512, 512),
            final_dimensions=(2048, 2048),
            color_mode="RGB",
            file_format="PNG",
            file_size_bytes=16777216,
            file_size_mb=16.0,
            processing_path="path_b_generative",
            stage_1_method="frequency_separation_semantic_reconstruction",
            stage_1_status="completed",
            stage_1_retried=False,
            quality_gate_passed=True,
            quality_gate_checks={"check_1": True, "check_2": True},
            linear_multiplier=4,
            area_multiplier=16,
            sha256="abcdef1234567890",
            execution_seconds=0.15,
            truth_label_stage_1="AI-assisted detail reconstruction from low-resolution source",
            truth_label_stage_2="True 4X full-color uncompressed RGB PNG export",
            truth_label_final="Professional 2-stage generative reconstruction + 4x export",
        )

        rep_dict = report.to_dict()
        self.assertEqual(rep_dict["source_dimensions"], "512x512")
        self.assertEqual(rep_dict["final_dimensions"], "2048x2048")
        self.assertEqual(rep_dict["linear_multiplier"], "4X")
        self.assertEqual(rep_dict["area_multiplier"], "16X")
        self.assertTrue(rep_dict["quality_gate_passed"])
        self.assertEqual(rep_dict["truth_labels"]["stage_1"], "AI-assisted detail reconstruction from low-resolution source")

        md = report.to_markdown()
        self.assertIn("# Sequential Reconstruction-to-4x Export Orchestrator v1.0 Report", md)
        self.assertIn("PASSED ✅", md)


if __name__ == "__main__":
    unittest.main()
