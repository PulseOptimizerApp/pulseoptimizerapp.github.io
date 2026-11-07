#!/usr/bin/env python3
"""
Refreshes guide/guide.json, the live data behind the PC guide in the Pulse app.

Runs every night on GitHub Actions (see .github/workflows/refresh-guide.yml). Uses only Python's standard library.

What it updates:
  - Graphics card prices (best US price now, lowest ever) from Tom's Hardware's GPU price tracker.
  - RAM kit prices and the 32 GB DDR5 price history from Capital and Compute's memory tracker.
  - News from the RSS feeds of PC hardware sites (headline, first sentence, link).
  - Spanish and Portuguese for new text, if a GEMINI_API_KEY secret is set (otherwise new text stays in English).

Safety rules: a price is only replaced when it was read cleanly and is believable next to the old one; anything
that can't be read keeps yesterday's value. "Updated" only moves forward when something was actually checked, so the
app's "updated X days ago" stays honest. The result must pass the same checks the app does, or nothing is written.
"""
import datetime as dt
import email.utils
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE = os.path.join(ROOT, "guide", "guide.json")
TODAY = dt.date.today()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36 PulseGuideBot/1.0"

GPU_URL = "https://www.tomshardware.com/pc-components/gpus/lowest-gpu-prices-tracking"
RAM_URL = "https://capitalandcompute.net/memory-prices/"
FEEDS = [
    ("Tom's Hardware", "https://www.tomshardware.com/feeds/all"),
    ("PC Gamer", "https://www.pcgamer.com/rss/"),
    ("TechSpot", "https://www.techspot.com/backend.xml"),
]
LOG = []


def log(msg):
    LOG.append(msg)
    print(msg, flush=True)


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read(5_000_000)
        charset = r.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


# ───────── HTML tables ─────────

