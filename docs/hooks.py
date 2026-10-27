"""MkDocs hooks: the site is built from the repository, not a copy of it.

- The repository's own documents (spec/, sandboxes/, corpus/, results/versions.md,
  contracts/CHANGES.md, runner/README.md) are added to the site as they are, so
  there is one source for each. Their relative links are rewritten: to the site
  page when the target is on the site, otherwise to the file on GitHub.
- Two pages are generated from the data: results/index.md (every published run)
  and contracts/index.md (the catalog of the current corpus).
- In the hand-written pages under docs/, a link `repo:path` points to that file on
  GitHub.
- The same hooks build the Spanish site (mkdocs.es.yml, theme language "es"): its
  hand-written pages are in docs-es/ at the same paths, the repository documents are
  translated in i18n/es/ at their repository paths, and the generated pages are
  written in Spanish. The build fails when an English page or document has no
  translation, so the two sites cannot drift apart unnoticed. Two logs that change
  with every corpus version and every run (ENGLISH_ONLY) stay in English.
"""
import glob, hashlib, json, os, posixpath, re, sys, tomllib

from mkdocs.exceptions import PluginError
from mkdocs.structure.files import File

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GITHUB = "https://github.com/carlostapiacl/sandbox-conformance"
sys.path.insert(0, os.path.join(ROOT, "runner"))
import corpus  # noqa: E402

# site path -> repository path
COPIED = {
    "reference/format.md": "spec/format.md",
    "reference/verdicts.md": "spec/verdicts.md",
    "reference/corpus.md": "corpus/README.md",
    "reference/runner.md": "runner/README.md",
    "changelog/contracts.md": "contracts/CHANGES.md",
    "results/versions.md": "results/versions.md",
    "sandboxes/index.md": "sandboxes/README.md",
}
for f in sorted(glob.glob(os.path.join(ROOT, "sandboxes", "*.md"))):
    name = os.path.basename(f)
    if name != "README.md":
        COPIED[f"sandboxes/{name}"] = f"sandboxes/{name}"
SITE_OF = {repo: site for site, repo in COPIED.items()}
LINK = re.compile(r"(\]\()([^)\s]+)(\))")
RESULTS_ORDER = ["contained", "escaped", "control-broke", "unsupported", "vacuous"]
ENGLISH_ONLY = {"contracts/CHANGES.md", "results/versions.md"}
LANG = "en"


def on_config(config):
    global LANG
    LANG = config.theme.get("language") or "en"
    if LANG == "es":
        missing = [f"docs-es/{p}" for p in hand_written() if not os.path.exists(os.path.join(ROOT, "docs-es", p))]
        missing += [f"i18n/es/{r}" for r in COPIED.values()
                    if r not in ENGLISH_ONLY and not os.path.exists(os.path.join(ROOT, "i18n", "es", r))]
        if missing:
            raise PluginError("the Spanish site lacks a translation of: " + ", ".join(sorted(missing)))
    return config


def hand_written():
    base = os.path.join(ROOT, "docs")
    return sorted(os.path.relpath(p, base) for p in glob.glob(os.path.join(base, "**", "*.md"), recursive=True))


def source_of(repo):
    """The repository document a page is built from, in the site's language."""
    if LANG == "es" and repo not in ENGLISH_ONLY:
        return os.path.join(ROOT, "i18n", "es", repo)
    return os.path.join(ROOT, repo)


def github(repo_path):
    full = os.path.join(ROOT, repo_path)
    kind = "tree" if os.path.isdir(full) else "blob"
    return f"{GITHUB}/{kind}/main/{repo_path}".rstrip("/")


def rewrite(markdown, site_path, repo_path):
    def fix(m):
        target = m.group(2)
        if target.startswith("repo:"):
            return m.group(1) + github(target[5:]) + m.group(3)
        if repo_path is None or re.match(r"^[a-z]+:|^#|^/", target):
            return m.group(0)
        path, _, frag = target.partition("#")
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(repo_path), path)) if path else repo_path
        if resolved in SITE_OF:
            rel = posixpath.relpath(SITE_OF[resolved], posixpath.dirname(site_path))
            return m.group(1) + rel + (f"#{frag}" if frag else "") + m.group(3)
        if resolved.startswith(".."):
            return m.group(0)
        return m.group(1) + github(resolved) + (f"#{frag}" if frag else "") + m.group(3)
    return LINK.sub(fix, markdown)


