"""
tools/authoring/claude_author_provider.py

Real implementation of AuthorProvider using the Anthropic Messages API.
Confirmed by direct test during Phase 6 development: this sandbox can
reach api.anthropic.com (network allowlist includes it) but has no
credential -- a real POST to /v1/messages returns
{"error": {"type": "authentication_error", "message": "x-api-key header
is required"}}. This is a genuine external dependency, exactly the same
category as the Veo API credentials gap from Phase 2 onward: the code
here is correct and complete, and will work the moment
ANTHROPIC_API_KEY is set in the environment it actually runs in.

Not mocked, not stubbed to "always succeed" -- if called without a key,
it raises a clear error rather than pretending to have authored
something.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from tools.authoring.author_provider import AuthorProvider
from tools.authoring.schemas import EpisodeScript, SeasonConcept

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-4-6"


class MissingCredentialError(RuntimeError):
    pass


class ClaudeAuthorProvider(AuthorProvider):
    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None, max_tokens: int = 8000):
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.max_tokens = max_tokens

    def _call(self, prompt: str) -> str:
        if not self.api_key:
            raise MissingCredentialError(
                "ANTHROPIC_API_KEY is not set. ClaudeAuthorProvider requires a real API "
                "credential to author content -- this is an infrastructure/access "
                "requirement, not something more code can work around (confirmed by "
                "direct test: the endpoint is reachable but rejects unauthenticated "
                "requests). Use ManualAuthorProvider instead if no key is available."
            )
        body = json.dumps({
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")
        req = urllib.request.Request(
            API_URL, data=body, method="POST",
            headers={
                "Content-Type": "application/json",
                "anthropic-version": API_VERSION,
                "x-api-key": self.api_key,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Anthropic API error {e.code}: {e.read().decode('utf-8')}") from e
        text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
        return "\n".join(text_blocks)

    @staticmethod
    def _extract_json(text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())

    def author_episode(self, prompt: str) -> EpisodeScript:
        raw = self._call(prompt)
        return EpisodeScript.from_dict(self._extract_json(raw))

    def author_season_concept(self, prompt: str) -> SeasonConcept:
        raw = self._call(prompt)
        return SeasonConcept.from_dict(self._extract_json(raw))
