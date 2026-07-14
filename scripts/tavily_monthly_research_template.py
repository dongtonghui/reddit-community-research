#!/usr/bin/env python3
"""
Monthly Tavily Reddit pain-point monitor.
Run via: python3 scripts/run_monthly_research.py

Reads TAVILY_API_KEY from environment, runs `tvly research` for each brand,
saves JSON output to data/, and writes a summary file.
"""

import json
import os
import shlex
import subprocess
import time
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    env_path = os.path.expanduser("~/.hermes/home/.hermes/tavily.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("export TAVILY_API_KEY="):
                    TAVILY_API_KEY = line.split("=", 1)[1].strip().strip('"')
                    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
                    break

BRANDS = [
    "Gardyn",
    "AeroGarden",
    "LettuceGrow",
]


def run_tavily_research(query: str, model: str = "mini") -> dict | None:
    """Run `tvly research` and return parsed JSON."""
    if not TAVILY_API_KEY:
        raise RuntimeError("TAVILY_API_KEY not found in env or env file")

    cmd = ["tvly", "research", query, "--model", model, "--json"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "TAVILY_API_KEY": TAVILY_API_KEY},
    )
    if result.returncode != 0:
        print(f"Error running tvly: {result.stderr}", file=os.sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", file=os.sys.stderr)
        return {"raw": result.stdout[:2000]}


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(script_dir, "..", "data"))
    os.makedirs(data_dir, exist_ok=True)

    run_date = datetime.now().strftime("%Y-%m-%d")
    summary = {
        "run_date": run_date,
        "next_run": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "queries": [],
    }

    for brand in BRANDS:
        query = f"{brand} indoor garden Reddit complaints problems pain points last 12 months"
        print(f"Running: {brand} ...")
        result = run_tavily_research(query, model="mini")
        if result:
            filename = f"{brand.lower()}_pain_points_{run_date}.json"
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "w") as f:
                json.dump(result, f, indent=2)
            print(f"  Saved: {filepath}")
            summary["queries"].append(
                {
                    "name": brand,
                    "query": query,
                    "file": filename,
                    "word_count": len(result.get("content", "")),
                    "source_count": len(result.get("sources", [])),
                }
            )
        time.sleep(2)

    summary_path = os.path.join(data_dir, f"summary_{run_date}.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved: {summary_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