def version_of(d):
    m = re.search(r"\d+\.\d+[0-9A-Za-z.\-]*", d.get("version", ""))
    return m.group(0) if m else d.get("version", "")


def results_page():
    rows = []
    for f in glob.glob(os.path.join(ROOT, "results", "*", "*.json")):
        try:
            d = json.load(open(f))
        except ValueError:
            continue
        if not isinstance(d, dict) or "contracts" not in d or "sandbox" not in d:
            continue
        run = os.path.basename(os.path.dirname(f))
        c = d.get("corpus") or corpus.corpus_of(d)
        if c:
            cv = f"v{c['version']}" + ("" if c["whole"] else f" ({c['ran']} of {c['of']})")
        else:
            cv = "pre-1.0"
        if c and not c["whole"] and LANG == "es":
            cv = f"v{c['version']} ({c['ran']} de {c['of']})"
        h = d.get("host") or {}
        osm = re.match(r"(\S+ \d+\.\d+)", h.get("os", ""))
        kern = re.match(r"\d+\.\d+\.\d+", h.get("kernel", ""))
        host = ", ".join(x.group(0) for x in (osm, kern) if x) or ("(ver el run)" if LANG == "es" else "(see run)")
        counts = d.get("counts", {})
        other = sum(v for k, v in counts.items() if k not in RESULTS_ORDER)
        rows.append({
            "run": run, "date": (d.get("run_at") or run)[:10], "sandbox": d["sandbox"], "version": version_of(d),
            "host": host, "profile": d.get("profile", "strict"), "corpus": cv,
            "verdicts": (d.get("spec_version") or "v0").replace(".0-draft", "-draft"), "counts": counts, "other": other,
        })
    rows.sort(key=lambda r: (r["date"], r["run"], r["sandbox"]), reverse=True)
    if LANG == "es":
        L = ["---", "hide:", "  - toc", "---", "", "# Todos los runs", "",
             "Cada run publicado, del más nuevo al más antiguo. Cada fila es una versión de un sandbox, en un host,",
             "bajo un profile, medida contra una [versión del corpus](../concepts/corpus-versions.md) y juzgada con",
             "una versión de los [verdicts](../reference/verdicts.md). Cómo se pueden comparar las filas está en la",
             "[metodología](../methodology.md#comparing-runs).", "",
             "Los conteos son por [result](../concepts/results.md); *otros* son `needs-feature`,",
             "`not-applicable` y las fallas del lab. La carpeta de cada run tiene su README, la tabla de",
             "comparación y la evidencia de cada caso: la fecha enlaza a ella.", "",
             "| run | sandbox | versión | host | corpus | verdicts | contained | escaped | control-broke | unsupported | vacuous | otros |",
             "|---|---|---|---|---|---|--:|--:|--:|--:|--:|--:|"]
    else:
        L = ["---", "hide:", "  - toc", "---", "", "# All runs", "",
             "Every published run, newest first. Each row is one sandbox version, on one host, under one",
             "profile, measured against one [corpus version](../concepts/corpus-versions.md) and judged under",
             "one version of the [verdicts](../reference/verdicts.md). How rows can be compared is in the",
             "[methodology](../methodology.md#comparing-runs).", "",
             "The counts are per [result](../concepts/results.md); *other* is `needs-feature`,",
             "`not-applicable` and the lab faults. Each run's folder has its README, the comparison table",
             "and the raw evidence of every case: the date links to it.", "",
             "| run | sandbox | version | host | corpus | verdicts | contained | escaped | control-broke | unsupported | vacuous | other |",
             "|---|---|---|---|---|---|--:|--:|--:|--:|--:|--:|"]
    for r in rows:
        cells = [str(r["counts"].get(k, 0)) for k in RESULTS_ORDER]
        L.append(f"| [{r['date']}]({github('results/' + r['run'])}) | {r['sandbox']} | {r['version']} | {r['host']} | "
                 f"{r['corpus']} | {r['verdicts']} | " + " | ".join(cells) + f" | {r['other']} |")
    if LANG == "es":
        L += ["", "*pre-1.0*: el run corrió contracts que cambiaron antes de que el corpus tuviera versiones. Sus",
              "resultados quedan como se publicaron, y [Qué cambió por versión](versions.md) compara los runs en",
              "los contracts que comparten sin cambios."]
    else:
        L += ["", "*pre-1.0*: the run ran contracts that changed before the corpus was versioned. Its results",
              "stand as published, and [What changed by version](versions.md) compares runs on the contracts",
              "they share unchanged."]
    return "\n".join(L) + "\n"


