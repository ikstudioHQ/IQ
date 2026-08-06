"""
tools/orchestration/veo_executor.py

Real implementation of the actual Veo call, following the documented
async long-running-operation pattern (POST .../models/{model}:predictLongRunning
-> poll GET .../{operation_name} until done -> read result). Endpoint
shape confirmed via ai.google.dev/gemini-api/docs/video and the Gemini
API forum during Phase 7 development -- NOT exercised against a live
Veo endpoint in this environment, because (same as ClaudeAuthorProvider)
no credential is available here. Raises MissingVeoCredentialError
rather than faking success, exactly like every other external-dependency
seam in this project.

Frame extraction, by contrast, IS fully real and tested here -- ffmpeg
is actually installed in this environment, so extract_last_frame() is
exercised against a real synthetically-generated video, not mocked.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


class MissingVeoCredentialError(RuntimeError):
    pass


class VeoExecutionError(RuntimeError):
    pass


class VeoExecutor:
    def __init__(self, api_key: Optional[str] = None, poll_interval_seconds: float = 5.0,
                 max_poll_seconds: float = 600.0):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("VEO_API_KEY")
        self.poll_interval_seconds = poll_interval_seconds
        self.max_poll_seconds = max_poll_seconds

    def generate(self, model_id: str, payload: dict) -> dict:
        """payload is exactly what VideoProvider.build_payload() produces.
        Its own "model" key is stripped here since the real endpoint takes
        the model in the URL, not the body. Returns the completed
        operation's raw response dict."""
        if not self.api_key:
            raise MissingVeoCredentialError(
                "No GEMINI_API_KEY/VEO_API_KEY set. This is the same class of external "
                "dependency documented since Phase 2 -- the request payload is built and "
                "correct; sending it requires a real credential this environment doesn't have."
            )
        body = {k: v for k, v in payload.items() if k != "model"}
        start_url = f"{GEMINI_API_BASE}/models/{model_id}:predictLongRunning"
        operation_name = self._post(start_url, body)["name"]
        return self._poll(operation_name)

    def _post(self, url: str, body: dict) -> dict:
        req = urllib.request.Request(
            url, data=json.dumps(body).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key},
        )
        return self._send(req)

    def _get(self, url: str) -> dict:
        req = urllib.request.Request(url, method="GET", headers={"x-goog-api-key": self.api_key})
        return self._send(req)

    @staticmethod
    def _send(req: "urllib.request.Request") -> dict:
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise VeoExecutionError(f"Veo API error {e.code}: {e.read().decode('utf-8')}") from e

    def _poll(self, operation_name: str) -> dict:
        elapsed = 0.0
        url = f"{GEMINI_API_BASE}/{operation_name}"
        while elapsed < self.max_poll_seconds:
            data = self._get(url)
            if data.get("done"):
                if "error" in data:
                    raise VeoExecutionError(f"Veo generation failed: {data['error']}")
                return data
            time.sleep(self.poll_interval_seconds)
            elapsed += self.poll_interval_seconds
        raise VeoExecutionError(f"Veo generation did not complete within {self.max_poll_seconds}s")


def extract_last_frame(video_path: str, output_image_path: str) -> Path:
    """Real ffmpeg invocation, not a stub. Grabs the last frame of the
    given video. Raises FileNotFoundError if ffmpeg isn't on PATH -- a
    real, separate infrastructure requirement, documented rather than
    silently skipped."""
    if shutil.which("ffmpeg") is None:
        raise FileNotFoundError(
            "ffmpeg is not installed / not on PATH. Last-frame extraction requires it. "
            "This is an infrastructure requirement for whatever environment actually runs "
            "generation, separate from the Veo credential requirement."
        )
    video_p = Path(video_path)
    output_p = Path(output_image_path)
    output_p.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["ffmpeg", "-y", "-sseof", "-1", "-i", str(video_p), "-update", "1", "-q:v", "2", str(output_p)],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not output_p.exists():
        raise VeoExecutionError(f"ffmpeg frame extraction failed: {result.stderr[-500:]}")
    return output_p


def save_video_from_operation(operation_response: dict, output_path: str) -> Path:
    """Best-effort extraction of video bytes/URI from a completed Veo
    operation. The exact field names for a completed video result were
    NOT verifiable against a live response in this environment (no
    credential to actually complete a real operation and inspect its
    shape) -- documented sources describe base64 video bytes OR a Cloud
    Storage URI depending on configuration, under
    response.generateVideoResponse.generatedSamples[0].video. Rather than
    guess silently, this function tries the documented shape and raises a
    clear, specific error if the real response doesn't match it, so a
    real run surfaces exactly what needs adjusting instead of silently
    producing an empty/wrong file."""
    import base64

    try:
        samples = operation_response["response"]["generateVideoResponse"]["generatedSamples"]
        video = samples[0]["video"]
    except (KeyError, IndexError, TypeError) as e:
        raise VeoExecutionError(
            f"Completed operation response did not match the documented shape "
            f"(response.generateVideoResponse.generatedSamples[0].video). Raw keys present: "
            f"{list(operation_response.get('response', {}).keys())}. This needs adjusting "
            f"against a real completed response, not guessed at."
        ) from e

    output_p = Path(output_path)
    output_p.parent.mkdir(parents=True, exist_ok=True)
    if "bytesBase64Encoded" in video:
        output_p.write_bytes(base64.b64decode(video["bytesBase64Encoded"]))
    elif "uri" in video:
        req = urllib.request.Request(video["uri"], headers={"x-goog-api-key": os.environ.get("GEMINI_API_KEY", "")})
        with urllib.request.urlopen(req, timeout=120) as resp:
            output_p.write_bytes(resp.read())
    else:
        raise VeoExecutionError(f"Video object has neither bytesBase64Encoded nor uri: {list(video.keys())}")
    return output_p
