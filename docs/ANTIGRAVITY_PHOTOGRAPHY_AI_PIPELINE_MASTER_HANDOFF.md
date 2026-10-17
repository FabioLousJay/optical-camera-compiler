# Antigravity Master Handoff: AI Photography, Super-Resolution, Print Engineering and Evaluation CI

**Status:** Implementation-ready requirements + locally tested CPU starter + historical master prompts. **Implemented and verified in PhotonQC (`photonqc/` + `photopipe/`).**

**Prepared:** 2026-10-17  
**Target:** Google Antigravity workspace, Python 3.11+, GitHub Actions, real SR model adapters, computational-photography evaluation.

See:
- [`photonqc/`](../photonqc/) and [`photopipe/`](../photopipe/) for the complete implementation.
- [`docs/evaluation.md`](evaluation.md) for perceptual evaluation & anti-hallucination benchmarks.
- [`docs/print-color-management.md`](print-color-management.md) for print geometry, LittleCMS2 ICC soft-proofing, and series cohesion.
- [`docs/provenance.md`](provenance.md) for cryptographic SHA-256 verification and byte-budget integrity.
- [`docs/model-cards/realesrgan_x4plus.md`](model-cards/realesrgan_x4plus.md) for RRDBNet model card & licensing governance.
- [`docs/BACKLOG_AND_REVIEW.md`](BACKLOG_AND_REVIEW.md) for Gate 0–5 verification status and remediated prototype defects.
