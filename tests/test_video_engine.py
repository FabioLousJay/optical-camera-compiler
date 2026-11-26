from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from optical_compiler.video_engine import (
    VIDEO_RESOLUTIONS,
    get_video_engine_status,
    post_edit_video_local,
    run_video_generation_local,
)
from photonqc.pyramids import LaplacianPyramidConfig, frequency_separate_portrait_lighting


class TestLocalVideoEngineIntegration(unittest.TestCase):
    """Verify local PyTorch MPS video engine status, resolution presets, FFmpeg post-edit, and 65MP pyramid guard."""

    def test_video_status_and_web_endpoint(self) -> None:
        status = get_video_engine_status()
        self.assertIn("wan22_ready", status)
        self.assertIn("ltx23_ready", status)
        self.assertIn("ffmpeg_ready", status)
        self.assertIn("mps_python_installed", status)
        self.assertEqual(status.get("backend"), "pytorch_mps_diffusers")
        self.assertIn("models", status)

        try:
            from tests.test_web import TestWebStudioHandler
        except ImportError:
            from test_web import TestWebStudioHandler  # type: ignore[import-not-found]

        helper = TestWebStudioHandler()
        code, _headers, body = helper._execute_request("GET", "/api/video/status")
        self.assertEqual(code, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertTrue(data["mps_python_installed"])
        self.assertTrue(data["ffmpeg_ready"])
        self.assertTrue(data["wan22_ready"])
        self.assertTrue(data["ltx23_ready"])

    def test_video_resolutions_divisible_by_32(self) -> None:
        for tier, ar_map in VIDEO_RESOLUTIONS.items():
            for aspect, (gw, gh, ow, oh) in ar_map.items():
                self.assertEqual(gw % 32, 0, f"{tier} {aspect} gen_w={gw}")
                self.assertEqual(gh % 32, 0, f"{tier} {aspect} gen_h={gh}")
                self.assertEqual(ow % 2, 0, f"{tier} {aspect} out_w={ow}")
                self.assertEqual(oh % 2, 0, f"{tier} {aspect} out_h={oh}")

    def test_wan22_requires_attached_photo(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            run_video_generation_local(
                prompt="A smiling portrait",
                output_path="/tmp/should_not_exist.mp4",
                engine="wan22",
            )
        self.assertIn("start photo", str(ctx.exception))

    def test_post_edit_trim_speed_audio_and_upscale(self) -> None:
        status = get_video_engine_status()
        if not status["ffmpeg_ready"]:
            self.skipTest("ffmpeg not installed")
        ffmpeg_bin = str(status["ffmpeg_path"])

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            src_mp4 = tmp / "src.mp4"
            subprocess.run(
                [
                    ffmpeg_bin,
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "testsrc2=size=320x256:rate=24:duration=2",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:sample_rate=48000:duration=2",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "aac",
                    str(src_mp4),
                ],
                capture_output=True,
                check=True,
            )

            edited_mp4 = tmp / "edited.mp4"
            edit_res = post_edit_video_local(
                src_mp4,
                edited_mp4,
                action="trim_audio",
                trim_start_sec=0.0,
                trim_end_sec=1.5,
                speed_factor=1.5,
            )
            self.assertTrue(edited_mp4.is_file())
            self.assertTrue(edit_res["has_audio"])
            self.assertEqual(edit_res["output_dimensions"], [320, 256])
            self.assertLess(edit_res["duration_seconds"], 1.3)

            up_mp4 = tmp / "upscaled.mp4"
            up_res = post_edit_video_local(src_mp4, up_mp4, action="upscale_1080p")
            self.assertTrue(up_mp4.is_file())
            self.assertTrue(up_res["has_audio"])
            self.assertEqual(up_res["output_dimensions"], [640, 512])
            self.assertEqual(up_res["method"], "ffmpeg_lanczos_unsharp_2x")

    def test_frequency_separate_blocks_accidental_oversize_4x_upscale(self) -> None:
        from PIL import Image

        large = Image.new("RGB", (4096, 4096), (120, 120, 120))
        with self.assertRaises(ValueError) as ctx:
            frequency_separate_portrait_lighting(large, LaplacianPyramidConfig(levels=5, scale_factor=4))
        self.assertIn("65 MP", str(ctx.exception))

    def test_run_server_reuses_live_studio_port(self) -> None:
        import threading
        from http.server import ThreadingHTTPServer
        from optical_compiler.web import StudioAPIHandler, run_server

        ThreadingHTTPServer.allow_reuse_address = True
        srv = ThreadingHTTPServer(("127.0.0.1", 0), StudioAPIHandler)
        busy_port = srv.server_address[1]
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            # Should detect the already-running /api/health server and exit cleanly without OSError
            run_server(host="127.0.0.1", port=busy_port, open_browser=False)
        finally:
            srv.shutdown()
            srv.server_close()
            t.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
