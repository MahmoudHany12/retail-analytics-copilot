#!/usr/bin/env python3
"""Interactive runner to test the HybridAgent manually.

Usage examples (PowerShell):
  python run_interactive.py
  python run_interactive.py --out outputs_hybrid.jsonl

Type a blank question to exit. If --out is provided, each result is appended as a JSONL line.
"""
import argparse
import json
from agent.graph_hybrid import HybridAgent


def interactive(out_file: str | None = None) -> None:
    agent = HybridAgent()
    idx = 1
    results = []
    print("Interactive Retail Analytics tester. Enter an empty question to exit.")
    while True:
        try:
            q = input(f"[{idx}] question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q:
            break
        fmt = input(" format_hint (optional): ").strip()
        qid = f"interactive_{idx}"
        try:
            res = agent.answer(qid, q, fmt)
        except Exception as e:
            res = {
                "id": qid,
                "final_answer": None,
                "sql": "",
                "confidence": 0.0,
                "explanation": str(e),
                "citations": [],
            }

        # Pretty-print to console
        print("Result:")
        print(json.dumps(res, ensure_ascii=False, indent=2))

        # Optionally append to JSONL
        if out_file:
            with open(out_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")

        results.append(res)
        idx += 1

    if out_file:
        print(f"Wrote {len(results)} results to {out_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive tester for Retail Analytics HybridAgent")
    parser.add_argument("--out", help="Optional JSONL file to append results to")
    args = parser.parse_args()
    interactive(args.out)


if __name__ == "__main__":
    main()