def contracts_page():
    vs = corpus.versions()
    v = vs[-1][0] if vs else "(unversioned)"
    by = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "contracts", "*", "*.toml"))):
        with open(f, "rb") as fh:
            c = tomllib.load(fh)
        by.setdefault(c.get("category", "?"), []).append((c, os.path.relpath(f, ROOT)))
    total = sum(len(x) for x in by.values())
    if LANG == "es":
        L = ["# Catálogo de contracts", "",
             f"Corpus **v{v}**: {total} contracts en {len(by)} categorías. Cada uno nombra el test público que",
             "re-expresa (`source`). El formato está en la [referencia](../reference/format.md).", "",
             "| categoría | contracts |", "|---|---|"]
        head = "| contract | severidad | os | source |"
    else:
        L = ["# Contract catalog", "",
             f"Corpus **v{v}**: {total} contracts in {len(by)} categories. Each one names the public test it",
             "re-expresses (`source`). The format is in the [reference](../reference/format.md).", "",
             "| category | contracts |", "|---|---|"]
        head = "| contract | severity | os | source |"
    L += [f"| [{cat}](#{cat}) | {len(items)} |" for cat, items in sorted(by.items())]
    for cat, items in sorted(by.items()):
        L += ["", f"## {cat}", "", head, "|---|---|---|---|"]
        for c, path in items:
            src = (c.get("source") or "").replace("|", "\\|")
            L.append(f"| [`{c['id']}`]({github(path)}) | {c.get('severity', '')} | {', '.join(c.get('os', []))} | {src} |")
    return "\n".join(L) + "\n"


def on_files(files, config):
    for site, repo in COPIED.items():
        with open(source_of(repo), encoding="utf-8") as fh:
            text = fh.read()
        if LANG == "es" and repo in ENGLISH_ONLY:
            title, _, rest = text.partition("\n")
            text = f"{title}\n\n!!! note \"En inglés\"\n    Este registro cambia con cada versión del corpus y cada run, y se mantiene en inglés.\n{rest}"
        files.append(File.generated(config, site, content=text))
    files.append(File.generated(config, "results/index.md", content=results_page()))
    files.append(File.generated(config, "contracts/index.md", content=contracts_page()))
    return files


def english_source(site):
    """The English file a Spanish page translates (None for a generated page)."""
    if site in COPIED:
        return None if COPIED[site] in ENGLISH_ONLY else COPIED[site]
    return f"docs/{site}" if os.path.exists(os.path.join(ROOT, "docs", site)) else None


def stale_note(site):
    """A Spanish page whose English original changed after it was translated says so."""
    en = english_source(site)
    if en is None:
        return ""
    stamps_file = os.path.join(ROOT, "i18n", "es", "SOURCES.json")
    stamps = json.load(open(stamps_file)) if os.path.exists(stamps_file) else {}
    with open(os.path.join(ROOT, en), "rb") as fh:
        now = hashlib.sha256(fh.read()).hexdigest()
    if stamps.get(en) == now:
        return ""
    url = "https://carlostapiacl.github.io/sandbox-conformance/docs/" + re.sub(r"(index)?\.md$", "", site)
    return (f'!!! warning "Traducción pendiente"\n    El original en inglés cambió después de esta traducción. '
            f"La versión al día está en [inglés]({url}).\n\n")


def on_page_markdown(markdown, page, config, files):
    site = page.file.src_uri
    out = rewrite(markdown, site, COPIED.get(site))
    if LANG == "es":
        note = stale_note(site)
        if note:
            title, _, rest = out.partition("\n")
            out = f"{title}\n\n{note}{rest}" if title.startswith("# ") else note + out
    return out
