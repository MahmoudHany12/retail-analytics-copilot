# run_agent_hybrid.py
import json
import argparse
from agent.graph_hybrid import HybridAgent

def run(batch_file: str, out_file: str):
    agent = HybridAgent()
    results = []

    # BOM-safe and streaming read
    with open(batch_file, "r", encoding="utf-8-sig") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON on line {line_num}: {e}")
                continue

            qid = item.get("id", f"line{line_num}")
            question = item.get("question", "")
            format_hint = item.get("format_hint", "")
            print(f"Processing {qid} ...")
            try:
                res = agent.answer(qid, question, format_hint)
                results.append(res)
            except Exception as e:
                print(f"Error processing question {qid}: {e}")
                results.append({
                    "id": qid,
                    "final_answer": None,
                    "sql": "",
                    "confidence": 0.0,
                    "explanation": str(e),
                    "citations": [],
                })

    # Write results to JSONL
    with open(out_file, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Wrote {len(results)} results to {out_file}")


def main():
    parser = argparse.ArgumentParser(description="Run Retail Analytics HybridAgent on JSONL batch")
    parser.add_argument("--batch", required=True, help="Input JSONL file with questions")
    parser.add_argument("--out", required=True, help="Output JSONL file for results")
    args = parser.parse_args()
    run(args.batch, args.out)


if __name__ == "__main__":
    main()
