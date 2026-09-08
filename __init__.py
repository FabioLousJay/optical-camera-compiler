"""ComfyUI custom node package entrypoint for Optical Camera Compiler.

When cloned into ComfyUI/custom_nodes/optical-camera-compiler, ComfyUI automatically
loads the NODE_CLASS_MAPPINGS below.
"""

try:
    from .optical_compiler.comfy_nodes import (
        NODE_CLASS_MAPPINGS,
        NODE_DISPLAY_NAME_MAPPINGS,
    )
    __all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
except ImportError:
    from optical_compiler.comfy_nodes import (
        NODE_CLASS_MAPPINGS,
        NODE_DISPLAY_NAME_MAPPINGS,
    )
    __all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
