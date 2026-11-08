from __future__ import annotations

import json
import unittest

from optical_compiler import TargetEngine, compile_scene
from optical_compiler.qwen_engine import get_qwen_engine_status


class TestQwenImage21Integration(unittest.TestCase):
    """Verify Qwen-Image-2.1 TargetEngine adapter, Web Studio status endpoint, and local Metal engine discovery."""

    def test_qwen_image_target_adapter_compilation(self) -> None:
        payload = compile_scene(
            "Commercial studio portrait of a ceramic espresso cup",
            profile="sony_a7r_vi",
            target="qwen_image",
            aspect_ratio="4:5",
        )
        self.assertEqual(payload.target_engine, TargetEngine.QWEN_IMAGE)
        self.assertIn("Sony Alpha 7R VI", payload.positive_prompt)
        self.assertEqual(payload.parameters["diffusion_model"], "qwen-image-2.1-turbo-Q8_0.gguf")
        self.assertEqual(payload.parameters["llm"], "Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf")
        self.assertEqual(payload.parameters["steps"], 8)
        self.assertEqual(payload.parameters["width"], 896)
        self.assertEqual(payload.parameters["height"], 1120)

    def test_qwen_engine_status_and_web_endpoint(self) -> None:
        status = get_qwen_engine_status()
        self.assertIn("ready", status)
        self.assertIn("sd_cli", status)
        self.assertIn("models", status)

        try:
            from tests.test_web import TestWebStudioHandler
        except ImportError:
            from test_web import TestWebStudioHandler  # type: ignore[import-not-found]

        helper = TestWebStudioHandler()
        code, _headers, body = helper._execute_request("GET", "/api/qwen-image/status")
        self.assertEqual(code, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertIn("ready", data)
        self.assertTrue(data["sd_cli"]["installed"])

    def test_web_studio_javascript_and_event_handlers_syntax_via_node_check(self) -> None:
        """Ensure HTML_TEMPLATE script blocks and all static HTML event handlers have 0 JS syntax errors."""
        import html as html_mod
        import os
        import re
        import shutil
        import subprocess
        import tempfile

        from optical_compiler.web import HTML_TEMPLATE

        # Verify refFileInput is placed outside refDropzone and paired with a native <label for="refFileInput">
        self.assertIn('<label for="refFileInput"', HTML_TEMPLATE)
        idx_input = HTML_TEMPLATE.index('id="refFileInput"')
        idx_dropzone = HTML_TEMPLATE.index('id="refDropzone"')
        self.assertLess(idx_input, idx_dropzone, "refFileInput must precede refDropzone to prevent click bubbling")

        if shutil.which("node"):
            static_html = HTML_TEMPLATE.split("<script>")[0] + HTML_TEMPLATE.split("</script>")[-1]
            scripts = re.findall(r"<script>(.*?)</script>", HTML_TEMPLATE, re.S)
            handlers = [
                html_mod.unescape(h)
                for h in re.findall(r'\bon(?:click|change|input|keydown)="([^"]+)"', static_html)
            ]
            combined = "\n".join(scripts) + "\n" + "\n".join(f"(function(event){{ {h} }});" for h in handlers)
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
                f.write(combined)
                js_path = f.name
            try:
                proc = subprocess.run(["node", "--check", js_path], capture_output=True, text=True, check=False)
                self.assertEqual(proc.returncode, 0, f"JavaScript SyntaxError in HTML_TEMPLATE:\n{proc.stderr}")
            finally:
                if os.path.exists(js_path):
                    os.unlink(js_path)


if __name__ == "__main__":
    unittest.main()
