"""
Phase 0 Kill Gate: Can AI Read Charts?

Tests whether vision AI (Claude and optionally Gemini) can accurately read
indicator values from TradingView chart screenshots.

Usage:
  1. Take 5 TradingView screenshots of SOL/USDC with EMA 21, EMA 50, RSI 14, Bollinger Bands
  2. Save them to chart_test_images/ directory
  3. Create chart_test_ground_truth.json with actual values
  4. Run: python chart_reading_test.py

Kill gate: >= 85% accuracy on indicator value reading -> PROCEED
"""

import base64
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

IMAGE_DIR = Path("chart_test_images")
GROUND_TRUTH_FILE = Path("chart_test_ground_truth.json")

CHART_READING_PROMPT = """List every indicator value visible on this TradingView chart with exact numbers.

For each indicator you can see, report:
- Indicator name (e.g., EMA 21, EMA 50, RSI 14, Bollinger Bands upper/middle/lower)
- Current value (the most recent/rightmost value)
- Timeframe shown on the chart

Output as JSON:
{
  "timeframe": "4H",
  "asset": "SOL/USDC",
  "indicators": {
    "EMA_21": 145.32,
    "EMA_50": 142.18,
    "RSI_14": 62.5,
    "BB_upper": 152.10,
    "BB_middle": 144.50,
    "BB_lower": 136.90,
    "price_close": 146.80
  }
}

Be as precise as possible. Read the exact numbers from the chart axis/labels."""


def encode_image(filepath: str) -> str:
    with open(filepath, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def get_media_type(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    return {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(ext, "image/png")


def read_chart_claude(image_path: str) -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    b64 = encode_image(image_path)
    media_type = get_media_type(image_path)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                {"type": "text", "text": CHART_READING_PROMPT},
            ],
        }],
    )
    raw = response.content[0].text
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse Claude response: {raw[:200]}")
        return {}


def read_chart_gemini(image_path: str) -> dict:
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set -- skipping Gemini test")
        return {}
    try:
        from google import genai
        from google.genai import types
        import PIL.Image

        client = genai.Client(api_key=GEMINI_API_KEY)
        img = PIL.Image.open(image_path)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[CHART_READING_PROMPT, img],
        )
        raw = response.text
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
        return json.loads(raw)
    except ImportError:
        logger.warning("google-genai not installed -- skipping Gemini")
        return {}
    except Exception as e:
        logger.error(f"Gemini chart reading failed: {e}")
        return {}


def calculate_accuracy(predicted: dict, actual: dict, tolerance_pct: float = 1.0) -> dict:
    pred_indicators = predicted.get("indicators", {})
    actual_indicators = actual.get("indicators", {})
    total = 0
    correct = 0
    details = []
    for key, actual_val in actual_indicators.items():
        total += 1
        pred_val = pred_indicators.get(key)
        if pred_val is None:
            details.append({"indicator": key, "actual": actual_val, "predicted": None, "match": False, "error_pct": None})
            continue
        if actual_val == 0:
            match = pred_val == 0
            error_pct = None
        else:
            error_pct = abs(pred_val - actual_val) / abs(actual_val) * 100
            match = error_pct <= tolerance_pct
        if match:
            correct += 1
        details.append({"indicator": key, "actual": actual_val, "predicted": pred_val, "match": match, "error_pct": round(error_pct, 2) if error_pct is not None else None})
    accuracy = (correct / total * 100) if total > 0 else 0
    return {"total_indicators": total, "correct": correct, "accuracy_pct": round(accuracy, 1), "details": details}


def create_sample_ground_truth():
    sample = {
        "chart_1.png": {
            "timeframe": "4H",
            "asset": "SOL/USDC",
            "indicators": {
                "EMA_21": 145.32,
                "EMA_50": 142.18,
                "RSI_14": 62.5,
                "BB_upper": 152.10,
                "BB_middle": 144.50,
                "BB_lower": 136.90,
                "price_close": 146.80
            }
        },
        "_instructions": "Replace with actual values from your TradingView screenshots. Add entries for chart_2.png through chart_5.png."
    }
    GROUND_TRUTH_FILE.write_text(json.dumps(sample, indent=2))
    logger.info(f"Sample ground truth written to {GROUND_TRUTH_FILE}")


