"""Unit tests for the Web Studio HTTP handler using in-memory streams (sandbox-safe)."""

from __future__ import annotations

import io
import json
import unittest
from unittest.mock import MagicMock

from optical_compiler.web import StudioAPIHandler


class MockSocket:
    """Mock socket for BaseHTTPRequestHandler testing."""

    def makefile(self, *args: str, **kwargs: int) -> io.BytesIO:
        return io.BytesIO()


class TestWebStudioHandler(unittest.TestCase):
    """Test suite for StudioAPIHandler endpoints using in-memory streams."""

    def _execute_request(
        self, method: str, path: str, body: bytes = b""
    ) -> tuple[int, dict[str, str], bytes]:
        """Simulate an HTTP request through StudioAPIHandler."""
        headers = [f"{method} {path} HTTP/1.1", "Host: localhost"]
        if body:
            headers.append(f"Content-Length: {len(body)}")
            headers.append("Content-Type: application/json")
        headers.append("")
        headers.append("")

        raw_request = "\r\n".join(headers).encode("utf-8") + body

        input_stream = io.BytesIO(raw_request)
        output_stream = io.BytesIO()

        # Instantiate mock handler
        handler = StudioAPIHandler.__new__(StudioAPIHandler)
        handler.rfile = input_stream
        handler.wfile = output_stream
        handler.connection = MockSocket()
        handler.client_address = ("127.0.0.1", 54321)
        handler.server = MagicMock()
        handler.close_connection = False

        # Parse request line and headers
        handler.handle_one_request()

        # Parse raw response
        output_stream.seek(0)
        raw_response = output_stream.read()

        header_part, _, body_part = raw_response.partition(b"\r\n\r\n")
        header_lines = header_part.decode("utf-8").split("\r\n")

        status_line = header_lines[0]
        status_code = int(status_line.split(" ")[1])

        resp_headers = {}
        for line in header_lines[1:]:
            if ": " in line:
                k, v = line.split(": ", 1)
                resp_headers[k.lower()] = v

        return status_code, resp_headers, body_part

    def test_get_root_html(self) -> None:
        """Verify root / returns 200 and HTML."""
        status, headers, body = self._execute_request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers.get("content-type", ""))
        self.assertIn(b"Optical Camera Compiler", body)
        self.assertIn(b"Master Studio Console", body)

    def test_get_profiles(self) -> None:
        """Verify /api/profiles returns JSON list of profiles."""
        status, headers, body = self._execute_request("GET", "/api/profiles")
        self.assertEqual(status, 200)
        self.assertIn("application/json", headers.get("content-type", ""))
        profiles = json.loads(body.decode("utf-8"))
        profile_ids = [p["id"] for p in profiles]
        self.assertIn("phase_one_iq4", profile_ids)
        self.assertIn("leica_m11", profile_ids)
        self.assertIn("hasselblad_h6d", profile_ids)

    def test_get_health(self) -> None:
        """Verify /api/health returns status ok."""
        status, headers, body = self._execute_request("GET", "/api/health")
        self.assertEqual(status, 200)
        data = json.loads(body.decode("utf-8"))
        self.assertEqual(data["status"], "ok")

    def test_post_compile(self) -> None:
        """Verify /api/compile accepts JSON payload and compiles."""
        payload = {
            "scene": "Botanist examining orchid specimens",
            "target": "imagen",
            "profile": "phase_one_iq4",
            "framing": "macro portrait",
            "aperture": "f/8",
        }
        body = json.dumps(payload).encode("utf-8")
        status, headers, resp_body = self._execute_request("POST", "/api/compile", body)
        self.assertEqual(status, 200)
        res_data = json.loads(resp_body.decode("utf-8"))
        self.assertEqual(res_data["target_engine"], "imagen")
        self.assertIn("Phase One XF IQ4", res_data["positive_prompt"])
        self.assertIn("Botanist", res_data["positive_prompt"])
        self.assertIn("airbrushed skin", res_data["negative_prompt"])
        # Verify unified prompt appends the anti-artifact negative shield directly after the optical payload
        self.assertIn("unified_prompt", res_data)
        self.assertIn("[ANTI-ARTIFACT NEGATIVE SHIELD]:", res_data["unified_prompt"])
        self.assertIn("Phase One XF IQ4", res_data["unified_prompt"])
        self.assertIn("airbrushed skin", res_data["unified_prompt"])

    def test_post_compile_v3_4_suite(self) -> None:
        """Verify /api/compile handles v3.4 parameters correctly."""
        payload = {
            "scene": "Fine-art gallery portrait in black latex",
            "target": "gpt_images",
            "profile": "phase_one_iq4",
            "body_volume": "biceps:significant, chest:moderate",
            "weight_lb": 230,
            "material": "latex_gloss",
            "background_style": "pure_black_blur",
            "volumetric_4d": True,
            "remove_text": True,
            "paper": "baryta",
            "policy_safe": True,
        }
        body = json.dumps(payload).encode("utf-8")
        status, headers, resp_body = self._execute_request("POST", "/api/compile", body)
        self.assertEqual(status, 200)
        res_data = json.loads(resp_body.decode("utf-8"))
        self.assertEqual(res_data["target_engine"], "gpt_images")
        prompt = res_data["positive_prompt"]
        self.assertIn("Policy-Safe Compliance Recovery Directive", prompt)
        self.assertIn("4D Volumetric & Premium Material Engine", prompt)
        self.assertIn("Proportional Volume Calibration", prompt)
        self.assertIn("Print-calibrated exhibition prepress specification", prompt)
        self.assertIn("Text removal engine", prompt)
        self.assertTrue(res_data["metadata"]["policy_safe"])

    def test_options_cors(self) -> None:
        """Verify OPTIONS request returns CORS headers for external frontends like Lovable."""
        status, headers, _ = self._execute_request("OPTIONS", "/api/compile")
        self.assertEqual(status, 204)
        self.assertEqual(headers.get("access-control-allow-origin"), "*")

    def test_post_upscale_102mp_missing_input(self) -> None:
        """Verify /api/upscale-102mp returns 400 when input_path is missing."""
        payload = {"output_format": "JPEG"}
        body = json.dumps(payload).encode("utf-8")
        status, headers, resp_body = self._execute_request("POST", "/api/upscale-102mp", body)
        self.assertEqual(status, 400)
        res_data = json.loads(resp_body.decode("utf-8"))
        self.assertIn("error", res_data)
        self.assertIn("input_path", res_data["error"])

    def test_post_upscale_102mp_success(self) -> None:
        """Verify /api/upscale-102mp executes and returns 18-field report."""
        try:
            from optical_compiler.restoration import PILLOW_AVAILABLE
            if not PILLOW_AVAILABLE:
                self.skipTest("Pillow is not installed")
        except ImportError:
            self.skipTest("Restoration module could not be imported")

        import tempfile
        from PIL import Image

        with tempfile.TemporaryDirectory() as td:
            in_file = f"{td}/web_sample.png"
            out_file = f"{td}/web_sample_out.png"
            img = Image.new("RGB", (60, 40), color=(100, 150, 200))
            img.save(in_file)

            payload = {
                "input_path": in_file,
                "output_path": out_file,
                "output_format": "PNG",
                "cleanup": True,
                "sharpening": True,
            }
            body = json.dumps(payload).encode("utf-8")
            status, headers, resp_body = self._execute_request("POST", "/api/upscale-102mp", body)
            self.assertEqual(status, 200)
            res_data = json.loads(resp_body.decode("utf-8"))
            self.assertEqual(res_data["profile"], "PLATINUM_NO_DRIFT")
            self.assertTrue(res_data["validation_passed"])
            self.assertTrue(res_data["exact_aspect_ratio_preserved"])
            self.assertEqual(res_data["output_format"], "PNG")

    def test_get_root_html_camera_and_ambient_dropdowns(self) -> None:
        """Verify root / returns HTML containing both Camera Style and Ambient Style dropdowns and Clear / Build Your Own."""
        status, headers, body = self._execute_request("GET", "/")
        self.assertEqual(status, 200)
        html = body.decode("utf-8")
        
        # Verify dual dropdown IDs and labels
        self.assertIn('id="cameraPresetSelect"', html)
        self.assertIn('id="ambientPresetSelect"', html)
        self.assertIn("Camera Style:", html)
        self.assertIn("Ambient Style:", html)

        # Verify Clear / Build Your Own button and options
        self.assertIn("Clear / Build Your Own", html)
        self.assertIn("-- Clear / Build Your Own (Custom Rig) --", html)
        self.assertIn("-- Clear / Build Your Own (Custom Ambience) --", html)

        # Verify legacy compatibility shim
        self.assertIn('id="scenarioSelect"', html)

        # Verify key camera presets in the HTML
        self.assertIn("cam_phase_one_iq4_still", html)
        self.assertIn("cam_leica_m11_reportage", html)
        self.assertIn("cam_leica_q3_monochrom", html)
        self.assertIn("cam_leica_sl2_motion_blur", html)
        self.assertIn("cam_sony_a1_ii_flash_freeze", html)
        self.assertIn("cam_canon_eos_r5_ii_vogue", html)
        self.assertIn("cam_canon_eos_r1_action", html)
        self.assertIn("cam_nikon_z9_plena", html)
        self.assertIn("cam_panasonic_s1rii_micro", html)
        self.assertIn("cam_arri_alexa_35_anamorphic", html)
        self.assertIn("cam_linhof_4x5_architectural", html)
        self.assertIn("cam_pentax_67_bokeh_king", html)

        # Verify key ambient presets in the HTML
        self.assertIn("amb_paris_haussmann", html)
        self.assertIn("amb_tokyo_shinjuku", html)
        self.assertIn("amb_amalfi_terrace", html)
        self.assertIn("amb_tuscan_vineyard", html)
        self.assertIn("amb_cosmetic_packshot", html)
        self.assertIn("amb_4d_liquid_glass", html)
        self.assertIn("amb_depixel_v2_restoration", html)
        self.assertIn("amb_monochrome_luminance", html)

    def test_country_city_and_geographic_vibe_dropdowns(self) -> None:
        """Verify root / contains Country/City and Geographic Vibe dual dropdowns meeting all regional thresholds."""
        status, headers, body = self._execute_request("GET", "/")
        self.assertEqual(status, 200)
        html = body.decode("utf-8")

        # 1. Verify presence of both coordinated dropdowns and compatibility shim
        self.assertIn('id="countryCitySelect"', html)
        self.assertIn('id="geographicVibeSelect"', html)
        self.assertIn('id="cityVibeSelect"', html)
        self.assertIn("Country / City", html)
        self.assertIn("Geographic Vibe", html)

        # 2. Verify all regional optgroups exist
        self.assertIn("United States (18 Cities)", html)
        self.assertIn("Canada (11 Cities)", html)
        self.assertIn("Brazil (12 Cities)", html)
        self.assertIn("Europe (34 Cities)", html)
        self.assertIn("Asia (22 Cities)", html)
        self.assertIn("Oceania (12 Cities)", html)
        self.assertIn("The Orient (Middle East, Levant, Silk Road, North Africa - 22 Cities)", html)

        # 3. Verify city quotas meet or exceed user requirements
        usa_cities = [c for c in html.split('value="') if c.startswith("usa_")]
        can_cities = [c for c in html.split('value="') if c.startswith("can_")]
        bra_cities = [c for c in html.split('value="') if c.startswith("bra_")]
        eur_cities = [c for c in html.split('value="') if c.startswith("eur_")]
        asia_cities = [c for c in html.split('value="') if c.startswith("asia_")]
        oce_cities = [c for c in html.split('value="') if c.startswith("oce_")]
        ori_cities = [c for c in html.split('value="') if c.startswith("ori_")]

        # In select options (at least 1 occurrence per city value)
        self.assertGreaterEqual(len(set([c.split('"')[0] for c in usa_cities])), 15)
        self.assertGreaterEqual(len(set([c.split('"')[0] for c in can_cities])), 10)
        self.assertGreaterEqual(len(set([c.split('"')[0] for c in bra_cities])), 10)
        self.assertGreaterEqual(len(set([c.split('"')[0] for c in eur_cities])), 30)
        self.assertGreaterEqual(len(set([c.split('"')[0] for c in asia_cities])), 20)
        self.assertGreaterEqual(len(set([c.split('"')[0] for c in oce_cities])), 10)
        self.assertGreaterEqual(len(set([c.split('"')[0] for c in ori_cities])), 20)

        # Total unique cities count across all 7 regions
        total_unique_cities = (
            len(set([c.split('"')[0] for c in usa_cities]))
            + len(set([c.split('"')[0] for c in can_cities]))
            + len(set([c.split('"')[0] for c in bra_cities]))
            + len(set([c.split('"')[0] for c in eur_cities]))
            + len(set([c.split('"')[0] for c in asia_cities]))
            + len(set([c.split('"')[0] for c in oce_cities]))
            + len(set([c.split('"')[0] for c in ori_cities]))
        )
        self.assertGreaterEqual(total_unique_cities, 120)

        # 4. Verify Geographic Vibes categories and key presets
        self.assertIn("Historic & Classical Architecture", html)
        self.assertIn("Modern, Industrial & Urban Atmosphere", html)
        self.assertIn("Regional, Coastal & Environmental Archetypes", html)
        self.assertIn('value="haussmann"', html)
        self.assertIn('value="cast_iron_soho"', html)
        self.assertIn('value="georgian_brick"', html)
        self.assertIn('value="classical_marble"', html)
        self.assertIn('value="modern_skyscrapers"', html)
        self.assertIn('value="industrial_brick"', html)
        self.assertIn('value="brutalist_concrete"', html)
        self.assertIn('value="art_deco_brass"', html)
        self.assertIn('value="narrow_neon_alleys"', html)
        self.assertIn('value="mediterranean_whitewash"', html)
        self.assertIn('value="traditional_timber_lattice"', html)
        self.assertIn('value="desert_sandstone_oasis"', html)
        self.assertIn('value="tropical_oceanfront"', html)
        self.assertIn('value="oriental_geometric_mosaic"', html)

        # 5. Verify JavaScript dictionaries and handlers
        self.assertIn("COUNTRY_CITY_DATA", html)
        self.assertIn("GEOGRAPHIC_VIBE_DATA", html)
        self.assertIn("onCountryCityChange", html)
        self.assertIn("onGeographicVibeChange", html)


if __name__ == "__main__":
    unittest.main()
