"""Record which version of each English source the Spanish translations follow.

Run after translating or re-translating (python3 i18n/es/stamp.py [path ...]): it
writes i18n/es/SOURCES.json, the sha256 of each English source a translation
exists for. With paths, only those are stamped (an English path: docs/x.md or a
repository document like spec/format.md). The site build compares these hashes
with the English files and marks a Spanish page whose original changed since.
"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "SOURCES.json")


def sha(p):
    with open(os.path.join(ROOT, p), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def translated():
    """English source path -> Spanish file path, for every translation present."""
    out = {}
    for base, _, names in os.walk(os.path.join(ROOT, "docs-es")):
        for n in names:
            if n.endswith(".md"):
                es = os.path.relpath(os.path.join(base, n), ROOT)
                out["docs/" + os.path.relpath(es, "docs-es")] = es
    for base, _, names in os.walk(HERE):
        for n in names:
            if n.endswith(".md") and n != "GLOSARIO.md":
                es = os.path.relpath(os.path.join(base, n), ROOT)
                out[os.path.relpath(es, "i18n/es")] = es
    return {en: es for en, es in out.items() if os.path.exists(os.path.join(ROOT, en))}


if __name__ == "__main__":
    stamps = json.load(open(OUT)) if os.path.exists(OUT) else {}
    want = sys.argv[1:] or sorted(translated())
    for en in want:
        stamps[en] = sha(en)
    with open(OUT, "w") as fh:
        json.dump(dict(sorted(stamps.items())), fh, indent=2)
        fh.write("\n")
    print(f"stamped {len(want)} translation(s)")
