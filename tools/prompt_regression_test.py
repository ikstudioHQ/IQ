#!/usr/bin/env python3
"""
prompt_regression_test.py — catch quality drops after editing a prompt.

WHAT THIS SCRIPT DOES: manages fixtures and runs the diff/comparison step.
WHAT IT DOES NOT DO: call an LLM for you. This repository has no live model
API wired in, so "generate the new output" is a step your coding agent
(Claude Code, Cursor, etc. — whichever one is actually connected to a model)
must perform and save to disk. This script handles everything mechanical
around that: storing the baseline, diffing against a new run, and producing
a regression report an agent or human can review quickly instead of reading
two full episode packages side by side.

Workflow:
  1. Before editing a prompt file (e.g. story_prompt.md), run:
       python3 tools/prompt_regression_test.py capture <topic_slug>
     with the CURRENT (pre-edit) output already generated and saved at
     output_package/<topic_slug>/. This copies it into
     tests/fixtures/<topic_slug>/baseline/.
  2. Edit the prompt file.
  3. Regenerate the SAME topic through your agent, saved again at
     output_package/<topic_slug>/.
  4. Run:
       python3 tools/prompt_regression_test.py compare <topic_slug>
     This diffs baseline vs. new output file-by-file (line count change,
     which files changed, which files disappeared/appeared) and writes
     tests/fixtures/<topic_slug>/regression_report.md.
  5. A human (or agent) reads the report and judges whether the changes
     are the intended improvement or an unintended regression — this
     script flags *what* changed, not whether the change is good; that
     judgment still needs `phase4/engine/quality/rubric.md`.

Usage:
    python3 tools/prompt_regression_test.py capture <topic_slug>
    python3 tools/prompt_regression_test.py compare <topic_slug>
"""
import difflib
import os
import shutil
import sys


def capture(slug):
    src = os.path.join("output_package", slug)
    if not os.path.isdir(src):
        print(f"ERROR: {src} does not exist. Generate this episode's output first.")
        sys.exit(1)
    dst = os.path.join("tests", "fixtures", slug, "baseline")
    if os.path.exists(dst):
        print(f"Baseline already exists at {dst}. Delete it manually first if you want to recapture.")
        sys.exit(1)
    shutil.copytree(src, dst)
    print(f"Baseline captured: {dst}")


def compare(slug):
    baseline = os.path.join("tests", "fixtures", slug, "baseline")
    current = os.path.join("output_package", slug)
    if not os.path.isdir(baseline):
        print(f"ERROR: no baseline at {baseline}. Run 'capture' first, before editing the prompt.")
        sys.exit(1)
    if not os.path.isdir(current):
        print(f"ERROR: no current output at {current}. Regenerate this episode first.")
        sys.exit(1)

    baseline_files = set(os.listdir(baseline))
    current_files = set(os.listdir(current))

    report = []
    report.append(f"# Regression Report — {slug}\n")

    removed = baseline_files - current_files
    added = current_files - baseline_files
    if removed:
        report.append(f"## Files removed in new output ({len(removed)})")
        for f in sorted(removed):
            report.append(f"- {f}")
        report.append("")
    if added:
        report.append(f"## Files added in new output ({len(added)})")
        for f in sorted(added):
            report.append(f"- {f}")
        report.append("")

    common = baseline_files & current_files
    report.append(f"## Changed files ({len(common)} compared)\n")
    for f in sorted(common):
        bpath = os.path.join(baseline, f)
        cpath = os.path.join(current, f)
        try:
            b_lines = open(bpath, encoding="utf-8").readlines()
            c_lines = open(cpath, encoding="utf-8").readlines()
        except Exception:
            report.append(f"### {f}\n(binary or unreadable — skipped diff)\n")
            continue
        if b_lines == c_lines:
            continue
        diff = list(difflib.unified_diff(b_lines, c_lines, lineterm="",
                                          fromfile=f"baseline/{f}", tofile=f"current/{f}"))
        pct_change = abs(len(c_lines) - len(b_lines)) / max(len(b_lines), 1) * 100
        report.append(f"### {f} — {len(b_lines)} → {len(c_lines)} lines ({pct_change:.0f}% length change)")
        report.append("```diff")
        report.extend(diff[:60])
        if len(diff) > 60:
            report.append(f"... ({len(diff) - 60} more diff lines, truncated)")
        report.append("```\n")

    out_path = os.path.join("tests", "fixtures", slug, "regression_report.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"Regression report written: {out_path}")
    print("Review it against phase4/engine/quality/rubric.md before deciding "
          "whether these changes are an improvement or a regression.")


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("capture", "compare"):
        print(__doc__)
        sys.exit(1)
    cmd, slug = sys.argv[1], sys.argv[2]
    if cmd == "capture":
        capture(slug)
    else:
        compare(slug)


if __name__ == "__main__":
    main()
