#!/usr/bin/env python3
"""Site checks for nej.dev (Python 3 standard library only).

    python3 scripts/check_site.py          check everything, change nothing
    python3 scripts/check_site.py --fix    also rewrite the English fallback text
                                           in index.html from locales/en.json

Why this exists: the text inside every [data-i18n] element of index.html is the
*fallback* that search engines, link previews and visitors without JavaScript
see. It has to match locales/en.json, and this script keeps the two in sync.
It also catches the mistakes that break a static site silently: a missing
locale key, a broken asset path, a dead #anchor, an unbalanced tag.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from textwrap import TextWrapper

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
LOCALES = ROOT / "locales"
FALLBACK_LANG = "en"  # language of the text written inside index.html

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}
BREAKS = {"li", "br", "p", "ul", "div"}  # count as a space when comparing text
INLINE = {"span", "a", "i", "b", "em", "strong", "small"}


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def flatten(d, prefix=""):
    out = {}
    for key, value in d.items():
        full = f"{prefix}.{key}" if prefix else key
        out.update(flatten(value, full) if isinstance(value, dict) else {full: value})
    return out


class Plain(HTMLParser):
    """Turns an HTML fragment into comparable plain text."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.buf, self.stack, self.errors = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag in BREAKS:
            self.buf.append(" ")
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag in BREAKS:
            self.buf.append(" ")
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append(f"unexpected </{tag}>")

    def handle_data(self, data):
        self.buf.append(data)


def plain(fragment):
    p = Plain()
    p.feed(fragment)
    p.close()
    errors = p.errors + [f"unclosed <{t}>" for t in p.stack]
    return norm("".join(p.buf)), errors