def run_test():
    print("=" * 60)
    print("PHASE 0 KILL GATE: Can AI Read Charts?")
    print("=" * 60)

    if not IMAGE_DIR.exists():
        print(f"\n[SETUP NEEDED] Create directory: {IMAGE_DIR}/")
        print("Save 5 TradingView screenshots there (SOL/USDC with EMA 21, EMA 50, RSI 14, BBands)")
        IMAGE_DIR.mkdir(exist_ok=True)
        create_sample_ground_truth()
        print(f"Sample ground truth written to {GROUND_TRUTH_FILE}")
        print("Fill in actual values, then re-run this script.")
        return

    images = sorted(IMAGE_DIR.glob("*.png")) + sorted(IMAGE_DIR.glob("*.jpg"))
    if not images:
        print(f"\n[SETUP NEEDED] No images found in {IMAGE_DIR}/")
        return

    if not GROUND_TRUTH_FILE.exists():
        create_sample_ground_truth()
        print(f"\n[SETUP NEEDED] Fill in {GROUND_TRUTH_FILE} with actual indicator values.")
        return

    with open(GROUND_TRUTH_FILE) as f:
        ground_truth = json.load(f)
    ground_truth.pop("_instructions", None)

    print(f"\nFound {len(images)} chart images")
    print(f"Ground truth entries: {len(ground_truth)}")

    all_accuracies = {"claude": [], "gemini": []}

    for img_path in images:
        filename = img_path.name
        actual = ground_truth.get(filename)
        if not actual:
            print(f"\n[SKIP] {filename} -- no ground truth entry")
            continue
        print(f"\n--- {filename} ---")

        print("  Claude Vision...")
        claude_result = read_chart_claude(str(img_path))
        if claude_result:
            claude_acc = calculate_accuracy(claude_result, actual)
            all_accuracies["claude"].append(claude_acc["accuracy_pct"])
            print(f"  Claude: {claude_acc['accuracy_pct']}% ({claude_acc['correct']}/{claude_acc['total_indicators']})")
            for d in claude_acc["details"]:
                status = "OK" if d["match"] else "MISS"
                err = f" ({d['error_pct']}% off)" if d["error_pct"] is not None and not d["match"] else ""
                print(f"    [{status}] {d['indicator']}: actual={d['actual']}, predicted={d['predicted']}{err}")

        if GEMINI_API_KEY:
            print("  Gemini 2.5 Flash...")
            gemini_result = read_chart_gemini(str(img_path))
            if gemini_result:
                gemini_acc = calculate_accuracy(gemini_result, actual)
                all_accuracies["gemini"].append(gemini_acc["accuracy_pct"])
                print(f"  Gemini: {gemini_acc['accuracy_pct']}% ({gemini_acc['correct']}/{gemini_acc['total_indicators']})")

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    kill_gate_pass = False
    for model, accs in all_accuracies.items():
        if accs:
            avg = sum(accs) / len(accs)
            print(f"\n{model.upper()}: Average accuracy = {avg:.1f}% across {len(accs)} charts")
            if avg >= 85:
                print(f"  -> PASS (>= 85% threshold)")
                kill_gate_pass = True
            else:
                print(f"  -> FAIL (< 85% threshold)")

    print("\n" + "=" * 60)
    if kill_gate_pass:
        print("KILL GATE: PASS -- Proceed to Phase 1")
    elif not any(all_accuracies.values()):
        print("KILL GATE: NOT RUN -- No test results")
    else:
        print("KILL GATE: FAIL -- Pivot to transcript-only or abandon video pipeline")
    print("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_test()
