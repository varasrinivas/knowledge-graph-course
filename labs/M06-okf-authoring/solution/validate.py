"""M06 solution — OKF bundle validator."""
import sys
from pathlib import Path

import frontmatter

RECOMMENDED = ["title", "description", "resource", "tags", "timestamp"]


def validate_bundle(root: Path) -> int:
    errors, valid = 0, 0
    for path in sorted(root.rglob("*.md")):
        if path.name in {"index.md", "log.md"}:
            continue
        try:
            post = frontmatter.load(path)
        except Exception as exc:  # noqa: BLE001 - report any parse failure
            print(f"ERROR {path}: unparseable frontmatter ({exc})")
            errors += 1
            continue
        if not post.metadata.get("type"):
            print(f"ERROR {path}: missing required field 'type'")
            errors += 1
            continue
        valid += 1
        for field in RECOMMENDED:
            if field not in post.metadata:
                print(f"warn  {path}: missing recommended field '{field}'")
    print(f"{valid} concepts valid, {errors} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    bundle = Path(sys.argv[1] if len(sys.argv) > 1 else "knowledge")
    raise SystemExit(validate_bundle(bundle))
