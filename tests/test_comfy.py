"""Tests for ComfyUI custom node integration."""

import unittest
from optical_compiler.comfy_nodes import (
    OpticalCameraCompilerNode,
    NODE_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS,
)


class TestComfyNode(unittest.TestCase):
    def setUp(self):
        self.node = OpticalCameraCompilerNode()

    def test_input_types(self):
        types = OpticalCameraCompilerNode.INPUT_TYPES()
        self.assertIn("required", types)
        self.assertIn("camera_rig", types["required"])
        self.assertIn("model_target", types["required"])
        self.assertIn("subject", types["required"])

    def test_compile_node_execution(self):
        pos, neg, unified = self.node.compile_optical_prompt(
            camera_rig="Phase One XF IQ4 150MP Trichromatic",
            model_target="flux",
            subject="Cyberpunk hacker in neon alleyway",
            environment="Wet asphalt reflections, rain drizzle",
            lighting_override="Rim light from blue neon signs",
            aspect_ratio="16:9",
            reference_mode="disabled",
            fidelity_lock=0.85,
            anti_drift_biometrics="enabled",
            append_negative_shield="yes",
        )
        self.assertIn("Phase One XF IQ4", pos)
        self.assertIn("CGI", neg)
        self.assertIn(pos, unified)
        self.assertIn("ANTI-ARTIFACT NEGATIVE SHIELD", unified)

    def test_compile_with_reference(self):
        pos, neg, unified = self.node.compile_optical_prompt(
            camera_rig="Hasselblad H6D-100c Studio Medium Format",
            model_target="midjourney",
            subject="Fine art editorial",
            reference_mode="transform_adapt",
            fidelity_lock=0.90,
            anti_drift_biometrics="enabled",
            append_negative_shield="yes",
        )
        self.assertIn("reference-guided photographic adaptation", pos)
        self.assertIn("--cref", pos)
        self.assertIn("identity drift", pos)

    def test_mappings_exported(self):
        self.assertIn("OpticalCameraCompiler", NODE_CLASS_MAPPINGS)
        self.assertIn("OpticalCameraCompiler", NODE_DISPLAY_NAME_MAPPINGS)


if __name__ == "__main__":
    unittest.main()