class Tables(HTMLParser):
    """Collects every <table> as a list of rows, each a list of cell texts."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self._row, self._cell, self._depth = [], None, None, 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._depth += 1
            self.tables.append([])
        elif tag == "tr" and self._depth:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
        elif tag == "br" and self._cell is not None:
            self._cell.append(" ")

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(re.sub(r"\s+", " ", "".join(self._cell)).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row and self.tables:
                self.tables[-1].append(self._row)
            self._row = None
        elif tag == "table" and self._depth:
            self._depth -= 1

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def tables(page):
    p = Tables()
    p.feed(page)
    return [t for t in p.tables if t]


def dollars(text):
    """All dollar amounts in a cell, as ints: "$1,399" -> [1399]; "$429 to $600" -> [429, 600]."""
    return [int(round(float(m.replace(",", "")))) for m in re.findall(r"\$\s?([\d,]+(?:\.\d+)?)", text or "")]


def norm(name):
    n = name.lower().replace("geforce", "").replace("radeon", "").replace("nvidia", "").replace("amd", "")
    return re.sub(r"[^a-z0-9]", "", n)


# ───────── graphics cards ─────────

def refresh_gpus(g):
    try:
        page = fetch(GPU_URL)
    except Exception as e:
        log(f"GPU prices: couldn't load the tracker ({e}); keeping yesterday's prices.")
        return False
    rows = {}
    for t in tables(page):
        for r in t:
            if len(r) >= 4 and r[0] and dollars(r[1]) and dollars(r[3]):
                rows[norm(r[0])] = r
    if not rows:
        # Some layouts aren't real tables: read "Name $a $b $c" lines from the page text instead.
        text = html.unescape(re.sub(r"<[^>]+>", "\n", page))
        for m in re.finditer(r"\n\s*((?:GeForce|Radeon|Arc)[^\n$]{3,40}?)\s*\n\s*(\$[\d,]+)\s*\n\s*(\$[\d,]+)\s*\n\s*(\$[\d,]+)", text):
            rows[norm(m.group(1))] = [m.group(1), m.group(2), m.group(3), m.group(4)]
    if not rows:
        log("GPU prices: the tracker's layout changed (no price table found); keeping yesterday's prices.")
        return False

    changed = 0
    for card in g["Gpus"]:
        r = rows.get(norm(card["Name"]))
        if not r:
            log(f"GPU prices: {card['Name']} not in the tracker; kept.")
            continue
        now, low, msrp = dollars(r[1]), dollars(r[2]), dollars(r[3])
        if not now:
            continue
        now = now[0]
        low = low[0] if low else card["Lowest"]
        msrp = msrp[0] if msrp else card["Msrp"]
        # Believable? Prices don't triple or crash overnight, and launch prices don't change.
        if not (0.4 * card["Now"] <= now <= 3 * card["Now"]) or abs(msrp - card["Msrp"]) > 0.25 * card["Msrp"]:
            log(f"GPU prices: {card['Name']} read as {now} (launch {msrp}), which looks wrong; kept {card['Now']}.")
            continue
        if low > now:
            low = min(card["Lowest"], now)
        if (card["Now"], card["Lowest"]) != (now, low):
            log(f"GPU prices: {card['Name']} ${card['Now']} -> ${now}")
            card["Now"], card["Lowest"] = now, low
            changed += 1
    g["GpuSource"] = "Tom's Hardware GPU price tracker, " + TODAY.strftime("%B %Y").replace(" 0", " ")
    g["GpuSourceUrl"] = GPU_URL
    log(f"GPU prices: checked {len(g['Gpus'])} cards, {changed} changed.")
    return True


# ───────── RAM ─────────

def kit_key(text):
    """'16GB DDR5 (2x8GB)' or '16 GB DDR5 (2×8)' -> '16ddr5'."""
    m = re.search(r"(\d+)\s*GB\s*(DDR[45])", text, re.I)
    return f"{m.group(1)}{m.group(2).lower()}" if m else None


def refresh_ram(g):
    try:
        page = fetch(RAM_URL)
    except Exception as e:
        log(f"RAM prices: couldn't load the tracker ({e}); keeping yesterday's prices.")
        return False
    found = False
    by_key = {kit_key(k["Kit"]): k for k in g["Ram"]}
    history = {p["Date"]: p for p in g["RamHistory"]}
    for t in tables(page):
        for r in t:
            if len(r) < 2:
                continue
            # Current kit prices: "16GB DDR5 (2x8GB) | $297 | ..."
            k = kit_key(r[0])
            if k in by_key:
                d = dollars(r[1])
                if d:
                    old = dollars(by_key[k]["Now"])
                    if old and not (0.4 * old[0] <= d[0] <= 3 * old[0]):
                        log(f"RAM prices: {r[0]} read as {d}, which looks wrong; kept.")
                        continue
                    by_key[k]["Now"] = f"${d[0]:,}" if len(d) == 1 else f"${d[0]:,} – ${d[1]:,}"
                    found = True
            # 32 GB DDR5 history: "2026-11-03 | $429 | $617"
            m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})", r[0].strip())
            if m and len(r) >= 3:
                a, b = dollars(r[1]), dollars(r[2])
                if a and b and m.group(1) not in history and m.group(1) <= TODAY.isoformat():
                    history[m.group(1)] = {"Date": m.group(1), "Cheapest": a[0], "Average": b[0]}
                    log(f"RAM history: added {m.group(1)} (${a[0]} / ${b[0]})")
                    found = True
    if not found:
        log("RAM prices: no kit prices found (layout changed?); keeping yesterday's prices.")
        return False
    g["RamHistory"] = [history[d] for d in sorted(history)]
    g["RamSource"] = "Capital and Compute RAM tracker, " + TODAY.strftime("%B %-d, %Y")
    g["RamSourceUrl"] = RAM_URL
    return True


# ───────── news ─────────

TAGS = [
    ("RAM", r"\b(ram|ddr[45]|dram|memory prices?|memory shortage|lpddr|hbm)\b"),
    ("Storage", r"\b(ssd|nand|nvme|storage)\b"),
    ("GPU", r"\b(gpu|graphics card|rtx|radeon|geforce|arc b\d|rdna)\b"),
    ("CPU", r"\b(cpu|ryzen|core ultra|x3d|zen ?\d|nova lake|arrow lake|processor)\b"),
    ("Windows", r"\b(windows 1[01]|26h2|25h2|microsoft update)\b"),
]
# Stories that change what to buy or when.
MATTERS = r"(price|cost|shortage|launch|release|delay|discontinu|recall|tariff|stock|cheaper|expensive|msrp|leak|announce|tested|upgrade|vs\.?|supply|rais|cut|hike)"
SKIP = r"(deal|% off|save \$|coupon|black friday|prime day|giveaway|sponsored|best .* (deals|sales)|\breview\b|hands-on|unboxing|podcast|quiz)"
HOT = r"(shortage|price (hike|increase|rise)|prices? (soar|surge|jump|climb|double)|discontinu|recall|delay)"


def first_sentence(text, limit=220):
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text or ""))).strip()
    t = re.sub(r"\s*(Read more|Continue reading|The post .* appeared first on .*)\s*$", "", t, flags=re.I)
    m = re.match(r"(.{40,%d}?[.!?])(\s|$)" % limit, t)
    if m:
        return m.group(1)
    return (t[: limit - 1].rsplit(" ", 1)[0] + "…") if len(t) > limit else t


def parse_feed(name, xml_text):
    items = []
    root = ET.fromstring(xml_text)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entries = root.findall(".//item") or root.findall(".//a:entry", ns)
    for it in entries:
        def text(tag):
            el = it.find(tag) if not tag.startswith("a:") else it.find(tag, ns)
            return (el.text or "") if el is not None else ""
        title = html.unescape(text("title") or text("a:title")).strip()
        link = text("link").strip()
        if not link:
            el = it.find("a:link", ns)
            link = el.get("href", "") if el is not None else ""
        date = text("pubDate") or text("a:updated") or text("a:published")
        try:
            when = email.utils.parsedate_to_datetime(date).date() if "," in date else dt.date.fromisoformat(date[:10])
        except Exception:
            when = None
        desc = text("description") or text("a:summary")
        if title and link.startswith("https://") and when:
            items.append({"title": title, "link": link, "date": when, "desc": desc, "source": name})
    return items


def refresh_news(g):
    stories = []
    for name, url in FEEDS:
        try:
            stories += parse_feed(name, fetch(url))
        except Exception as e:
            log(f"News: {name} feed failed ({e}).")
    if not stories:
        log("News: no feeds could be read; keeping yesterday's news.")
        return False

    picked, seen = [], set()
    for s in sorted(stories, key=lambda s: s["date"], reverse=True):
        t = s["title"]
        if (TODAY - s["date"]).days > 14 or re.search(SKIP, t, re.I) or not re.search(MATTERS, t, re.I):
            continue
        tag = next((tag for tag, rx in TAGS if re.search(rx, t, re.I)), None)
        if not tag:
            continue
        key = re.sub(r"[^a-z0-9]", "", t.lower())[:50]
        if key in seen:
            continue
        seen.add(key)
        # "Coming" for future launches.
        if tag in ("GPU", "CPU") and re.search(r"\b(next|upcoming|coming|leak|rumou?r|20(2[7-9]))\b", t, re.I):
            tag = "Coming"
        picked.append({
            "Tag": tag, "Hot": False, "Title": t, "Body": first_sentence(s["desc"]) or t,
            "SourceName": s["source"], "SourceUrl": s["link"], "Date": s["date"].isoformat(), "Auto": True,
        })

    # Balance: at most 3 per tag, 7 automatic stories, the biggest ones marked.
    per_tag, auto = {}, []
    for p in picked:
        if per_tag.get(p["Tag"], 0) >= 3:
            continue
        per_tag[p["Tag"]] = per_tag.get(p["Tag"], 0) + 1
        auto.append(p)
        if len(auto) == 7:
            break
    # Hand-written stories (from the weekly review) stay for 30 days.
    for n in g["News"]:
        n.setdefault("Date", TODAY.isoformat())
    curated = [n for n in g["News"] if not n.get("Auto") and (TODAY - dt.date.fromisoformat(n["Date"])).days <= 30][:4]

    hot = sum(1 for n in curated if n.get("Hot"))  # at most 3 big stories in all
    for p in auto:
        if hot < 3 and re.search(HOT, p["Title"], re.I):
            p["Hot"], hot = True, hot + 1
    news = curated + auto
    if len(news) < 3:
        log(f"News: only {len(news)} stories found; keeping yesterday's news.")
        return False
    g["News"] = news
    log(f"News: {len(curated)} hand-picked + {len(auto)} from feeds.")
    return True


# ───────── translations ─────────

SKIP_KEYS = {"SourceUrl", "GpuSourceUrl", "RamSourceUrl", "PulsePage", "Date", "Glyph", "Updated", "Name", "SourceName",
             "GpuSource", "RamSource", "RamHistorySource", "Auto", "Schema", "Now", "Msrp", "Lowest", "Before"}


def strings(o, key=None):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "Tr" or k in SKIP_KEYS:
                continue
            yield from strings(v, k)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v, key)
    elif isinstance(o, str) and o.strip() and key not in SKIP_KEYS:
        yield o


def translate(g):
    used = set(strings(g))
    for code in ("es", "pt-BR"):
        g["Tr"].setdefault(code, {})
        g["Tr"][code] = {k: v for k, v in g["Tr"][code].items() if k in used}  # drop text no longer shown
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    missing = sorted(s for s in used if s not in g["Tr"]["es"] or s not in g["Tr"]["pt-BR"])
    if not missing:
        return
    if not key:
        log(f"Translations: {len(missing)} new texts stay in English (no GEMINI_API_KEY secret).")
        return
    prompt = (
        "Translate each English string for a Windows gaming app's PC hardware guide into Spanish (es) and Brazilian "
        "Portuguese (pt-BR). Keep product names, brand names, numbers, prices, units and placeholders like {0} exactly. "
        "Natural, short, casual-but-clear wording for gamers. Reply with JSON only: an object mapping each English string "
        'to {"es": "...", "pt-BR": "..."}.\n\n' + json.dumps(missing, ensure_ascii=False)
    )
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
    }).encode()
    for model in (os.environ.get("GEMINI_MODEL") or "gemini-flash-latest", "gemini-2.5-flash"):
        try:
            req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                data=body, headers={"Content-Type": "application/json", "x-goog-api-key": key})
            with urllib.request.urlopen(req, timeout=120) as r:
                out = json.loads(r.read())
            text = out["candidates"][0]["content"]["parts"][0]["text"]
            result = json.loads(re.sub(r"^```(json)?|```$", "", text.strip()))
            n = 0
            for en, tr in result.items():
                if en in missing and isinstance(tr, dict):
                    for code in ("es", "pt-BR"):
                        if isinstance(tr.get(code), str) and tr[code].strip():
                            g["Tr"][code][en] = tr[code].strip()
                    n += 1
            log(f"Translations: {n} of {len(missing)} new texts translated with {model}.")
            return
        except Exception as e:
            log(f"Translations: {model} failed ({e}).")
    log("Translations: new texts stay in English this time.")


# ───────── checks (same rules as the app's GuideContent.Parse, plus a few more) ─────────

def check(g):
    assert g.get("Schema") == 1, "Schema must be 1"
    dt.date.fromisoformat(g["Updated"][:10])
    for part in ("Tips", "Gpus", "Ram", "News"):
        assert g.get(part), f"{part} is empty"
    for c in g["Gpus"]:
        assert all(isinstance(c[k], int) and c[k] > 0 for k in ("Msrp", "Now", "Lowest")), c["Name"]
    dates = [p["Date"] for p in g["RamHistory"]]
    assert dates == sorted(dates), "RamHistory out of order"
    for n in g["News"] + [p for grp in g["Gear"] for p in grp["Picks"]] + g["Tips"] + g["Builders"]:
        u = n.get("SourceUrl")
        assert u is None or u.startswith("https://"), u
    assert len(json.dumps(g, ensure_ascii=False).encode()) < 1_500_000, "too big"


def main():
    with open(GUIDE, encoding="utf-8") as f:
        before = f.read()
    g = json.loads(before)
    checked = [refresh_gpus(g), refresh_ram(g), refresh_news(g)]
    if any(checked):
        g["Updated"] = TODAY.isoformat()
    translate(g)
    check(g)
    after = json.dumps(g, ensure_ascii=False, indent=1) + "\n"
    if after.strip() != before.strip():
        with open(GUIDE, "w", encoding="utf-8") as f:
            f.write(after)
        log("guide.json updated.")
    else:
        log("Nothing changed.")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## PC guide refresh\n\n" + "\n".join(f"- {line}" for line in LOG) + "\n")
    # Fail the run (so GitHub emails you) only when nothing at all could be checked.
    return 0 if any(checked) else 1


if __name__ == "__main__":
    sys.exit(main())
