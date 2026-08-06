# Release Validation — v2.72

From the extracted repository root on Windows, macOS, or Linux:

`python tools/validate_release.py`

The launcher anchors execution to its own repository, disables pytest cache creation, runs tests, validator, distribution preflight, runtime compilation, song/episode compilation, and final hygiene checks. No shell-specific grep/sed commands are required.

## Clean-source validation

Use `python tools/validate_release.py` as the supported release check. It rebuilds derived runtime/song/episode outputs before running tests that inspect those outputs, refreshes the deterministic source fingerprint, disables pytest cache/bytecode generation, then runs validator, preflight, and hygiene checks.

For ad-hoc pytest runs, prefer `python -B -m pytest -p no:cacheprovider` so local bytecode/cache files do not intentionally trip the release-hygiene gate later.
