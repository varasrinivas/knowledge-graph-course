"""M08 solution — diff-scoped OKF concept refresh.

Pipeline: git diff -> owning service -> regenerate Dependencies from the
structural graph -> append log.md -> lint. Fails loudly at every stage.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

LABS = Path(__file__).resolve().parents[2]

# Changed-path prefix -> (concept relative path, service module prefix)
SERVICE_MAP = {
    "services/billing": ("services/billing-service.md", "services.billing"),
    "services/orders": ("services/orders-service.md", "services.orders"),
    "services/notifications": ("services/notifications-service.md", "services.notifications"),
    "shared": ("services/shared-libraries.md", "shared"),
}


def sh(args: list[str], cwd: Path) -> str:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def changed_files(repo: Path) -> list[str]:
    out = sh(["git", "diff", "--name-only", "HEAD~1", "HEAD"], cwd=repo)
    return [line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()]


def build_graph(repo: Path) -> dict:
    out = repo / "graphify-out" / "graph.json"
    out.parent.mkdir(exist_ok=True)
    sh([sys.executable, str(LABS / "shared_tools" / "kg_extract.py"),
        str(repo), "--out", str(out)], cwd=repo)
    return json.loads(out.read_text(encoding="utf-8"))


def service_dependencies(graph: dict, module_prefix: str) -> list[str]:
    """Outbound cross-service call edges for one service, from the graph."""
    deps = set()
    for edge in graph["edges"]:
        src_mod = edge["source"].split(":", 1)[1]
        dst_mod = edge["target"].split(":", 1)[1]
        if src_mod.startswith(module_prefix) and not dst_mod.startswith(module_prefix):
            deps.add(f"- calls `{dst_mod}` ({edge['provenance']})")
    return sorted(deps)


def refresh_concept(bundle: Path, concept_rel: str, deps: list[str]) -> None:
    path = bundle / concept_rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        text = path.read_text(encoding="utf-8")
        head, sep, _tail = text.partition("## Dependencies")
        base = head if sep else text
    else:
        name = Path(concept_rel).stem
        base = f"---\ntype: Service\ntitle: {name}\n---\n\n# {name}\n\n"
    dep_block = "## Dependencies\n" + ("\n".join(deps) if deps else "- (none detected)") + "\n"
    path.write_text(base.rstrip() + "\n\n" + dep_block, encoding="utf-8")
    print(f"[enrich] refreshed Dependencies ({len(deps)} edges) in {path.name}")


def append_log(bundle: Path, concepts: list[str]) -> None:
    log = bundle / "log.md"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = f"\n## {stamp}\n" + "".join(f"- refreshed {c} from commit diff\n" for c in concepts)
    log.write_text((log.read_text(encoding="utf-8") if log.exists() else "# Bundle log\n") + entry,
                   encoding="utf-8")
    print("[enrich] log.md updated")


def lint(bundle: Path) -> None:
    validator = LABS / "M06-okf-authoring" / "solution" / "validate.py"
    result = subprocess.run([sys.executable, str(validator), str(bundle)],
                            capture_output=True, text=True)
    print(f"[enrich] lint: {result.stdout.strip()}")
    if result.returncode != 0:
        raise RuntimeError("lint failed — refusing to publish the bundle")


def main(repo: Path) -> int:
    bundle = repo / "knowledge"
    files = changed_files(repo)
    touched: dict[str, str] = {}
    for f in files:
        for prefix, (concept, module_prefix) in SERVICE_MAP.items():
            if f.startswith(prefix):
                touched[concept] = module_prefix
                print(f"[enrich] changed: {f} -> concept {Path(concept).stem}")
    if not touched:
        print("[enrich] no service files in diff — nothing to do")
        return 0

    graph = build_graph(repo)  # diff decides WHAT to refresh; graph supplies the edges
    for concept, module_prefix in touched.items():
        refresh_concept(bundle, concept, service_dependencies(graph, module_prefix))
    append_log(bundle, [Path(c).stem for c in touched])
    lint(bundle)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: refresh_concepts.py <repo_root>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1]).resolve()))
