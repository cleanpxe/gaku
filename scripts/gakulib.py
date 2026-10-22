"""Shared helpers for gaku's vault scripts. Standard library only (Python 3.11+).

Every script takes the vault root from, in order: a `--vault DIR` argument, the
`GAKU_VAULT` environment variable, or the folder above `scripts/`. Settings come
from `gaku.toml` at the vault root, merged over DEFAULTS below.
"""
import os, re, sys, tomllib
from pathlib import Path

DEFAULTS = {
    "git": {"push": "ask"},
    "vault": {
        # never read
        "hard_skip": [".git", ".obsidian", ".trash", "_trash", "node_modules", ".venv", ".vault-meta"],
        # not linted, and a link only lands here when nothing else matches (raw drops, demo inputs)
        "skip_dirs": ["Inbox"],
        "skip_paths": [],
        "prose_dirs": ["docs/", "Methodology/", ".claude/"],
        "images": "raw_images",
    },
    "lint": {"personal_scan": True, "allow": [], "frontmatter_dirs": ["Courses/"]},
    "heal": {
        "scope": ["Courses", "Projects", "People", "Synthesis", "Sources"],
        "gloss_words": [3, 10],
    },
    "intake": {"from": "~/Downloads", "extensions": ["pdf"], "dpi": 110},
}

# Extensions Obsidian treats as attachments. Anything else after a dot is part of
# the note name (`Reading - 4.3 Torsion`, `Jeff S. Shamma`).
ATTACHMENT_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".avif", ".pdf",
    ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".mp4", ".webm", ".mov", ".mkv",
    ".canvas", ".base", ".csv", ".json", ".txt", ".zip",
}

HEAL_START = "%% claude-heal:start"
HEAL_END = "%% claude-heal:end %%"


def vault_root(argv=None):
    argv = sys.argv if argv is None else argv
    if "--vault" in argv:
        return Path(argv[argv.index("--vault") + 1]).expanduser().resolve()
    if os.environ.get("GAKU_VAULT"):
        return Path(os.environ["GAKU_VAULT"]).expanduser().resolve()
    return Path(__file__).resolve().parent.parent


def load_config(root):
    cfg = {k: dict(v) for k, v in DEFAULTS.items()}
    path = Path(root) / "gaku.toml"
    if path.exists():
        with open(path, "rb") as fh:
            user = tomllib.load(fh)
        for section, values in user.items():
            if isinstance(values, dict):
                cfg.setdefault(section, {}).update(values)
            else:
                cfg[section] = values
    return cfg


# --- files -------------------------------------------------------------------

def is_skipped(rel, cfg):
    parts = rel.split("/")
    return (any(p in cfg["vault"]["skip_dirs"] for p in parts[:-1])
            or rel.startswith(tuple(cfg["vault"]["skip_paths"])))


def walk(root, cfg, suffix=None, include_skipped=False):
    """Yield (relpath, abspath) for every file outside the skip dirs."""
    root = Path(root)
    hard = set(cfg["vault"]["hard_skip"])
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(d for d in dns if d not in hard)
        for fn in sorted(fns):
            if suffix and not fn.endswith(suffix):
                continue
            ap = Path(dp) / fn
            rel = ap.relative_to(root).as_posix()
            if include_skipped or not is_skipped(rel, cfg):
                yield rel, ap


def read(path):
    return Path(path).read_text(encoding="utf-8")


# --- frontmatter -------------------------------------------------------------

FM = re.compile(r"\A---\n(.*?)\n---[ \t]*(?:\n|\Z)", re.S)


def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        return [_scalar(x) for x in v[1:-1].split(",") if x.strip()]
    return v


def frontmatter(text):
    """Parse the flat YAML subset gaku uses: scalars, inline lists, `- item` lists."""
    m = FM.match(text)
    if not m:
        return {}
    data, key = {}, None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s+(.*)$", line) or re.match(r"^-\s+(.*)$", line)
        if item and key is not None:
            if not isinstance(data.get(key), list):
                data[key] = []
            data[key].append(_scalar(item.group(1)))
            continue
        kv = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if kv:
            key = kv.group(1)
            data[key] = _scalar(kv.group(2)) if kv.group(2).strip() else []
    return data


def body_offset(text):
    m = FM.match(text)
    return m.end() if m else 0


# --- links -------------------------------------------------------------------

