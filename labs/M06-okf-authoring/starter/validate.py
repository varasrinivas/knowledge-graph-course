"""M06 starter — OKF bundle validator. Fill in TODO 3."""
import sys
from pathlib import Path

import frontmatter

RECOMMENDED = ["title", "description", "resource", "tags", "timestamp"]


def validate_bundle(root: Path) -> int:
    errors, valid = 0, 0
    for path in sorted(root.rglob("*.md")):
        if path.name in {"index.md", "log.md"}:
            continue
        # TODO 3:
        #  1. load the file with frontmatter.load (handle YAML parse errors:
        #     catch Exception, print the path, count as error, continue)
        #  2. if "type" missing or empty -> print error with path, errors += 1
        #  3. else valid += 1; print a warning for each missing RECOMMENDED field
        raise NotImplementedError("TODO 3")
    print(f"{valid} concepts valid, {errors} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    bundle = Path(sys.argv[1] if len(sys.argv) > 1 else "knowledge")
    raise SystemExit(validate_bundle(bundle))
