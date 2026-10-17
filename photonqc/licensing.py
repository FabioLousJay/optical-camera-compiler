"""Model licensing, governance registry, and supply-chain verification gates."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ModelLicenseSpec:
    """Governance and license specification for a Super-Resolution model."""

    name: str
    architecture: str
    scale: int
    spdx_license: str
    commercial_allowed: bool
    upstream_url: str
    weights_url: str
    notes: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


MODEL_GOVERNANCE_REGISTRY: dict[str, ModelLicenseSpec] = {
    "RealESRGAN_x4plus": ModelLicenseSpec(
        name="RealESRGAN_x4plus",
        architecture="RRDBNet (23 blocks, 64 feat, 32 grow_ch)",
        scale=4,
        spdx_license="BSD-3-Clause",
        commercial_allowed=True,
        upstream_url="https://github.com/xinntao/Real-ESRGAN",
        weights_url="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        notes="Official 4x perceptual SR checkpoint; verify weight terms and SHA-256 independently.",
    ),
    "RealESRNet_x4plus": ModelLicenseSpec(
        name="RealESRNet_x4plus",
        architecture="RRDBNet (23 blocks, 64 feat, 32 grow_ch, MSE/L1 fidelity trained)",
        scale=4,
        spdx_license="BSD-3-Clause",
        commercial_allowed=True,
        upstream_url="https://github.com/xinntao/Real-ESRGAN",
        weights_url="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth",
        notes="High structural fidelity 4x checkpoint without GAN discriminator hallucination.",
    ),
    "SwinIR-M_x4": ModelLicenseSpec(
        name="SwinIR-M_x4",
        architecture="Swin Transformer Image Restoration (Medium)",
        scale=4,
        spdx_license="Apache-2.0",
        commercial_allowed=True,
        upstream_url="https://github.com/JingyunLiang/SwinIR",
        weights_url="https://github.com/JingyunLiang/SwinIR/releases",
        notes="Transformer comparator for Phase 2/4 evaluations.",
    ),
    "HAT-S_x4": ModelLicenseSpec(
        name="HAT-S_x4",
        architecture="Hybrid Attention Transformer (Small)",
        scale=4,
        spdx_license="Apache-2.0",
        commercial_allowed=True,
        upstream_url="https://github.com/XPixelGroup/HAT",
        weights_url="https://github.com/XPixelGroup/HAT/releases",
        notes="Hybrid channel + window attention SR comparator.",
    ),
    "SUPIR": ModelLicenseSpec(
        name="SUPIR",
        architecture="Scaling-UP Image Restoration (SDXL Diffusion Prior)",
        scale=4,
        spdx_license="LicenseRef-SUPIR-NonCommercial",
        commercial_allowed=False,
        upstream_url="https://github.com/Fanghua-Yu/SUPIR",
        weights_url="https://github.com/Fanghua-Yu/SUPIR",
        notes="RESTRICTED: Non-commercial research only absent explicit license permission. Rejected for source-locked commercial pipelines.",
    ),
}


def verify_model_license(
    model_name: str,
    allow_non_commercial: bool = False,
) -> ModelLicenseSpec:
    """Validate model against governance registry and enforce commercial-use license gate."""
    normalized = model_name.strip()
    aliases = {
        "realesrgan": "RealESRGAN_x4plus",
        "realesrgan_x4plus": "RealESRGAN_x4plus",
        "realesrnet": "RealESRNet_x4plus",
        "realesrnet_x4plus": "RealESRNet_x4plus",
        "swinir": "SwinIR-M_x4",
        "swinir_m_x4": "SwinIR-M_x4",
        "hat": "HAT-S_x4",
        "hat_s_x4": "HAT-S_x4",
        "supir": "SUPIR",
    }
    canonical = aliases.get(normalized.lower(), normalized)
    if canonical not in MODEL_GOVERNANCE_REGISTRY:
        raise ValueError(
            f"Unregistered model {model_name!r}. Registered models: {sorted(MODEL_GOVERNANCE_REGISTRY.keys())}"
        )

    spec = MODEL_GOVERNANCE_REGISTRY[canonical]
    if not spec.commercial_allowed and not allow_non_commercial:
        raise PermissionError(
            f"Model {spec.name!r} carries a restrictive license ({spec.spdx_license}) and is blocked "
            f"by default: {spec.notes}. Pass allow_non_commercial=True only for authorized non-commercial research."
        )
    return spec