FENCE = re.compile(r"^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*$", re.S | re.M)
# An inline code span never crosses a blank line, so a stray backtick can't swallow a paragraph.
INLINE_CODE = re.compile(r"(`+)(?!`)((?:(?!\n[ \t]*\n).)+?)(?<!`)\1(?!`)", re.S)
LINK = re.compile(r"(!?)\[\[([^\[\]\n]+?)\]\]")


def strip_code(text):
    """Blank out fenced blocks and inline code, keeping line numbers intact."""
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))
    return INLINE_CODE.sub(blank, FENCE.sub(blank, text))


def links(text):
    """Yield (line_no, is_embed, target) for each wikilink outside code."""
    clean = strip_code(text)
    for m in LINK.finditer(clean):
        target = target_of(m.group(2))
        if not target:
            continue  # [[#Heading]] — a link inside the same note
        yield clean.count("\n", 0, m.start()) + 1, m.group(1) == "!", target


def target_of(inner):
    """The note or file a link's inner text points at: `Note#Heading|alias` -> `Note`."""
    target = re.split(r"\\?\|", inner, maxsplit=1)[0]  # `\|` = escaped pipe in a table
    return target.split("#", 1)[0].split("^", 1)[0].strip().rstrip("\\").strip()


def is_placeholder(target):
    return bool(re.search(r"<[^>]*>|\{\{|<%|⬜", target))


def is_attachment(target):
    return Path(target).suffix.lower() in ATTACHMENT_EXT


# --- note index --------------------------------------------------------------

class Index:
    """Resolves wikilink targets the way Obsidian does: by name, alias, or path suffix."""

    def __init__(self, root, cfg):
        self.root = Path(root)
        self.notes = {}         # relpath -> frontmatter, for notes outside the skip dirs
        self.secondary = set()  # relpaths inside skip dirs/paths
        self.by_name = {}       # casefolded stem or alias -> set(relpath)
        self.by_suffix = {}     # casefolded "dir/stem" path suffix -> set(relpath)
        self.files = {}         # casefolded attachment basename or path suffix -> set(relpath)
        for rel, ap in walk(root, cfg, include_skipped=True):
            if is_skipped(rel, cfg):
                self.secondary.add(rel)
            if rel.endswith(".md"):
                text = read(ap)
                fm = frontmatter(text)
                if rel not in self.secondary:
                    self.notes[rel] = fm
                stem = rel[:-3]
                self._add(self.by_name, Path(stem).name, rel)
                aliases = fm.get("aliases") or []
                for a in aliases if isinstance(aliases, list) else [aliases]:
                    if a:
                        self._add(self.by_name, a, rel)
                parts = stem.split("/")
                for i in range(len(parts) - 1):
                    self._add(self.by_suffix, "/".join(parts[i:]), rel)
            else:
                parts = rel.split("/")
                for i in range(len(parts)):
                    self._add(self.files, "/".join(parts[i:]), rel)

    @staticmethod
    def _add(table, key, rel):
        table.setdefault(key.casefold(), set()).add(rel)

    def resolve(self, target):
        """Return the set of files a target could mean (empty = dead link)."""
        t = target.strip()
        if is_attachment(t):
            hits = self.files.get(t.casefold(), set())
        else:
            if t.lower().endswith(".md"):
                t = t[:-3]
            table = self.by_suffix if "/" in t else self.by_name
            hits = table.get(t.strip("/").casefold(), set())
        return (hits - self.secondary) or hits

    def duplicates(self):
        stems = {}
        for rel in self.notes:
            stems.setdefault(Path(rel[:-3]).name.casefold(), []).append(rel)
        return {k: sorted(v) for k, v in stems.items() if len(v) > 1}


# --- heal blocks -------------------------------------------------------------

def heal_markers(text):
    """Return (starts, ends, unanchored) line numbers for heal-block markers outside code."""
    clean = strip_code(text)
    starts, ends, loose = [], [], []
    for i, line in enumerate(clean.splitlines(), 1):
        if line.startswith(HEAL_START):
            starts.append(i)
        elif line.startswith(HEAL_END):
            ends.append(i)
        elif HEAL_START in line or HEAL_END in line:
            loose.append(i)
    return starts, ends, loose


def split_heal(text):
    """Split a note into (body, block, tail). block is '' when the note has none."""
    # search the code-blanked copy (same offsets) so a block quoted in a fence never matches
    m = re.search(r"^%% claude-heal:start.*?^%% claude-heal:end %%[ \t]*\n?", strip_code(text), re.S | re.M)
    if not m:
        return text, "", ""
    return text[: m.start()], m.group(0), text[m.end():]
