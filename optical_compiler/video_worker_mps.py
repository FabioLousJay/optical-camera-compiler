"""PyTorch Apple Silicon MPS video worker for Wan2.2-I2V-A14B (4-step) and LTX-2.3 Audio-Video (8-step distilled)."""

from __future__ import annotations

import argparse
import gc
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import wave

import numpy as np
from PIL import Image
import torch

LTX23_DISTILLED_SIGMAS_8 = [1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875]
WAN22_HF_REPO = "Wan-AI/Wan2.2-I2V-A14B-Diffusers"
LTX23_HF_REPO = "dg845/LTX-2.3-Diffusers"


def _clear_mps() -> None:
    gc.collect()
    if hasattr(torch, "mps") and torch.backends.mps.is_available():
        torch.mps.empty_cache()


def _device() -> str:
    return "mps" if torch.backends.mps.is_available() else "cpu"


def _write_mp4_h264(frames_uint8: np.ndarray, output_mp4: Path, fps: int, ffmpeg_bin: str) -> None:
    """Write RGB uint8 `(T, H, W, 3)` array to crisp H.264 MP4 via ffmpeg."""
    import imageio.v3 as iio

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmpf:
        raw_path = Path(tmpf.name)
    try:
        iio.imwrite(str(raw_path), frames_uint8, fps=fps, codec="libx264")
        subprocess.run(
            [
                ffmpeg_bin,
                "-y",
                "-i",
                str(raw_path),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-crf",
                "16",
                "-movflags",
                "+faststart",
                str(output_mp4),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    finally:
        raw_path.unlink(missing_ok=True)


def run_wan22_mps(args: argparse.Namespace) -> None:
    """Generate a Wan2.2-I2V-A14B 4-step clip cleanly on Apple Silicon MPS."""
    from diffusers import (
        AutoencoderKLWan,
        GGUFQuantizationConfig,
        UniPCMultistepScheduler,
        WanImageToVideoPipeline,
        WanTransformer3DModel,
    )
    from transformers import AutoConfig, AutoTokenizer, UMT5EncoderModel

    if not args.init_image:
        raise ValueError("Wan2.2-I2V requires an attached init image.")

    wan_dir = Path(args.models_root) / "wan22"
    dev = _device()
    t0 = time.monotonic()

    tok = AutoTokenizer.from_pretrained(WAN22_HF_REPO, subfolder="tokenizer")
    t5_cfg = AutoConfig.from_pretrained(WAN22_HF_REPO, subfolder="text_encoder")
    text_enc = UMT5EncoderModel.from_pretrained(
        str(wan_dir),
        gguf_file="umt5-xxl-encoder-Q4_K_M.gguf",
        config=t5_cfg,
        dtype=torch.float32,
    ).to(dev)
    vae = AutoencoderKLWan.from_single_file(
        str(wan_dir / "wan_2.1_vae.safetensors"),
        torch_dtype=torch.float32,
    ).to(dev)
    sched = UniPCMultistepScheduler.from_pretrained(WAN22_HF_REPO, subfolder="scheduler", flow_shift=5.0)

    enc_pipe = WanImageToVideoPipeline(
        tokenizer=tok,
        text_encoder=text_enc,
        vae=vae,
        scheduler=sched,
        transformer=None,
        transformer_2=None,
    )
    neg_prompt = args.negative_prompt or "blurry, distorted face, extra limbs, artifacts, low quality"
    with torch.no_grad():
        prompt_embeds, neg_embeds = enc_pipe.encode_prompt(
            prompt=args.prompt,
            negative_prompt=neg_prompt,
            do_classifier_free_guidance=False,
            device=dev,
            dtype=torch.bfloat16,
        )
    prompt_embeds = prompt_embeds.cpu()
    neg_embeds = neg_embeds.cpu()
    del enc_pipe, text_enc
    _clear_mps()

    qcfg = GGUFQuantizationConfig(compute_dtype=torch.bfloat16)
    tr_high = WanTransformer3DModel.from_single_file(
        str(wan_dir / "wan2.2_i2v_A14b_high_noise_lightx2v_4step-Q4_K_M.gguf"),
        config=WAN22_HF_REPO,
        subfolder="transformer",
        quantization_config=qcfg,
        torch_dtype=torch.bfloat16,
    )
    tr_low = WanTransformer3DModel.from_single_file(
        str(wan_dir / "wan2.2_i2v_A14b_low_noise_lightx2v_4step-Q4_K_M.gguf"),
        config=WAN22_HF_REPO,
        subfolder="transformer_2",
        quantization_config=qcfg,
        torch_dtype=torch.bfloat16,
    )

    pipe = WanImageToVideoPipeline(
        tokenizer=tok,
        text_encoder=None,
        vae=vae,
        scheduler=sched,
        transformer=tr_high,
        transformer_2=tr_low,
        boundary_ratio=0.9,
    )
    if dev == "mps":
        pipe.enable_model_cpu_offload(device="mps")

    init_img = Image.open(args.init_image).convert("RGB").resize((args.width, args.height), Image.Resampling.LANCZOS)
    last_img = (
        Image.open(args.end_image).convert("RGB").resize((args.width, args.height), Image.Resampling.LANCZOS)
        if args.end_image
        else None
    )

    with torch.no_grad():
        out = pipe(
            image=init_img,
            last_image=last_img,
            prompt_embeds=prompt_embeds,
            negative_prompt_embeds=neg_embeds,
            height=args.height,
            width=args.width,
            num_frames=args.frames,
            num_inference_steps=4,
            guidance_scale=1.0,
            guidance_scale_2=1.0,
            generator=torch.Generator("cpu").manual_seed(args.seed),
            output_type="np",
        )

    frames = (np.clip(out.frames[0], 0.0, 1.0) * 255).astype(np.uint8)
    _write_mp4_h264(frames, Path(args.output_mp4), args.fps, args.ffmpeg_bin)
    print(f"WAN22_MPS_DONE {frames.shape} in {time.monotonic() - t0:.2f}s", flush=True)


def _load_ltx23_connectors(ltx_dir: Path) -> torch.nn.Module:
    import gguf
    from diffusers.models.condition_embedders.condition_embedder_ltx2 import LTX2TextConnectors
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file

    ccfg = json.loads(Path(hf_hub_download(LTX23_HF_REPO, "connectors/config.json")).read_text(encoding="utf-8"))
    ccfg["rope_double_precision"] = False
    conn = LTX2TextConnectors.from_config(ccfg).to(torch.bfloat16)

    proj_sd = load_file(str(ltx_dir / "ltx-2.3-22b-distilled_embeddings_connectors.safetensors"))
    csd: dict[str, torch.Tensor] = {
        "audio_text_proj_in.weight": proj_sd["text_embedding_projection.audio_aggregate_embed.weight"],
        "audio_text_proj_in.bias": proj_sd["text_embedding_projection.audio_aggregate_embed.bias"],
        "video_text_proj_in.weight": proj_sd["text_embedding_projection.video_aggregate_embed.weight"],
        "video_text_proj_in.bias": proj_sd["text_embedding_projection.video_aggregate_embed.bias"],
    }
    reader = gguf.GGUFReader(str(ltx_dir / "ltx-2.3-22b-distilled-1.1-Q4_K_M.gguf"))
    for tensor in reader.tensors:
        if "embeddings_connector." in tensor.name:
            k = (
                tensor.name.replace("audio_embeddings_connector.", "audio_connector.")
                .replace("video_embeddings_connector.", "video_connector.")
                .replace("transformer_1d_blocks.", "transformer_blocks.")
                .replace(".k_norm.", ".norm_k.")
                .replace(".q_norm.", ".norm_q.")
            )
            csd[k] = torch.from_numpy(gguf.dequantize(tensor.data, tensor.tensor_type).copy()).to(torch.bfloat16)

    conn.load_state_dict(csd, strict=True)
    return conn


def _patch_ltx23_single_file_mapping() -> None:
    from diffusers.loaders import single_file_model as sfm

    entry = sfm.SINGLE_FILE_LOADABLE_CLASSES.get("LTX2VideoTransformer3DModel")
    if not entry or getattr(entry["checkpoint_mapping_fn"], "_ltx23_patched", False):
        return
    orig_fn = entry["checkpoint_mapping_fn"]

    def _remap_ltx23(checkpoint: dict[str, torch.Tensor], **kwargs):
        for k in list(checkpoint.keys()):
            nk = k.replace("audio_prompt_adaln_single.", "audio_prompt_adaln.").replace(
                "prompt_adaln_single.", "prompt_adaln."
            )
            if nk != k:
                checkpoint[nk] = checkpoint.pop(k)
        return orig_fn(checkpoint, **kwargs)

    _remap_ltx23._ltx23_patched = True  # type: ignore[attr-defined]
    entry["checkpoint_mapping_fn"] = _remap_ltx23


def run_ltx23_mps(args: argparse.Namespace) -> None:
    """Generate an LTX-2.3 Audio-Video 8-step distilled clip cleanly on Apple Silicon MPS."""
    import imageio.v3 as iio
    from diffusers import (
        AutoencoderKLLTX2Audio,
        AutoencoderKLLTX2Video,
        GGUFQuantizationConfig,
        LTX2ConditionPipeline,
        LTX2ImageToVideoPipeline,
        LTX2Pipeline,
        LTX2VideoTransformer3DModel,
    )
    from diffusers.pipelines.ltx2.pipeline_ltx2_condition import LTX2VideoCondition
    from diffusers.pipelines.ltx2.vocoder import LTX2VocoderWithBWE
    from diffusers.schedulers import FlowMatchEulerDiscreteScheduler
    from transformers import AutoTokenizer, Gemma3Config, Gemma3ForCausalLM

    ltx_dir = Path(args.models_root) / "ltx23"
    dev = _device()
    t0 = time.monotonic()

    tok = AutoTokenizer.from_pretrained(LTX23_HF_REPO, subfolder="tokenizer")
    gcfg = Gemma3Config.from_pretrained(LTX23_HF_REPO, subfolder="text_encoder")
    text_enc = Gemma3ForCausalLM.from_pretrained(
        str(ltx_dir),
        gguf_file="gemma-3-12b-it-qat-UD-Q4_K_XL.gguf",
        config=gcfg.text_config,
        dtype=torch.bfloat16,
    ).to(dev)

    sched = FlowMatchEulerDiscreteScheduler.from_pretrained(LTX23_HF_REPO, subfolder="scheduler")
    avae = AutoencoderKLLTX2Audio.from_pretrained(LTX23_HF_REPO, subfolder="audio_vae", torch_dtype=torch.bfloat16)
    voc = LTX2VocoderWithBWE.from_pretrained(LTX23_HF_REPO, subfolder="vocoder", torch_dtype=torch.bfloat16)
    vae = AutoencoderKLLTX2Video.from_pretrained(LTX23_HF_REPO, subfolder="vae", torch_dtype=torch.bfloat16)

    enc_pipe = LTX2ImageToVideoPipeline(
        scheduler=sched,
        vae=vae,
        audio_vae=avae,
        text_encoder=text_enc,
        tokenizer=tok,
        connectors=None,
        transformer=None,
        vocoder=voc,
    )
    with torch.no_grad():
        prompt_embeds, prompt_mask, _, _ = enc_pipe.encode_prompt(
            prompt=args.prompt,
            negative_prompt=None,
            do_classifier_free_guidance=False,
            device=dev,
            dtype=torch.bfloat16,
        )
    prompt_embeds = prompt_embeds.cpu()
    prompt_mask = prompt_mask.cpu()
    del enc_pipe, text_enc
    _clear_mps()

    conn = _load_ltx23_connectors(ltx_dir)
    _patch_ltx23_single_file_mapping()
    tr = LTX2VideoTransformer3DModel.from_single_file(
        str(ltx_dir / "ltx-2.3-22b-distilled-1.1-Q4_K_M.gguf"),
        config=LTX23_HF_REPO,
        subfolder="transformer",
        quantization_config=GGUFQuantizationConfig(compute_dtype=torch.bfloat16),
        torch_dtype=torch.bfloat16,
    )
    for mod in list(conn.modules()) + list(tr.modules()):
        if hasattr(mod, "double_precision"):
            mod.double_precision = False

    common_kwargs = dict(
        prompt_embeds=prompt_embeds,
        prompt_attention_mask=prompt_mask,
        height=args.height,
        width=args.width,
        num_frames=args.frames,
        frame_rate=float(args.fps),
        num_inference_steps=8,
        sigmas=LTX23_DISTILLED_SIGMAS_8,
        guidance_scale=1.0,
        stg_scale=0.0,
        modality_scale=1.0,
        guidance_rescale=0.0,
        audio_guidance_scale=1.0,
        audio_stg_scale=0.0,
        audio_modality_scale=1.0,
        audio_guidance_rescale=0.0,
        generator=torch.Generator("cpu").manual_seed(args.seed),
        output_type="np",
    )

    if args.init_image and args.end_image:
        init_img = Image.open(args.init_image).convert("RGB").resize((args.width, args.height), Image.Resampling.LANCZOS)
        end_img = Image.open(args.end_image).convert("RGB").resize((args.width, args.height), Image.Resampling.LANCZOS)
        pipe = LTX2ConditionPipeline(
            scheduler=sched,
            vae=vae,
            audio_vae=avae,
            text_encoder=None,
            tokenizer=tok,
            connectors=conn,
            transformer=tr,
            vocoder=voc,
        )
        if dev == "mps":
            pipe.enable_model_cpu_offload(device="mps")
        with torch.no_grad():
            out = pipe(
                conditions=[
                    LTX2VideoCondition(frames=init_img, index=0, strength=1.0, crf=0),
                    LTX2VideoCondition(frames=end_img, index=-1, strength=1.0, crf=0),
                ],
                **common_kwargs,
            )
    elif args.init_image:
        init_img = Image.open(args.init_image).convert("RGB").resize((args.width, args.height), Image.Resampling.LANCZOS)
        pipe = LTX2ImageToVideoPipeline(
            scheduler=sched,
            vae=vae,
            audio_vae=avae,
            text_encoder=None,
            tokenizer=tok,
            connectors=conn,
            transformer=tr,
            vocoder=voc,
        )
        if dev == "mps":
            pipe.enable_model_cpu_offload(device="mps")
        with torch.no_grad():
            out = pipe(image=init_img, image_crf=0, **common_kwargs)
    else:
        pipe = LTX2Pipeline(
            scheduler=sched,
            vae=vae,
            audio_vae=avae,
            text_encoder=None,
            tokenizer=tok,
            connectors=conn,
            transformer=tr,
            vocoder=voc,
        )
        if dev == "mps":
            pipe.enable_model_cpu_offload(device="mps")
        with torch.no_grad():
            out = pipe(**common_kwargs)

    frames = (np.clip(out.frames[0], 0.0, 1.0) * 255).astype(np.uint8)
    audio_raw = (
        out.audio[0].float().cpu().numpy() if torch.is_tensor(out.audio) else np.asarray(out.audio[0], dtype=np.float32)
    )
    if audio_raw.ndim == 2 and audio_raw.shape[0] <= 2:
        audio_raw = audio_raw.T
    pcm = (np.clip(audio_raw, -1.0, 1.0) * 32767.0).astype(np.int16)
    sr = int(getattr(voc.config, "output_sampling_rate", 48000))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_vid = Path(tmpdir) / "vid.mp4"
        tmp_aud = Path(tmpdir) / "aud.wav"
        iio.imwrite(str(tmp_vid), frames, fps=args.fps, codec="libx264")
        with wave.open(str(tmp_aud), "wb") as wf:
            wf.setnchannels(pcm.shape[1] if pcm.ndim == 2 else 1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm.tobytes())
        subprocess.run(
            [
                args.ffmpeg_bin,
                "-y",
                "-i",
                str(tmp_vid),
                "-i",
                str(tmp_aud),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-crf",
                "16",
                "-af",
                "apad",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                "-movflags",
                "+faststart",
                str(args.output_mp4),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    print(f"LTX23_MPS_DONE {frames.shape} sr={sr} in {time.monotonic() - t0:.2f}s", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apple Silicon Metal MPS Video Worker")
    parser.add_argument("--engine", required=True, choices=["wan22", "ltx23"])
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--negative-prompt", default="")
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--frames", type=int, required=True)
    parser.add_argument("--fps", type=int, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--init-image", default=None)
    parser.add_argument("--end-image", default=None)
    parser.add_argument("--models-root", required=True)
    parser.add_argument("--ffmpeg-bin", required=True)
    parser.add_argument("--output-mp4", required=True)
    args = parser.parse_args()

    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    if args.engine == "wan22":
        run_wan22_mps(args)
    else:
        run_ltx23_mps(args)


if __name__ == "__main__":
    main()
