"""Local Apple Silicon Metal Video Generation Engine (Wan2.2-I2V-A14B 4-Step MPS, LTX-2.3 Audio+Video MPS, FFmpeg 2x)."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any

from .qwen_engine import _engine_root

VIDEO_RESOLUTIONS: dict[str, dict[str, tuple[int, int, int, int]]] = {
    # quality_tier -> aspect_ratio -> (gen_w, gen_h, out_w, out_h), exact multiples of 32
    "fast_480p": {
        "1:1": (640, 640, 640, 640),
        "4:3": (672, 512, 672, 512),
        "3:4": (512, 672, 512, 672),
        "4:5": (512, 640, 512, 640),
        "5:4": (640, 512, 640, 512),
        "3:2": (768, 512, 768, 512),
        "2:3": (512, 768, 512, 768),
        "16:9": (832, 480, 832, 480),
        "9:16": (480, 832, 480, 832),
        "21:9": (896, 384, 896, 384),
    },
    "hd_720p": {
        "1:1": (896, 896, 896, 896),
        "4:3": (1024, 768, 1024, 768),
        "3:4": (768, 1024, 768, 1024),
        "4:5": (768, 960, 768, 960),
        "5:4": (960, 768, 960, 768),
        "3:2": (1088, 704, 1088, 704),
        "2:3": (704, 1088, 704, 1088),
        "16:9": (1280, 704, 1280, 704),
        "9:16": (704, 1280, 704, 1280),
        "21:9": (1344, 576, 1344, 576),
    },
    "pro_1080p": {
        # Base generation dimensions (exact multiples of 32) upscaled 2x via crisp Lanczos + Unsharp
        "1:1": (544, 544, 1088, 1088),
        "4:3": (704, 544, 1408, 1088),
        "3:4": (544, 704, 1088, 1408),
        "4:5": (544, 672, 1088, 1344),
        "5:4": (672, 544, 1344, 1088),
        "3:2": (800, 544, 1600, 1088),
        "2:3": (544, 800, 1088, 1600),
        "16:9": (960, 544, 1920, 1088),
        "9:16": (544, 960, 1088, 1920),
        "21:9": (1024, 448, 2048, 896),
    },
}


def _find_ffmpeg() -> str | None:
    found = shutil.which("ffmpeg")
    if found:
        return found
    for cand in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        if Path(cand).is_file():
            return cand
    return None


def _find_ffprobe() -> str | None:
    found = shutil.which("ffprobe")
    if found:
        return found
    for cand in ("/opt/homebrew/bin/ffprobe", "/usr/local/bin/ffprobe"):
        if Path(cand).is_file():
            return cand
    return None


def get_video_engine_status() -> dict[str, Any]:
    """Inspect PyTorch MPS runtime, `ffmpeg`, Wan2.2-I2V-A14B, and LTX-2.3 weights."""
    root = _engine_root()
    mps_python = root / ".venv" / "bin" / "python"
    sd_cli = root / "bin" / "sd-cli"
    video_root = root / "models" / "video"
    wan_dir = video_root / "wan22"
    ltx_dir = video_root / "ltx23"

    def _f(p: Path, min_bytes: int = 1_000_000) -> dict[str, Any]:
        exists = p.is_file() and p.stat().st_size >= min_bytes
        sz = p.stat().st_size if p.is_file() else 0
        return {"path": str(p), "exists": exists, "size_gb": round(sz / (1024**3), 2)}

    wan_high = _f(wan_dir / "wan2.2_i2v_A14b_high_noise_lightx2v_4step-Q4_K_M.gguf", 8_500_000_000)
    wan_low = _f(wan_dir / "wan2.2_i2v_A14b_low_noise_lightx2v_4step-Q4_K_M.gguf", 8_500_000_000)
    wan_t5 = _f(wan_dir / "umt5-xxl-encoder-Q4_K_M.gguf", 3_000_000_000)
    wan_vae = _f(wan_dir / "wan_2.1_vae.safetensors", 200_000_000)
    relay_vsr = _f(wan_dir / "flash_x2.safetensors", 100_000_000)

    ltx_dit = _f(ltx_dir / "ltx-2.3-22b-distilled-1.1-Q4_K_M.gguf", 12_000_000_000)
    ltx_llm = _f(ltx_dir / "gemma-3-12b-it-qat-UD-Q4_K_XL.gguf", 6_500_000_000)
    ltx_conn = _f(ltx_dir / "ltx-2.3-22b-distilled_embeddings_connectors.safetensors", 2_000_000_000)
    ltx_vvae = _f(ltx_dir / "ltx-2.3-22b-distilled_video_vae.safetensors", 1_200_000_000)
    ltx_avae = _f(ltx_dir / "ltx-2.3-22b-distilled_audio_vae.safetensors", 300_000_000)

    mps_ok = mps_python.is_file() and os.access(mps_python, os.X_OK)
    sd_ok = sd_cli.is_file() and os.access(sd_cli, os.X_OK)
    ffmpeg_bin = _find_ffmpeg()
    ffprobe_bin = _find_ffprobe()
    wan22_ready = bool(mps_ok and wan_high["exists"] and wan_low["exists"] and wan_t5["exists"] and wan_vae["exists"])
    ltx23_ready = bool(mps_ok and ltx_dit["exists"] and ltx_llm["exists"] and ltx_conn["exists"] and ltx_vvae["exists"] and ltx_avae["exists"])

    return {
        "ready": bool(wan22_ready or ltx23_ready),
        "backend": "pytorch_mps_diffusers",
        "mps_python": str(mps_python),
        "mps_python_installed": mps_ok,
        "sd_cli": str(sd_cli),
        "sd_cli_installed": sd_ok,
        "ffmpeg_ready": bool(ffmpeg_bin),
        "ffmpeg_path": ffmpeg_bin,
        "ffprobe_path": ffprobe_bin,
        "wan22_ready": wan22_ready,
        "ltx23_ready": ltx23_ready,
        "relayvsr_ready": bool(relay_vsr["exists"] and wan_vae["exists"]),
        "models": {
            "wan22": {
                "high_noise": wan_high,
                "low_noise": wan_low,
                "t5": wan_t5,
                "vae": wan_vae,
                "relay_vsr_x2": relay_vsr,
            },
            "ltx23": {
                "diffusion": ltx_dit,
                "gemma_llm": ltx_llm,
                "connectors": ltx_conn,
                "video_vae": ltx_vvae,
                "audio_vae": ltx_avae,
            },
        },
    }


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _probe_video(ffprobe_bin: str | None, video_path: Path) -> dict[str, Any]:
    if not ffprobe_bin or not video_path.is_file():
        return {}
    try:
        proc = subprocess.run(
            [
                ffprobe_bin,
                "-v",
                "error",
                "-show_entries",
                "stream=codec_type,codec_name,width,height,r_frame_rate,duration",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            import json as _json

            return _json.loads(proc.stdout)
    except Exception:
        pass
    return {}


def _upscale_clip_2x(
    ffmpeg_bin: str,
    input_video: Path,
    output_mp4: Path,
    *,
    target_w: int,
    target_h: int,
) -> tuple[Path, str]:
    """Upscale a clip cleanly 2x to Pro 1080p using FFmpeg Lanczos + edge-safe unsharp."""
    probe = _probe_video(_find_ffprobe(), input_video)
    has_audio = any(s.get("codec_type") == "audio" for s in probe.get("streams", []))
    vf = f"scale={target_w}:{target_h}:flags=lanczos,unsharp=5:5:0.45:5:5:0.0"
    cmd = [ffmpeg_bin, "-y", "-i", str(input_video), "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16"]
    if has_audio:
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])
    cmd.extend(["-movflags", "+faststart", str(output_mp4)])
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return output_mp4, "ffmpeg_lanczos_unsharp_2x"


def run_video_generation_local(
    prompt: str,
    output_path: str | Path,
    *,
    engine: str = "wan22",
    negative_prompt: str = "",
    aspect_ratio: str = "16:9",
    quality_tier: str = "fast_480p",
    duration_sec: int = 3,
    seed: int = 42,
    init_image_path: str | Path | None = None,
    end_image_path: str | Path | None = None,
    custom_audio_path: str | Path | None = None,
    extend_from_video: str | Path | None = None,
) -> dict[str, Any]:
    """Execute local Apple Metal video generation (`wan22` or `ltx23`) via PyTorch MPS Diffusers + `ffmpeg`."""
    status = get_video_engine_status()
    if not status["mps_python_installed"]:
        raise RuntimeError("qwen-image-2.1-engine PyTorch MPS environment (.venv/bin/python) is missing.")
    if not status["ffmpeg_ready"]:
        raise RuntimeError("ffmpeg is required for MP4/audio muxing and was not found on PATH.")

    engine_key = engine.strip().lower()
    if engine_key not in ("wan22", "ltx23"):
        raise ValueError(f"Unsupported video engine '{engine}'. Expected 'wan22' or 'ltx23'.")
    if engine_key == "wan22" and not status["wan22_ready"]:
        raise RuntimeError(f"Wan2.2-I2V-A14B weights are not ready yet: {status['models']['wan22']}")
    if engine_key == "ltx23" and not status["ltx23_ready"]:
        raise RuntimeError(f"LTX-2.3 weights are not ready yet: {status['models']['ltx23']}")

    mps_python = str(status["mps_python"])
    ffmpeg_bin = str(status["ffmpeg_path"])
    ffprobe_bin = status.get("ffprobe_path")
    models_root = str(_engine_root() / "models" / "video")
    worker_script = Path(__file__).resolve().with_name("video_worker_mps.py")

    tier = quality_tier if quality_tier in VIDEO_RESOLUTIONS else "fast_480p"
    ar_map = VIDEO_RESOLUTIONS[tier]
    gen_w, gen_h, out_w, out_h = ar_map.get(aspect_ratio, ar_map["16:9"])

    dur = max(2, min(5, int(duration_sec)))
    if engine_key == "ltx23":
        fps = 24
        # LTX-2.3 requires (frames - 1) divisible by 8
        raw_frames = dur * fps
        video_frames = ((max(16, raw_frames) + 7) // 8) * 8 + 1
    else:
        fps = 16
        # Wan2.2 requires (frames - 1) divisible by 4
        raw_frames = dur * fps
        video_frames = ((max(16, raw_frames) + 3) // 4) * 4 + 1

    out_p = Path(output_path).expanduser().resolve()
    if out_p.suffix.lower() != ".mp4":
        out_p = out_p.with_suffix(".mp4")
    out_p.parent.mkdir(parents=True, exist_ok=True)

    extend_p: Path | None = None
    if extend_from_video:
        extend_p = Path(extend_from_video).expanduser().resolve()
        if not extend_p.is_file():
            raise FileNotFoundError(f"Video to extend not found: {extend_p}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        effective_init: Path | None = None
        if extend_p is not None:
            last_frame = tmp / "extend_last_frame.png"
            subprocess.run(
                [ffmpeg_bin, "-y", "-sseof", "-0.15", "-i", str(extend_p), "-frames:v", "1", "-q:v", "2", str(last_frame)],
                capture_output=True,
                text=True,
                check=True,
            )
            if not last_frame.is_file():
                raise RuntimeError(f"Failed to extract final frame from {extend_p}")
            effective_init = last_frame
        elif init_image_path:
            effective_init = Path(init_image_path).expanduser().resolve()
            if not effective_init.is_file():
                raise FileNotFoundError(f"Init image not found: {effective_init}")

        if engine_key == "wan22" and effective_init is None:
            raise ValueError(
                "Wan2.2-I2V requires an attached start photo (or Extend Clip). Switch to LTX-2.3 for text-only generation."
            )

        raw_mp4 = tmp / "raw_mps.mp4"
        cmd: list[str] = [
            mps_python,
            "-u",
            str(worker_script),
            "--engine",
            engine_key,
            "--prompt",
            prompt,
            "--negative-prompt",
            negative_prompt,
            "--width",
            str(gen_w),
            "--height",
            str(gen_h),
            "--frames",
            str(video_frames),
            "--fps",
            str(fps),
            "--seed",
            str(seed),
            "--models-root",
            models_root,
            "--ffmpeg-bin",
            ffmpeg_bin,
            "--output-mp4",
            str(raw_mp4),
        ]
        if effective_init is not None:
            cmd.extend(["--init-image", str(effective_init)])
        if end_image_path:
            end_p = Path(end_image_path).expanduser().resolve()
            if not end_p.is_file():
                raise FileNotFoundError(f"End frame image not found: {end_p}")
            cmd.extend(["--end-image", str(end_p)])

        t0 = time.monotonic()
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=2400)
        elapsed_gen = round(time.monotonic() - t0, 2)
        if proc.returncode != 0 or not raw_mp4.is_file():
            tail = (proc.stderr or proc.stdout or "")[-2000:]
            raise RuntimeError(f"PyTorch MPS worker ({engine_key}) failed (exit {proc.returncode}): {tail}")

        upscale_method = "none_native"
        clip_mp4 = raw_mp4
        if tier == "pro_1080p" and (out_w > gen_w or out_h > gen_h):
            up_mp4 = tmp / "clip_1080p.mp4"
            clip_mp4, upscale_method = _upscale_clip_2x(
                ffmpeg_bin,
                raw_mp4,
                up_mp4,
                target_w=out_w,
                target_h=out_h,
            )

        # Optional clip extension (concatenate extend_from_video + newly generated clip)
        if extend_p is not None:
            stitched_mp4 = tmp / "stitched.mp4"
            p_old = _probe_video(ffprobe_bin, extend_p)
            p_new = _probe_video(ffprobe_bin, clip_mp4)
            old_has_aud = any(s.get("codec_type") == "audio" for s in p_old.get("streams", []))
            new_has_aud = any(s.get("codec_type") == "audio" for s in p_new.get("streams", []))
            if old_has_aud and new_has_aud:
                filt = (
                    f"[0:v]scale={out_w}:{out_h}:setsar=1,fps={fps}[v0];"
                    f"[1:v]scale={out_w}:{out_h}:setsar=1,fps={fps}[v1];"
                    "[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]"
                )
                maps = ["-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", "192k"]
            else:
                filt = (
                    f"[0:v]scale={out_w}:{out_h}:setsar=1,fps={fps}[v0];"
                    f"[1:v]scale={out_w}:{out_h}:setsar=1,fps={fps}[v1];"
                    "[v0][v1]concat=n=2:v=1:a=0[v]"
                )
                maps = ["-map", "[v]"]
            subprocess.run(
                [
                    ffmpeg_bin,
                    "-y",
                    "-i",
                    str(extend_p),
                    "-i",
                    str(clip_mp4),
                    "-filter_complex",
                    filt,
                    *maps,
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-crf",
                    "16",
                    "-movflags",
                    "+faststart",
                    str(stitched_mp4),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            clip_mp4 = stitched_mp4

        # Optional custom audio track overlay (mux onto video)
        if custom_audio_path:
            aud_p = Path(custom_audio_path).expanduser().resolve()
            if not aud_p.is_file():
                raise FileNotFoundError(f"Custom audio file not found: {aud_p}")
            muxed_mp4 = tmp / "muxed.mp4"
            subprocess.run(
                [
                    ffmpeg_bin,
                    "-y",
                    "-i",
                    str(clip_mp4),
                    "-i",
                    str(aud_p),
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-shortest",
                    "-movflags",
                    "+faststart",
                    str(muxed_mp4),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            clip_mp4 = muxed_mp4

        shutil.copy2(clip_mp4, out_p)

    probe_final = _probe_video(ffprobe_bin, out_p)
    v_stream = next((s for s in probe_final.get("streams", []) if s.get("codec_type") == "video"), {})
    a_stream = next((s for s in probe_final.get("streams", []) if s.get("codec_type") == "audio"), None)
    return {
        "method": f"pytorch_mps_{engine_key}",
        "engine": engine_key,
        "quality_tier": tier,
        "upscale_method": upscale_method,
        "generated_dimensions": [gen_w, gen_h],
        "output_dimensions": [int(v_stream.get("width", out_w)), int(v_stream.get("height", out_h))],
        "fps": fps,
        "video_frames": video_frames,
        "has_audio": a_stream is not None,
        "audio_codec": a_stream.get("codec_name") if a_stream else None,
        "duration_seconds": round(float(probe_final.get("format", {}).get("duration", dur)), 2),
        "elapsed_seconds": elapsed_gen,
        "extended_from": str(extend_p) if extend_p else None,
        "output_path": str(out_p),
        "output_sha256": _sha256_file(out_p),
    }


def post_edit_video_local(
    input_video_path: str | Path,
    output_path: str | Path,
    *,
    action: str = "trim_audio",
    trim_start_sec: float = 0.0,
    trim_end_sec: float | None = None,
    speed_factor: float = 1.0,
    custom_audio_path: str | Path | None = None,
) -> dict[str, Any]:
    """Post-edit an existing generated clip cleanly (trim, slow-mo/speed, custom audio mux, or 2x 1080p upscale)."""
    status = get_video_engine_status()
    if not status["ffmpeg_ready"]:
        raise RuntimeError("ffmpeg is not installed.")
    ffmpeg_bin = str(status["ffmpeg_path"])
    ffprobe_bin = status.get("ffprobe_path")

    in_p = Path(input_video_path).expanduser().resolve()
    if not in_p.is_file():
        raise FileNotFoundError(f"Input video not found: {in_p}")
    out_p = Path(output_path).expanduser().resolve()
    if out_p.suffix.lower() != ".mp4":
        out_p = out_p.with_suffix(".mp4")
    out_p.parent.mkdir(parents=True, exist_ok=True)

    act = action.strip().lower()
    if act == "upscale_1080p":
        probe = _probe_video(ffprobe_bin, in_p)
        v_s = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), {})
        w_cur = int(v_s.get("width", 832))
        h_cur = int(v_s.get("height", 480))
        t_w = ((w_cur * 2) // 2) * 2
        t_h = ((h_cur * 2) // 2) * 2
        _, method = _upscale_clip_2x(ffmpeg_bin, in_p, out_p, target_w=t_w, target_h=t_h)
        p_out = _probe_video(ffprobe_bin, out_p)
        a_s = next((s for s in p_out.get("streams", []) if s.get("codec_type") == "audio"), None)
        return {
            "method": method,
            "has_audio": a_s is not None,
            "audio_codec": a_s.get("codec_name") if a_s else None,
            "output_path": str(out_p),
            "output_dimensions": [t_w, t_h],
            "duration_seconds": round(float(p_out.get("format", {}).get("duration", 0.0)), 2),
            "output_sha256": _sha256_file(out_p),
        }

    # Trim / Speed / Custom Audio Mux
    in_probe = _probe_video(ffprobe_bin, in_p)
    in_has_audio = any(s.get("codec_type") == "audio" for s in in_probe.get("streams", []))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_vid = Path(tmpdir) / "edited.mp4"
        cmd = [ffmpeg_bin, "-y"]
        if trim_start_sec > 0.0:
            cmd.extend(["-ss", f"{float(trim_start_sec):.3f}"])
        if trim_end_sec is not None and trim_end_sec > trim_start_sec:
            cmd.extend(["-to", f"{float(trim_end_sec):.3f}"])
        cmd.extend(["-i", str(in_p)])

        spd = max(0.5, min(2.0, float(speed_factor)))
        vfilters: list[str] = []
        if abs(spd - 1.0) > 1e-3:
            vfilters.append(f"setpts={1.0 / spd:.4f}*PTS")

        aud_p: Path | None = None
        if custom_audio_path:
            aud_p = Path(custom_audio_path).expanduser().resolve()
            if not aud_p.is_file():
                raise FileNotFoundError(f"Audio file not found: {aud_p}")
            cmd.extend(["-i", str(aud_p), "-map", "0:v:0", "-map", "1:a:0", "-shortest"])
        elif in_has_audio and abs(spd - 1.0) > 1e-3:
            cmd.extend(["-af", f"atempo={spd:.4f}"])

        if vfilters:
            cmd.extend(["-vf", ",".join(vfilters)])
        cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(tmp_vid)])
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=300)
        if proc.returncode != 0 or not tmp_vid.is_file():
            raise RuntimeError(f"ffmpeg post-edit failed: {proc.stderr[-800:]}")
        shutil.copy2(tmp_vid, out_p)

    p_out = _probe_video(ffprobe_bin, out_p)
    v_s = next((s for s in p_out.get("streams", []) if s.get("codec_type") == "video"), {})
    a_s = next((s for s in p_out.get("streams", []) if s.get("codec_type") == "audio"), None)
    return {
        "method": "ffmpeg_post_edit",
        "has_audio": a_s is not None,
        "audio_codec": a_s.get("codec_name") if a_s else None,
        "output_dimensions": [int(v_s.get("width", 0)), int(v_s.get("height", 0))],
        "duration_seconds": round(float(p_out.get("format", {}).get("duration", 0.0)), 2),
        "output_path": str(out_p),
        "output_sha256": _sha256_file(out_p),
    }
