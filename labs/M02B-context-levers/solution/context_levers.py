"""M02B solution — fix the poisoned transcript with the retrieve and offload levers.

The sibling course's M03B lab fixed a rotted transcript with the COMPRESS lever
(summarize-and-crop). This lab implements the two levers that lab left as a
gap, using this course's machinery:

  retrieve — replace duplicated grep dumps with ONE structural graph answer
             (M09's explore(), imported directly)
  offload  — replace in-history definition sprawl with ONE canonical OKF
             concept read (M06's weekly_active_users.md)

The check is offline and deterministic: a fixed run must still CONTAIN the
key facts an answer needs (necessary condition for correctness — the offline
equivalent of the sibling lab's "Run 2 must still cite the correct delivery
date"), while spending materially fewer tokens.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import frontmatter

LABS = Path(__file__).resolve().parents[2]

# ---- reuse the M09 server's graph tools (retrieve lever) --------------------
_spec = importlib.util.spec_from_file_location(
    "m09_server", LABS / "M09-mcp-graph-server" / "solution" / "server.py")
m09 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m09)

WAU_CONCEPT = (LABS / "M06-okf-authoring" / "solution" / "knowledge"
               / "analytics" / "metrics" / "weekly_active_users.md")

KEY_FACTS = {
    "direct caller": "verify_token",
    "transitive caller": "post_invoice",
    "WAU window": "7-day",
    "WAU exclusion": "internal test",
    "WAU basis": "completed order",
}


def tokens(text: str) -> int:
    return max(1, len(text) // 4)


class ContextBudget:
    """Slim mirror of the sibling lab's class: six layers + four arms."""

    def __init__(self, transcript: dict):
        self.t = transcript

    # -- layer accounting (same six layers as the sibling's account()) -------
    def account(self, t: dict | None = None) -> dict[str, int]:
        t = t or self.t
        return {
            "system": tokens(t["system"]),
            "tools": tokens(json.dumps(t["tools"])),
            "retrieved": tokens(json.dumps(t["retrieved"])),
            "history": tokens(json.dumps(t["history"])),
            "tool_results": tokens(json.dumps(t["tool_results"])),
            "current": tokens(t["current"]),
        }

    @staticmethod
    def render(t: dict) -> str:
        """Flatten a transcript into the text the model would actually see."""
        parts = [t["system"], json.dumps(t["tools"])]
        parts += [r["text"] for r in t["retrieved"]]
        parts += [f"{m['role']}: {m['content']}" for m in t["history"]]
        parts += [f"[{r['tool']}]\n{r['content']}" for r in t["tool_results"]]
        parts.append(t["current"])
        return "\n\n".join(parts)

    # -- arm 1: raw ----------------------------------------------------------
    def raw(self) -> dict:
        return self.t

    # -- arm 2: compress (the sibling lab's lever, naive extractive version) -
    def fix_by_compress(self, keep_recent: int = 4) -> dict:
        t = json.loads(json.dumps(self.t))  # deep copy
        dropped = t["history"][:-keep_recent]
        summary = " / ".join(m["content"].split(".")[0] for m in dropped)
        t["history"] = ([{"role": "system", "content": f"[summary of {len(dropped)} turns] {summary}"}]
                        + t["history"][-keep_recent:])
        t["tool_results"] = t["tool_results"][-2:]  # keep last 2, like the sibling
        return t

    # -- arm 3: retrieve (this course's lever: one graph answer) -------------
    def fix_by_retrieve(self) -> dict:
        t = json.loads(json.dumps(self.t))
        answer = m09.explore("decode_jwt")
        if "error" in answer:
            raise RuntimeError(f"graph could not resolve decode_jwt: {answer}")
        # name the transitive callers too (explore reports only the count) —
        # a BFS over the reverse index, the same walk M01 taught
        from collections import deque
        seeds = [n["id"] for n in m09._resolve("decode_jwt")]
        queue, seen = deque(seeds), set(seeds)
        transitive = []
        while queue:
            for edge in m09._reverse.get(queue.popleft(), []):
                if edge["source"] not in seen:
                    seen.add(edge["source"])
                    transitive.append(edge["source"].split(":", 1)[1])
                    queue.append(edge["source"])
        answer["transitive_callers"] = sorted(transitive)
        # one deterministic answer replaces every grep dump
        t["tool_results"] = [{"tool": "graph.explore('decode_jwt')",
                              "content": json.dumps(answer, indent=2)}]
        return t

    # -- arm 4: offload (this course's lever: one concept read) --------------
    def fix_by_offload(self) -> dict:
        t = json.loads(json.dumps(self.t))
        post = frontmatter.load(WAU_CONCEPT)
        concept = f"[OKF concept {post.metadata.get('title')}]\n{post.content}"
        # the canonical file replaces BOTH stale retrieved chunks...
        t["retrieved"] = [{"source": str(WAU_CONCEPT.name), "text": concept}]
        # ...and the WAU debate in history (it is settled knowledge now)
        t["history"] = [m for m in t["history"] if "WAU" not in m["content"]
                        and "wau" not in m["content"].lower()]
        return t

    # -- arm 5: combined (retrieve + offload) --------------------------------
    def fix_combined(self) -> dict:
        combined = ContextBudget(self.fix_by_offload()).fix_by_retrieve()
        return combined


def facts_present(t: dict) -> dict[str, bool]:
    text = ContextBudget.render(t).lower()
    return {label: needle.lower() in text for label, needle in KEY_FACTS.items()}


def main() -> int:
    m09.load_graph()  # builds orderflow graph.json once
    fixture = json.loads(
        (Path(__file__).parents[1] / "starter" / "poisoned_transcript.json")
        .read_text(encoding="utf-8"))
    budget = ContextBudget(fixture)

    print("Per-layer accounting (raw):")
    for layer, n in budget.account().items():
        print(f"  {layer:<13} {n:>6,} tokens")

    arms = {
        "raw": budget.raw(),
        "compress": budget.fix_by_compress(),
        "retrieve": budget.fix_by_retrieve(),
        "offload": budget.fix_by_offload(),
        "retrieve+offload": budget.fix_combined(),
    }

    print(f"\n{'arm':<18} {'tokens':>8} {'vs raw':>8}  facts preserved")
    print("-" * 66)
    raw_tokens = tokens(ContextBudget.render(arms["raw"]))
    ok = True
    for name, t in arms.items():
        n = tokens(ContextBudget.render(t))
        facts = facts_present(t)
        missing = [k for k, v in facts.items() if not v]
        status = "ALL" if not missing else f"MISSING: {', '.join(missing)}"
        print(f"{name:<18} {n:>8,} {n / raw_tokens:>7.0%}  {status}")
        if name in ("retrieve", "offload", "retrieve+offload"):
            # the levers this lab teaches must keep the facts they own
            owned = (["direct caller", "transitive caller"] if "retrieve" in name else []) \
                    + (["WAU window", "WAU exclusion", "WAU basis"] if "offload" in name else [])
            ok &= all(facts[k] for k in owned) and n < raw_tokens

    print("-" * 66)
    if "--check" in sys.argv:
        print("SUCCESS CRITERION " + ("MET" if ok else "NOT MET")
              + ": each lever preserves the facts it owns at fewer tokens than raw.")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
