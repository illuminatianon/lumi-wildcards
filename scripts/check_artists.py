#!/usr/bin/env -S uv run --quiet
# /// script
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from openrouter_inference import OpenRouterClient, extract_message_text


SYSTEM_PROMPT = (
    "You are an art historian assistant. "
    "Be precise and concise. "
    "If you are unsure whether an artist is real or identifiable, return Unrecognized."
)

USER_PROMPT_TEMPLATE = (
    "Create a brief description (max 40 words) of the visual art style of \"{artist}\". "
    "If you do not recognize the artist, respond exactly with \"Unrecognized\". "
    "Output only the description or \"Unrecognized\"."
)

UNRECOGNIZED_RE = re.compile(r"^unrecognized\W*$", re.IGNORECASE)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_artists(path: Path) -> list[str]:
    artists: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        artists.append(line)
    return artists


def is_unrecognized(text: str) -> bool:
    return bool(UNRECOGNIZED_RE.match(text.strip()))


def load_existing_results(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    existing: dict[str, dict] = {}
    for item in data.get("results", []):
        artist = item.get("artist")
        if isinstance(artist, str):
            existing[artist] = item
    return existing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check which artists are recognized by an OpenRouter model."
    )
    parser.add_argument(
        "--artists-file",
        type=Path,
        default=Path("wildcards/std/artists.txt"),
        help="Path to artist list file (default: wildcards/std/artists.txt)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artists_check_kimi-k2-0905.json"),
        help="Output JSON file path (default: artists_check_kimi-k2-0905.json)",
    )
    parser.add_argument(
        "--model",
        default="moonshotai/kimi-k2-0905",
        help="OpenRouter model id (default: moonshotai/kimi-k2-0905)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature (default: 0.0)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=80,
        help="Max completion tokens per artist (default: 80)",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.2,
        help="Delay between API calls in seconds (default: 0.2)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="HTTP timeout in seconds (default: 60)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing output file entries.",
    )
    args = parser.parse_args()

    if not args.artists_file.exists():
        print(f"Error: artists file not found: {args.artists_file}", file=sys.stderr)
        return 1

    artists = load_artists(args.artists_file)
    if not artists:
        print("Error: no artists found in input file.", file=sys.stderr)
        return 1

    existing = load_existing_results(args.output) if args.resume else {}

    try:
        client = OpenRouterClient.from_env(timeout=args.timeout)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print("Set OPENROUTER_API_KEY before running this script.", file=sys.stderr)
        return 1

    results: list[dict] = []
    recognized_count = 0
    unrecognized_count = 0
    error_count = 0

    for idx, artist in enumerate(artists, start=1):
        if artist in existing:
            entry = existing[artist]
            results.append(entry)
            status = entry.get("status")
            if status == "ok":
                if entry.get("recognized"):
                    recognized_count += 1
                else:
                    unrecognized_count += 1
            elif status == "error":
                error_count += 1
            print(f"[{idx}/{len(artists)}] {artist}: reused existing result")
            continue

        print(f"[{idx}/{len(artists)}] {artist}: querying {args.model}...")
        user_prompt = USER_PROMPT_TEMPLATE.format(artist=artist)
        checked_at = utc_now_iso()

        try:
            response = client.chat_completion(
                model=args.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
            text = extract_message_text(response)
            normalized_text = " ".join(text.split())
            recognized = bool(normalized_text) and not is_unrecognized(normalized_text)
            status = "ok"
            if recognized:
                recognized_count += 1
            else:
                unrecognized_count += 1

            entry = {
                "artist": artist,
                "status": status,
                "recognized": recognized,
                "response": normalized_text,
                "checked_at": checked_at,
                "model": args.model,
            }
        except Exception as exc:  # noqa: BLE001 - include all request/runtime errors
            error_count += 1
            entry = {
                "artist": artist,
                "status": "error",
                "recognized": False,
                "response": "",
                "error": str(exc),
                "checked_at": checked_at,
                "model": args.model,
            }
            print(f"  Error: {exc}", file=sys.stderr)

        results.append(entry)

        if args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "generated_at": utc_now_iso(),
            "artists_file": str(args.artists_file),
            "model": args.model,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "total_artists": len(artists),
            "recognized": recognized_count,
            "unrecognized": unrecognized_count,
            "errors": error_count,
            "system_prompt": SYSTEM_PROMPT,
            "user_prompt_template": USER_PROMPT_TEMPLATE,
        },
        "results": results,
    }

    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("\nDone.")
    print(f"Wrote: {args.output}")
    print(
        "Counts: "
        f"recognized={recognized_count}, "
        f"unrecognized={unrecognized_count}, "
        f"errors={error_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
