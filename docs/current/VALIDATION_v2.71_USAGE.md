# Release Validation — v2.72

From the extracted repository root on Windows, macOS, or Linux:

`python tools/validate_release.py`

The launcher anchors execution to its own repository, disables pytest cache creation, runs tests, validator, distribution preflight, runtime compilation, song/episode compilation, and final hygiene checks. No shell-specific grep/sed commands are required.
