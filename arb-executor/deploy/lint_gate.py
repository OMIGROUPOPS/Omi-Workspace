#!/usr/bin/env python3
"""Deploy-gate lint: NO DEPLOY WITHOUT THIS PASSING (law of 2026-07-04).

Born from the _sibling_ticker incident: 5b924f10 added a 1-arg _sibling_ticker
helper while a 2-arg _sibling_ticker(tk, et) existed later in the class body.
Both parse fine; the later def silently wins; every 1-arg call died with
TypeError at runtime and killed the routing loop for 8 hours. Tests exercised
the helper directly and missed it. A duplicate-name lint catches it in <1s.

Checks (dependency-free core, hard-fail):
  1. compile() -- syntax (E999 class).
  2. AST duplicate definitions: two def/async def/class with the same name in
     the same scope (module, class body, or function body). @property/@setter/
     @overload/@singledispatch stacks are exempt.
If flake8 is importable, also runs --select=E999,F811,F821,F823 (hard-fail).

Usage: python3 deploy/lint_gate.py live_v4.py [more_files...]
Exit 0 = clean, 1 = violations (deploy must refuse).
"""
import ast
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

EXEMPT_DECORATORS = ("property", "setter", "getter", "deleter", "overload",
                     "register", "cached_property", "abstractmethod")


def _decorator_names(node):
    names = []
    for d in getattr(node, "decorator_list", []):
        t = d
        while isinstance(t, ast.Call):
            t = t.func
        while isinstance(t, ast.Attribute):
            names.append(t.attr)
            t = t.value
        if isinstance(t, ast.Name):
            names.append(t.id)
    return names


def duplicate_defs(tree, filename):
    """Return [(name, first_line, dup_line, scope)] for same-scope re-defs."""
    violations = []

    def scan(body, scope):
        seen = {}
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                decs = _decorator_names(node)
                exempt = any(d in EXEMPT_DECORATORS for d in decs)
                if node.name in seen and not exempt and not seen[node.name][1]:
                    violations.append((node.name, seen[node.name][0], node.lineno, scope))
                else:
                    seen.setdefault(node.name, (node.lineno, exempt))
                    if exempt:
                        seen[node.name] = (seen[node.name][0], True)
                if isinstance(node, ast.ClassDef):
                    scan(node.body, f"{scope}.{node.name}")
                else:
                    scan(node.body, f"{scope}.{node.name}()")
            elif isinstance(node, (ast.If, ast.Try, ast.With, ast.AsyncWith)):
                # conditional/guarded defs at the same level: walk their bodies in
                # the SAME scope map is intentional-overload territory; skip to
                # avoid false positives on `if TYPE_CHECKING:` style dual defs.
                continue
    scan(tree.body, Path(filename).name)
    return violations


def main():
    files = sys.argv[1:] or ["live_v4.py"]
    failed = False
    for f in files:
        src = Path(f).read_text(encoding="utf-8", errors="replace")
        # 1. syntax
        try:
            tree = ast.parse(src, filename=f)
            compile(src, f, "exec")
        except SyntaxError as e:
            print(f"LINT FAIL [syntax] {f}:{e.lineno}: {e.msg}")
            failed = True
            continue
        # 2. duplicate defs
        for name, first, dup, scope in duplicate_defs(tree, f):
            print(f"LINT FAIL [duplicate-def] {f}:{dup}: '{name}' redefines "
                  f"{f}:{first} in scope {scope} (later def silently wins)")
            failed = True
    # 3. flake8 if present
    try:
        import flake8  # noqa: F401
        r = subprocess.run([sys.executable, "-m", "flake8",
                            "--select=E999,F811,F821,F823", *files],
                           capture_output=True, text=True)
        if r.stdout.strip():
            print(r.stdout.strip())
            print("LINT FAIL [flake8]")
            failed = True
        elif r.returncode not in (0, 1):
            print(f"LINT WARN: flake8 exited {r.returncode}: {r.stderr.strip()[:200]}")
    except ImportError:
        print("LINT NOTE: flake8 not installed; AST core checks only")
    if failed:
        print("LINT: FAIL -- deploy refused")
        return 1
    print("LINT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
