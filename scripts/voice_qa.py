import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


@dataclass
class VoiceCase:
    audio: str
    expected: str
    language: str = "auto"
    provider: str = "whisper"


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    # Keep unicode word characters while removing punctuation
    text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text


def token_f1(predicted: str, expected: str) -> float:
    p_tokens = normalize_text(predicted).split()
    e_tokens = normalize_text(expected).split()
    if not p_tokens and not e_tokens:
        return 1.0
    if not p_tokens or not e_tokens:
        return 0.0

    p_set = set(p_tokens)
    e_set = set(e_tokens)
    overlap = len(p_set.intersection(e_set))
    precision = overlap / max(len(p_set), 1)
    recall = overlap / max(len(e_set), 1)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def transcribe(endpoint: str, case: VoiceCase) -> dict[str, Any]:
    with open(case.audio, "rb") as fh:
        files = {"file": fh}
        data = {
            "language": case.language,
            "provider": case.provider,
        }
        response = requests.post(endpoint, files=files, data=data, timeout=180)
    response.raise_for_status()
    return response.json()


def load_cases(path: Path) -> list[VoiceCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    cases: list[VoiceCase] = []
    for item in raw:
        cases.append(
            VoiceCase(
                audio=item["audio"],
                expected=item["expected"],
                language=item.get("language", "auto"),
                provider=item.get("provider", "whisper"),
            )
        )
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description="EcoTour voice transcription QA smoke test")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8000/api/voice/transcribe")
    parser.add_argument("--cases", default="app/data/voice_test_cases.json")
    parser.add_argument("--min-f1", type=float, default=0.45)
    args = parser.parse_args()

    cases_path = Path(args.cases)
    if not cases_path.exists():
        raise FileNotFoundError(f"Cases file not found: {cases_path}")

    cases = load_cases(cases_path)
    failures = 0

    print("Voice QA Results")
    print("=" * 70)
    for index, case in enumerate(cases, start=1):
        audio_path = Path(case.audio)
        if not audio_path.exists():
            print(f"[{index}] MISSING audio file: {audio_path}")
            failures += 1
            continue

        try:
            result = transcribe(args.endpoint, case)
            text = (result.get("text") or "").strip()
            f1 = token_f1(text, case.expected)
            status = "PASS" if f1 >= args.min_f1 else "FAIL"
            print(f"[{index}] {status} | provider={result.get('provider')} | lang={result.get('language')} | f1={f1:.2f}")
            print(f" expected: {case.expected}")
            print(f" got     : {text}")
            warning = result.get("warning")
            if warning:
                print(f" warning : {warning}")
            print("-" * 70)
            if status == "FAIL":
                failures += 1
        except Exception as exc:
            failures += 1
            print(f"[{index}] ERROR: {exc}")
            print("-" * 70)

    if failures:
        print(f"Voice QA completed with {failures} failing case(s).")
        return 1

    print("Voice QA completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
