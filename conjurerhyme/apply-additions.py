#!/usr/bin/env python3
"""Merge `conjurerhyme/additions.dict` into `cmudict.dict`.

The dictionary is 3.6 MB of one-entry-per-line text, so the additions are kept as
data and applied by this script rather than hand-edited. That makes re-applying
them over a new upstream release mechanical:

    git fetch upstream
    git checkout upstream/master -- cmudict.dict
    python3 conjurerhyme/apply-additions.py
    git commit -am "Re-apply ConjureRhyme additions over upstream <rev>"

**Where an entry goes.** Upstream's file is not in any single machine sort order
(punctuation and the `(N)` variant suffix both break a plain byte sort), so this
script does not try to re-sort anything. It uses upstream's own local rule: a
variant sits immediately after the last existing pronunciation of its base word,
which is exactly where `transfer(2)` and `transports(2)` sit. Every other byte of
the file is untouched.

Applying twice is a no-op, and an addition whose text no longer matches what is
already in the file is an error rather than a silent overwrite — an upstream that
has added the entry itself should retire our copy, not fight it.

`--check` applies nothing and exits non-zero if the file is not up to date; that
is the mode for CI and for the vendoring script downstream.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DICT = HERE.parent / "cmudict.dict"
ADDITIONS = HERE / "additions.dict"

_VARIANT = re.compile(r"\(\d+\)$")


def head_word(line: str) -> str:
    """The head word of an entry line, variant suffix and all."""
    return line.split(maxsplit=1)[0]


def base_word(head: str) -> str:
    """`transplant(2)` -> `transplant`."""
    return _VARIANT.sub("", head)


def entries(text: str) -> list[str]:
    """Addition lines, with full-line comments and blank lines dropped."""
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def apply(lines: list[str], addition: str) -> tuple[list[str], bool]:
    """Return the file with `addition` present, and whether anything changed."""
    head = head_word(addition)
    base = base_word(head)

    last = None
    for i, line in enumerate(lines):
        existing = head_word(line)
        if existing == head:
            if line != addition:
                raise SystemExit(
                    f"{head}: already present with different phones.\n"
                    f"  in cmudict.dict:  {line}\n"
                    f"  in additions:     {addition}\n"
                    "Upstream may have added this entry. Reconcile by hand, then "
                    "drop it from additions.dict if upstream's version wins."
                )
            return lines, False  # already applied
        if base_word(existing) == base:
            last = i

    if last is None:
        raise SystemExit(
            f"{head}: base word {base!r} is not in cmudict.dict. This file adds "
            "pronunciations to existing words, not new vocabulary."
        )
    return lines[: last + 1] + [addition] + lines[last + 1 :], True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if cmudict.dict is missing any addition; write nothing",
    )
    args = parser.parse_args()

    original = DICT.read_text(encoding="utf-8")
    lines = original.splitlines()
    additions = entries(ADDITIONS.read_text(encoding="utf-8"))
    if not additions:
        raise SystemExit(f"{ADDITIONS.name} holds no entries")

    missing = []
    for addition in additions:
        lines, changed = apply(lines, addition)
        if changed:
            missing.append(head_word(addition))

    if args.check:
        if missing:
            print(f"cmudict.dict is missing {len(missing)}: {', '.join(missing)}")
            return 1
        print(f"cmudict.dict carries all {len(additions)} additions")
        return 0

    if not missing:
        print(f"cmudict.dict already carries all {len(additions)} additions; unchanged")
        return 0

    # The file ends in a newline and every line is plain ASCII with a \n terminator;
    # rebuilding it this way keeps that true and leaves untouched lines byte-identical.
    DICT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"added {len(missing)}: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
