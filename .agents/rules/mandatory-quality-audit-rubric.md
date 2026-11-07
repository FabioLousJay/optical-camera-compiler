---
trigger: always_on
description: Permanent Mandatory Finish-Line Quality Audit Check Rubric required at the completion of every task without user reminder.
---

# Permanent Mandatory Constraint: Finish-Line Quality Audit Check Rubric

At the finish of **every** engineering, research, profile addition, bug-fix, or feature implementation task, you **MUST** execute and present a comprehensive **Finish-Line Quality Audit Check Rubric** before concluding your response—without the user ever needing to ask for it.

## Mandatory Pre-Finish Verification Steps
1. **Automated Test Suite Execution**: Run the full unit and integration test suite (`.venv/bin/python -m unittest discover -s tests -v`) and verify 0 failures and 0 regressions.
2. **Data & Profile Synchronization Check**: Verify that any added or modified profiles, presets, lenses, CLI flags, Web Studio endpoints/UI controls, and ComfyUI nodes are 100% synchronized across both `profiles/` and `optical_compiler/profiles_data/`.
3. **Mathematical & Signal-Processing Verification**: Verify numerical invariants (e.g., exact dimensions, aspect-ratio lock, SHA-256 provenance, pyramid reconstruction MSE, edge-halo suppression, flat-black preservation).
4. **Prohibited Token & Artist-Name Hygiene**: Verify zero prohibited artist/photographer names exist anywhere in prompts, profiles, or presets.
5. **Git Working Tree & Remote Sync Check**: Verify `git status` is clean and all verified commits are pushed to `origin/main` (when appropriate to the workflow).

## Mandatory Output Rubric Format at the End of Every Task
Always include a structured **Quality Audit Check Rubric** table at the end of your final response summarizing:
- **Check ID & Category** (Architecture, Mathematical Accuracy, Cross-Layer Integration, Automated Tests, Security/Hygiene, Git/Deployment)
- **Verification Method / Command Executed**
- **Measured Result / Metric**
- **Status (`PASS` / `FAIL`)**