class Page(HTMLParser):
    """Parses index.html and records every [data-i18n] element with its position."""

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.line_starts = [0]
        for line in text.split("\n"):
            self.line_starts.append(self.line_starts[-1] + len(line) + 1)
        self.stack, self.items, self.open_items = [], [], []
        self.errors, self.ids, self.refs = [], set(), []
        self.html_lang = None

    def here(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "html":
            self.html_lang = a.get("lang")
        if tag == "link" and a.get("href"):
            self.refs.append((tag, a["href"], self.getpos()[0]))
        elif tag in ("script", "img", "source") and a.get("src"):
            self.refs.append((tag, a["src"], self.getpos()[0]))
        elif tag == "a" and a.get("href"):
            self.refs.append((tag, a["href"], self.getpos()[0]))
        if tag in BREAKS:
            for it in self.open_items:
                it["buf"].append(" ")
        if tag in VOID:
            return
        self.stack.append(tag)
        if "data-i18n" in a:
            tag_start = self.here()
            item = {"key": a["data-i18n"], "tag": tag, "depth": len(self.stack),
                    "tag_start": tag_start,
                    "start": tag_start + len(self.get_starttag_text()),
                    "end": None, "buf": [], "line": self.getpos()[0]}
            self.items.append(item)
            self.open_items.append(item)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag not in self.stack:
            self.errors.append(f"line {self.getpos()[0]}: stray </{tag}>")
            return
        if self.stack[-1] != tag:
            self.errors.append(f"line {self.getpos()[0]}: </{tag}> closes <{self.stack[-1]}> first")
            while self.stack[-1] != tag:
                self.stack.pop()
        depth = len(self.stack)
        for it in [i for i in self.open_items if i["depth"] == depth]:
            it["end"] = self.here()
            self.open_items.remove(it)
        if tag in BREAKS:
            for it in self.open_items:
                it["buf"].append(" ")
        self.stack.pop()

    def handle_data(self, data):
        for it in self.open_items:
            it["buf"].append(data)


def wrap(s, first, rest, width=108):
    """Word-wrap HTML text without ever breaking inside a tag."""
    hidden = re.sub(r"<[^>]*>", lambda m: m.group(0).replace(" ", "\x00"), s)
    w = TextWrapper(width=width, initial_indent=first, subsequent_indent=rest,
                    break_long_words=False, break_on_hyphens=False)
    return w.fill(hidden).replace("\x00", " ")


def render_inner(text, item, value):
    """Format a locale value as the inner HTML of its element."""
    line_start = text.rfind("\n", 0, item["tag_start"]) + 1
    indent = re.match(r"[ \t]*", text[line_start:]).group(0)
    if "<li>" in value:
        lis = re.findall(r"<li>.*?</li>", value, flags=re.S)
        body = "\n".join(wrap(li, indent + "    ", indent + "        ") for li in lis)
        return "\n" + body + "\n" + indent
    if len(value) <= 60:
        return value
    if item["tag"] in INLINE:
        return wrap(value, "", indent + "    ")
    return "\n" + wrap(value, indent + "    ", indent + "    ") + "\n" + indent


def main():
    fix = "--fix" in sys.argv[1:]
    errors, warnings = [], []

    # --- locale files -------------------------------------------------------
    locales = {}
    for path in sorted(LOCALES.glob("*.json")):
        try:
            locales[path.stem] = flatten(json.loads(path.read_text(encoding="utf-8")))
        except ValueError as exc:
            errors.append(f"{path.name} is not valid JSON: {exc}")
    if FALLBACK_LANG not in locales:
        print(f"FAIL: locales/{FALLBACK_LANG}.json is missing or invalid")
        return 1
    reference = locales[FALLBACK_LANG]
    for lang, table in locales.items():
        for key in sorted(set(reference) - set(table)):
            errors.append(f"locales/{lang}.json is missing key: {key}")
        for key in sorted(set(table) - set(reference)):
            errors.append(f"locales/{lang}.json has an extra key: {key}")
        for key, value in table.items():
            if not isinstance(value, str) or not value.strip():
                errors.append(f"locales/{lang}.json: empty or non-text value for {key}")
                continue
            _, problems = plain(value)
            errors += [f"locales/{lang}.json {key}: {p}" for p in problems]

    # --- index.html ---------------------------------------------------------
    text = INDEX.read_bytes().decode("utf-8")
    page = Page(text)
    page.feed(text)
    page.close()
    errors += page.errors
    errors += [f"index.html: unclosed <{t}>" for t in page.stack]

    used = {it["key"] for it in page.items}
    for key in sorted(used - set(reference)):
        errors.append(f"index.html uses key that is not in the locale files: {key}")
    for key in sorted(set(reference) - used):
        warnings.append(f"locale key is never used in index.html: {key}")

    drift = []
    for it in page.items:
        if it["key"] not in reference or it["end"] is None:
            continue
        have = norm("".join(it["buf"]))
        want, _ = plain(reference[it["key"]])
        if have != want:
            drift.append((it, want))

    if fix and drift:
        newline = "\r\n" if "\r\n" in text else "\n"
        for it, _ in sorted(drift, key=lambda d: d[0]["start"], reverse=True):
            inner = render_inner(text, it, reference[it["key"]]).replace("\n", newline)
            text = text[:it["start"]] + inner + text[it["end"]:]
        INDEX.write_bytes(text.encode("utf-8"))
        print(f"fixed: rewrote {len(drift)} fallback element(s) in index.html from locales/{FALLBACK_LANG}.json")
        return main_recheck()
    for it, want in drift:
        errors.append(f"index.html line {it['line']} ({it['key']}): fallback text differs from "
                      f"locales/{FALLBACK_LANG}.json  -> run with --fix")

    # --- links, assets, anchors ----------------------------------------------
    for tag, ref, line in page.refs:
        if re.match(r"^(https?:|//|mailto:|tel:|data:|javascript:)", ref) or ref == "#":
            continue
        if ref.startswith("#"):
            if ref[1:] not in page.ids:
                errors.append(f"index.html line {line}: anchor {ref} has no element with that id")
            continue
        target = ROOT / ref.split("?")[0].split("#")[0].lstrip("/")
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            errors.append(f"index.html line {line}: <{tag}> points to a missing file: {ref}")

    # --- default language must agree with <html lang> -------------------------
    js_files = [p for p in ROOT.rglob("*.js") if "arcade" not in p.parts and ".git" not in p.parts]
    default = None
    for js in js_files:
        m = re.search(r"DEFAULT_LANG\s*=\s*['\"](\w+)['\"]", js.read_text(encoding="utf-8"))
        if m:
            default = m.group(1)
    if default is None:
        warnings.append("could not find DEFAULT_LANG in any script")
    else:
        if default != FALLBACK_LANG:
            errors.append(f"DEFAULT_LANG is '{default}' but the fallback text is '{FALLBACK_LANG}' "
                          "(visitors would see the language flip on load)")
        if page.html_lang != default:
            errors.append(f"<html lang=\"{page.html_lang}\"> does not match DEFAULT_LANG '{default}'")

    # --- report -----------------------------------------------------------------
    print(f"checked {len(page.items)} data-i18n elements, "
          f"{len(reference)} keys x {len(locales)} languages ({', '.join(sorted(locales))})")
    for w in warnings:
        print("warning:", w)
    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print(" -", e)
        return 1
    print("OK: nothing is out of sync or broken")
    return 0


def main_recheck():
    # Re-run the checks after --fix has rewritten the file.
    sys.argv = [a for a in sys.argv if a != "--fix"]
    return main()


if __name__ == "__main__":
    sys.exit(main())
