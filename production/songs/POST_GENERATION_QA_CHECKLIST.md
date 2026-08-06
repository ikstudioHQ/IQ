# Post-Generation QA Checklist

Use this AFTER actually running a scene_XX.md prompt through Gemini and
getting real video back. This repository cannot verify these items
itself — it has no way to see generated video.

## Per-clip checklist
- [ ] Character appearance matches the locked identity in the prompt
      (skin tone, hair, clothing colors) — not just "close enough"
- [ ] Voice/performance matches the labeled performer (right character
      speaking/singing, not a different one)
- [ ] Lip-sync reasonably matches the exact words given
- [ ] Duration is close to the requested seconds (Gemini's actual
      output length can vary — note the real delta)
- [ ] No extra/missing characters beyond those listed as visible
- [ ] No religious content added or altered beyond what was specified
- [ ] No unsafe content (per the frozen content-safety policy)
- [ ] Ending frame reasonably sets up the next scene's continuity

## Classify any problem found using the real categories
- **PROMPT_DEFECT** — the compiled prompt itself was wrong/unclear →
  file against `tools/compile_gemini_scenes.py` or the canonical source
- **SOURCE_DEFECT** — canonical source data was wrong → correct the
  source file directly, then recompile (never patch the compiled output)
- **COMPILER_DEFECT** — the compiler mishandled correct source data →
  fix the compiler, add a regression test using this real example
- **MODEL_LIMITATION** — Gemini itself didn't follow a clear, correct
  instruction → do not change the repository for this alone
- **GENERATION_VARIANCE** — normal run-to-run difference → do not
  change the repository for this alone

Only the first three justify a repository change, per the frozen
compiler policy (VERSION_COMPATIBILITY.md v2.53).

## Real cross-song reuse check (once multiple songs are generated)
If the same character appears in 2+ generated songs, compare the
actual rendered appearance side by side — this repository's text-level
consistency check (AH, v2.53) can only confirm the *prompts* were
consistent, not that Gemini's actual rendering was.
