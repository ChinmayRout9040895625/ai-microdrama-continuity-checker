"""One function, `structured_call`, hides which LLM backend is used.

- anthropic: official SDK, structured outputs via `client.messages.parse`
  (pinned to the configured model; no server-side model fallback).
- ollama:    local model through Ollama's /api/chat with a JSON schema.

Responses are cached on disk (keyed by provider/model/effort/prompt/schema), so a
re-run on unchanged input costs nothing and is deterministic.
"""
import hashlib
import json
import os
import threading
import time
from dataclasses import dataclass, field
from typing import TypeVar

import requests
from pydantic import BaseModel, ValidationError

from .config import PROMPT_VERSION, Settings

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    pass


@dataclass
class Usage:
    calls: int = 0
    cached_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def add(self, inp: int, out: int, secs: float, cached: bool) -> None:
        with self._lock:
            self.calls += 1
            self.cached_calls += int(cached)
            self.input_tokens += inp
            self.output_tokens += out
            self.seconds += secs

    def as_dict(self) -> dict:
        return {k: getattr(self, k) for k in ("calls", "cached_calls", "input_tokens", "output_tokens", "seconds")}


class LLM:
    def __init__(self, settings: Settings):
        self.s = settings
        self.usage = Usage()
        os.makedirs(self.s.cache_dir, exist_ok=True)
        self._client = None
        if self.s.provider == "anthropic":
            import anthropic

            self._anthropic = anthropic
            self._client = anthropic.Anthropic(max_retries=4)
        elif self.s.provider != "ollama":
            raise LLMError(f"Unknown LLM_PROVIDER '{self.s.provider}' (use 'anthropic' or 'ollama')")

    # ------------------------------------------------------------------
    def structured_call(self, step: str, system: str, user: str, schema: type[T]) -> tuple[T, str]:
        """Return (parsed object, raw JSON text). `step` is 'extract' or 'check'."""
        model, effort = self.s.model_for(step), self.s.effort_for(step)
        key_src = json.dumps([self.s.provider, model, effort, PROMPT_VERSION, schema.__name__, system, user])
        path = os.path.join(self.s.cache_dir, hashlib.sha256(key_src.encode()).hexdigest()[:24] + ".json")

        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)["raw"]
            self.usage.add(0, 0, 0.0, cached=True)
            return schema.model_validate_json(raw), raw

        t0 = time.time()
        if self.s.provider == "anthropic":
            raw, inp, out = self._call_anthropic(model, effort, system, user, schema)
        else:
            raw, inp, out = self._call_ollama(model, system, user, schema)
        self.usage.add(inp, out, time.time() - t0, cached=False)

        parsed = schema.model_validate_json(raw)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"model": model, "effort": effort, "raw": raw}, f)
        return parsed, raw

    # ------------------------------------------------------------------
    def _call_anthropic(self, model, effort, system, user, schema):
        # No server-side model fallback: every call runs on exactly the configured model,
        # and a refusal surfaces as an error instead of silently switching models.
        resp = self._client.messages.parse(
            model=model,
            max_tokens=16000,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_format=schema,
            output_config={"effort": effort},
        )
        if resp.stop_reason == "refusal":
            raise LLMError(f"Model refused: {getattr(resp, 'stop_details', None)}")
        if resp.stop_reason == "max_tokens":
            raise LLMError("Response hit max_tokens; input episode is probably too long")
        raw = next((b.text for b in resp.content if b.type == "text"), None)
        if raw is None:
            raise LLMError("No text block in response")
        return raw, resp.usage.input_tokens, resp.usage.output_tokens

    def _call_ollama(self, model, system, user, schema):
        last_err = None
        for _ in range(2):  # one retry: small local models sometimes emit invalid JSON
            r = requests.post(
                f"{self.s.ollama_url}/api/chat",
                json={
                    "model": model,
                    "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                    "format": schema.model_json_schema(),
                    "stream": False,
                    # cap output: small models can loop forever inside JSON mode
                    "options": {"temperature": 0, "num_ctx": 8192, "num_predict": 2500},
                },
                timeout=900,
            )
            r.raise_for_status()
            data = r.json()
            raw = data["message"]["content"]
            try:
                schema.model_validate_json(raw)
                return raw, data.get("prompt_eval_count", 0), data.get("eval_count", 0)
            except ValidationError as e:
                last_err = e
        raise LLMError(f"Ollama returned invalid JSON twice: {last_err}")
