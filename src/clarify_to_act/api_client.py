from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


RESPONSES_URL = "https://api.openai.com/v1/responses"


class OpenAIAPIError(RuntimeError):
    pass


def read_api_key(path: str | None = None) -> str:
    if path:
        key_path = Path(path)
        if key_path.exists():
            return key_path.read_text(encoding="utf-8").strip()
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise OpenAIAPIError("No API key found. Pass --api-key-path or set OPENAI_API_KEY.")
    return key


def stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def extract_output_text(response: dict) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    texts: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                texts.append(content["text"])
    if texts:
        return "\n".join(texts)
    return json.dumps(response)


def parse_json_object(text: str) -> dict:
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        parsed = json.loads(text[start : end + 1])
        if isinstance(parsed, dict):
            return parsed
    raise ValueError(f"Could not parse JSON object from model output: {text[:300]}")


class CachedResponsesClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        cache_path: str = "data/runs/api_cache.jsonl",
        timeout: int = 60,
        retries: int = 2,
        cache_only: bool = False,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.cache_path = Path(cache_path)
        self.timeout = timeout
        self.retries = retries
        self.cache_only = cache_only
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache: dict[str, dict] = {}
        if self.cache_path.exists():
            with self.cache_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        row = json.loads(line)
                        self.cache[row["cache_key"]] = row

    def complete_json(self, prompt: str, max_output_tokens: int = 300) -> tuple[dict, dict]:
        body = {
            "model": self.model,
            "input": prompt,
            "temperature": 0,
            "max_output_tokens": max_output_tokens,
            "store": False,
            "text": {"format": {"type": "json_object"}},
        }
        cache_key = stable_hash(body)
        if cache_key in self.cache:
            row = self.cache[cache_key]
            return row["parsed"], row
        if self.cache_only:
            raise OpenAIAPIError(f"Cache miss in cache-only mode for key {cache_key}.")

        raw_response = self._post(body)
        output_text = extract_output_text(raw_response)
        parsed = parse_json_object(output_text)
        row = {
            "cache_key": cache_key,
            "model": self.model,
            "created_at": time.time(),
            "prompt_hash": stable_hash(prompt),
            "parsed": parsed,
            "output_text": output_text,
            "usage": raw_response.get("usage", {}),
            "response_id": raw_response.get("id"),
        }
        with self.cache_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
        self.cache[cache_key] = row
        return parsed, row

    def _post(self, body: dict) -> dict:
        payload = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            RESPONSES_URL,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                body_text = exc.read().decode("utf-8", errors="replace")
                last_error = OpenAIAPIError(f"OpenAI HTTP {exc.code}: {body_text}")
                if exc.code not in {408, 409, 429, 500, 502, 503, 504}:
                    break
            except urllib.error.URLError as exc:
                last_error = exc
            if attempt < self.retries:
                time.sleep(1.5 * (attempt + 1))
        raise OpenAIAPIError(str(last_error))
