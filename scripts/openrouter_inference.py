#!/usr/bin/env python3
"""Shared OpenRouter chat inference helpers for local scripts."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, request


class OpenRouterClient:
    """Minimal OpenRouter chat completions client."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: int = 60,
        referer: str | None = None,
        title: str | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("OpenRouter API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.referer = referer
        self.title = title

    @classmethod
    def from_env(cls, *, timeout: int = 60) -> "OpenRouterClient":
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        return cls(api_key=api_key, timeout=timeout)

    def chat_completion(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.referer:
            headers["HTTP-Referer"] = self.referer
        if self.title:
            headers["X-Title"] = self.title

        req = request.Request(
            url=f"{self.base_url}/chat/completions",
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except error.HTTPError as exc:
            details = ""
            try:
                details = exc.read().decode("utf-8")
            except Exception:
                details = ""
            raise RuntimeError(
                f"OpenRouter request failed ({exc.code} {exc.reason}): {details.strip()}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(f"OpenRouter network error: {exc.reason}") from exc


def extract_message_text(response: dict[str, Any]) -> str:
    """Extract assistant text from OpenRouter chat completions response."""
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""

    message = choices[0].get("message", {})
    content = message.get("content", "")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts: list[str] = []
        for chunk in content:
            if isinstance(chunk, dict) and chunk.get("type") == "text":
                text = chunk.get("text", "")
                if isinstance(text, str) and text:
                    text_parts.append(text)
        return "\n".join(text_parts).strip()

    return ""
