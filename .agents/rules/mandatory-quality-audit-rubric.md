---
trigger: always_on
description: Permanent Mandatory Finish-Line Quality Audit Check Rubric required at the completion of every task without user reminder.
---

# Permanent Mandatory Constraint: Finish-Line Quality Audit Check Rubric & Brutal Honesty Mandate

1. **Brutal Honesty & Zero Hype**: Be blunt and factual about real image quality, model limits, and failures. Never claim professional camera quality or success if 100% visual inspection shows artifacts, blur, distortion, or collage seams.
2. **Never Fake It & Never Hallucinate**: Report only verified facts, exact byte/pixel counts, and real visual observations. Never rely on synthetic metrics alone when visual outputs fail.
3. **Never Drift**: Stick strictly to what the user requested and stop immediately when an approach hits a fundamental model/hardware ceiling instead of wasting tokens on diminishing-returns patches.
4. **Always QC Everything**: At the finish of **every** engineering, research, profile addition, bug-fix, or feature implementation task, execute real end-to-end QC (live process/endpoints, UI/JS syntax, test suite, and visual inspection of real outputs) and present a comprehensive **Finish-Line Quality Audit Check Rubric** before concluding—without the user ever needing to ask for it.

## Mandatory Pre-Finish Verification Steps
1. **Automated Test Suite & JS Syntax Execution**: Run the full unit and integration test suite with `SyntaxWarning` treated as error (`.venv/bin/python -W error::SyntaxWarning -m unittest discover -s tests -v`), which also runs `node --check` on the Web Studio's `<script>` and all static HTML event handlers, and verify 0 failures and 0 regressions.
2. **Live Server Restart & End-to-End Probe**: Whenever `optical_compiler/web.py` or backend modules are modified, restart the live server on `http://127.0.0.1:8765` and verify the live served HTML passes `node --check` and the modified HTTP endpoints return `200 OK`.
3. **Data & Profile Synchronization Check**: Verify that any added or modified profiles, presets, lenses, CLI flags, Web Studio endpoints/UI controls, and ComfyUI nodes are 100% synchronized across both `profiles/` and `optical_compiler/profiles_data/`.
4. **Mathematical & Signal-Processing Verification**: Verify numerical invariants (e.g., exact dimensions, aspect-ratio lock, SHA-256 provenance, pyramid reconstruction MSE, edge-halo suppression, flat-black preservation).
5. **Prohibited Token & Artist-Name Hygiene**: Verify zero prohibited artist/photographer names exist anywhere in prompts, profiles, or presets.
6. **Git Working Tree & Remote Sync Check**: Verify `git status` is clean and all verified commits are pushed to `origin/main` (when appropriate to the workflow).

## Mandatory Output Rubric Format at the End of Every Task
Always include a structured **Quality Audit Check Rubric** table at the end of your final response summarizing:
- **Check ID & Category** (Architecture, Mathematical Accuracy, Cross-Layer Integration, Automated Tests, Security/Hygiene, Git/Deployment)
- **Verification Method / Command Executed**
- **Measured Result / Metric**
- **Status (`PASS` / `FAIL`)**
