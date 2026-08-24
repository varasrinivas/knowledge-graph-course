"""gen_java_repo — deterministic synthetic Java codebase generator.

Creates a Java repo with a KNOWN structure so extraction and measurement are
exactly verifiable offline. Seeded PRNG -> identical output every run.

Layout: P packages x C classes; each class has methods that call
  - the shared hub  core.Registry.lookup   (the deliberate god node)
  - its package service  <pkg>.Service<p>.process
  - one cross-package neighbor
Every package ships one Handler interface implemented by its classes.
A ground-truth manifest (known_truth.json) records the seeded facts.

Usage:
    python gen_java_repo.py <out_dir> [--files 1500]
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

CLASS_TMPL = """package {pkg};

public class {cls} implements Handler{p} {{

    private final int weight = {weight};

    public String handle(String input) {{
        Object ref = Registry.lookup("{pkg}.{cls}");
        return Service{p}.process(input) + ref.toString();
    }}

    public int compute{cls}(int value) {{
        if (value < 0) {{
            throw new IllegalArgumentException("negative value");
        }}
        return helper{cls}(value) + weight;
    }}

    private int helper{cls}(int value) {{
        {neighbor_call}
        return value * 2;
    }}
}}
"""

SERVICE_TMPL = """package {pkg};

public final class Service{p} {{
    private Service{p}() {{}}

    public static String process(String input) {{
        if (input == null) {{
            return "";
        }}
        return input.trim().toLowerCase();
    }}
}}
"""

IFACE_TMPL = """package {pkg};

public interface Handler{p} {{
    String handle(String input);
}}
"""

REGISTRY = """package core;

import java.util.HashMap;
import java.util.Map;

public final class Registry {
    private static final Map<String, Object> ENTRIES = new HashMap<>();

    private Registry() {}

    public static Object lookup(String key) {
        Object value = ENTRIES.get(key);
        if (value == null) {
            throw new IllegalStateException("unknown key: " + key);
        }
        return value;
    }

    public static void register(String key, Object value) {
        ENTRIES.put(key, value);
    }
}
"""


def generate(out: Path, target_files: int) -> dict:
    rng = random.Random(42)
    # files = P*(C + 2) + 1(Registry)  ->  choose P, C to hit the target
    classes_per_pkg = 8
    packages = max(1, (target_files - 1) // (classes_per_pkg + 2))

    (out / "src/core").mkdir(parents=True, exist_ok=True)
    (out / "src/core/Registry.java").write_text(REGISTRY, encoding="utf-8")

    truth = {"god_node": "Registry.lookup", "packages": packages,
             "classes_per_pkg": classes_per_pkg,
             "lookup_callers": 0, "process_callers": {}, "sample_edges": []}

    for p in range(packages):
        pkg = f"pkg{p:03d}"
        d = out / "src" / pkg
        d.mkdir(parents=True, exist_ok=True)
        (d / f"Handler{p}.java").write_text(
            IFACE_TMPL.format(pkg=pkg, p=p), encoding="utf-8")
        (d / f"Service{p}.java").write_text(
            SERVICE_TMPL.format(pkg=pkg, p=p), encoding="utf-8")
        for c in range(classes_per_pkg):
            cls = f"Widget{p:03d}x{c}"
            neighbor_p = rng.randrange(packages)
            neighbor_c = rng.randrange(classes_per_pkg)
            neighbor = f"Widget{neighbor_p:03d}x{neighbor_c}"
            neighbor_call = (f"int unused = new {neighbor}().compute{neighbor}(value);"
                             if neighbor != cls else "// self neighbor skipped")
            (d / f"{cls}.java").write_text(
                CLASS_TMPL.format(pkg=pkg, cls=cls, p=p, weight=rng.randrange(1, 100),
                                  neighbor_call=neighbor_call),
                encoding="utf-8")
            truth["lookup_callers"] += 1  # every handle() calls Registry.lookup
            if len(truth["sample_edges"]) < 5:
                truth["sample_edges"].append(
                    {"caller": f"{cls}.handle", "callee": "Registry.lookup"})
        truth["process_callers"][f"Service{p}.process"] = classes_per_pkg

    n_files = sum(1 for _ in out.rglob("*.java"))
    truth["java_files"] = n_files
    (out / "known_truth.json").write_text(json.dumps(truth, indent=2), encoding="utf-8")
    return truth


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    out = Path(sys.argv[1]).resolve()
    target = int(sys.argv[sys.argv.index("--files") + 1]) if "--files" in sys.argv else 1500
    truth = generate(out, target)
    print(f"Generated {truth['java_files']} Java files in {out}")
    print(f"  packages={truth['packages']} classes/pkg={truth['classes_per_pkg']}")
    print(f"  god node Registry.lookup has {truth['lookup_callers']} seeded callers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
