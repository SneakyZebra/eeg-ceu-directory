"""Free EEG CEU discovery for GitHub Actions.

Combines known providers, newly found education hubs, and broad RSS searches.
Every new result is a lead requiring human verification of CEU approval and cost.
Uses only requests and beautifulsoup4, already in requirements.txt.
"""
import datetime as dt
import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlencode, parse_qsl, urlunparse
import requests
from bs4 import BeautifulSoup

PATH = Path("ceu-offerings.json")
NOW = dt.datetime.now(dt.timezone.utc)
TODAY = NOW.date().isoformat()
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; EEGCEUDirectory/3.0; educational discovery)"}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
MAX_ITEMS = 500
MAX_NEW = 45

# The original nine sources remain. New sites provide additional entry points.
SOURCES = [
    ("Stratus EEG U", "https://www.stratusneuro.com/eeg-u", "free"),
    ("Neuro Pathway", "https://myneuropathway.com/ceus/", "free"),
    ("Next Gen Neuro", "https://www.teamngn.com/ngngivesback-sponsor", "free"),
    ("ASET Member Resources", "https://www.aset.org/free-and-exclusive-member-resources/", "paid"),
    ("ASET Webinars", "https://www.aset.org/events/webinars/", "paid"),
    ("American Epilepsy Society", "https://learn.aesnet.org/", "unknown"),
    ("ACNS", "https://www.acns.org/meetings/fall-courses/principles-of-clinical-neurophysiology/cme--ceu-information", "paid"),
    ("ILAE", "https://www.ilae.org/education", "unknown"),
    ("EpiCARE", "https://epi-care.eu/webinars/", "unknown"),
    ("ASET Events", "https://www.aset.org/events/", "unknown"),
    ("Neurocritical Care Society Webinars", "https://www.neurocriticalcare.org/NCS-Learning-Center/Access-My-Education/Industry-Sponsored-Webinars", "unknown"),
    ("Neurocritical Care Society Calendar", "https://www.neurocriticalcare.org/Events/Event-Calendar", "unknown"),
    ("NowYouKnowMed EEG Tech", "https://nowyouknowmed.com/sessions/eeg-tech", "unknown"),
]
# Broad searches work better than several mandatory quoted terms.
QUERIES = [
    "EEG technologist webinar", "neurodiagnostic CEU", "EEG continuing education",
    "ASET CEU webinar", "ABRET recertification education",
    "epilepsy EEG webinar", "clinical neurophysiology webinar",
    "critical care EEG webinar", "intraoperative monitoring education",
    "evoked potentials CEU", "long term EEG monitoring webinar",
    "EEG free online course", "neurodiagnostic training webinar",
    "EEG technologist education", "neurodiagnostic conference CEU",
    "seizure monitoring education",
]
# Separate broad news announcements from directly indexed educational pages.
# Bing RSS is a free public feed, not a paid search API. It can rate limit or change.
SEARCH_ENGINES = ("bing", "google_news")
TOPIC = re.compile(r"\b(EEG|electroencephalograph\w*|neurodiagnostic\w*|neurophysiolog\w*|epilep\w*|seizure\w*|evoked potentials?|intraoperative|neuromonitoring|long.term monitoring|ABRET|ASET)\b", re.I)
EDUCATION = re.compile(r"\b(CEUs?|CECs?|credit\w*|continuing education|webinar\w*|course\w*|seminar\w*|training|workshop\w*|education\w*|lecture\w*|board review|conference\w*)\b", re.I)
EXCLUDE = re.compile(r"\b(job opening|job posting|salary|hiring|vacancy|equipment for sale|used equipment)\b", re.I)
LINK_HINT = re.compile(r"webinar|course|ceu|credit|education|training|seminar|event|learn|register|session|workshop", re.I)
TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "fbclid", "gclid"}

def normalize(url):
    try:
        p = urlparse(url.strip())
        if p.scheme not in ("https", "http") or not p.netloc:
            return ""
        if p.hostname in {"localhost", "127.0.0.1"}:
            return ""
        query = urlencode([(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k.lower() not in TRACKING])
        path = p.path.rstrip("/") or "/"
        return urlunparse((p.scheme.lower(), p.netloc.lower(), path, "", query, ""))
    except (ValueError, AttributeError):
        return ""

def tidy(s):
    return " ".join(str(s or "").split())[:190]

def relevant(title, description=""):
    combined = tidy(title + " " + description)
    return bool(TOPIC.search(combined) and EDUCATION.search(combined) and not EXCLUDE.search(title))

def add(items, title, provider, url, category="unknown", source=""):
    url = normalize(url)
    title = tidy(title)
    if not url or len(title) < 12 or url in items or len(items) >= MAX_ITEMS:
        return False
    items[url] = {
        "title": title, "provider": tidy(provider) or "Web discovery",
        "url": url, "category": category, "status": "Needs verification",
        "date_added": TODAY, "discovery_source": source,
    }
    return True

def rss_items(content):
    """Correctly parse RSS as XML, not HTML (HTML parsers lose item/link data)."""
    root = ET.fromstring(content)
    for item in root.findall(".//item"):
        title = tidy(item.findtext("title"))
        link = tidy(item.findtext("link"))
        desc = tidy(BeautifulSoup(item.findtext("description") or "", "html.parser").get_text(" ", strip=True))
        source = item.find("source")
        provider = tidy(source.text if source is not None else "")
        yield title, link, desc, provider

def rss_url(engine, query):
    if engine == "bing":
        return "https://www.bing.com/search?" + urlencode({"q": query, "format": "rss"})
    return "https://news.google.com/rss/search?" + urlencode({
        "q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"
    })

def search_discovery(items):
    offset = NOW.date().toordinal() % len(QUERIES)
    selected = [QUERIES[(offset + i) % len(QUERIES)] for i in range(6)]
    stats = []
    added = 0
    for query in selected:
        for engine in SEARCH_ENGINES:
            try:
                r = SESSION.get(rss_url(engine, query), timeout=16)
                r.raise_for_status()
                entries = list(rss_items(r.content))[:25]
                matched = 0
                for title, link, desc, provider in entries:
                    if not relevant(title, desc):
                        continue
                    matched += 1
                    if add(items, title, provider or urlparse(link).netloc, link, "unknown", engine + " RSS"):
                        added += 1
                stats.append({"query": query, "engine": engine, "results": len(entries), "relevant": matched})
                if added >= MAX_NEW:
                    return stats, added
            except (requests.RequestException, ET.ParseError, ValueError) as e:
                stats.append({"query": query, "engine": engine, "error": str(e)[:110]})
                print(f"Search unavailable ({engine}, {query}): {e}")
            time.sleep(0.15)
    return stats, added

def monitor_sources(items):
    checked = []
    added = 0
    for provider, url, category in SOURCES:
        try:
            r = SESSION.get(url, timeout=16)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            checked.append(provider)
            for a in soup.select("a[href]"):
                title = tidy(a.get_text(" ", strip=True))
                target = urljoin(url, a.get("href", ""))
                # A short course name can be meaningful when the URL identifies an event.
                if not 12 <= len(title) <= 160 or not LINK_HINT.search(title + " " + target):
                    continue
                if not relevant(title, provider + " " + target):
                    continue
                if normalize(target) == normalize(url):
                    continue
                if add(items, title, provider, target, category, "Provider monitoring"):
                    added += 1
        except requests.RequestException as e:
            print(f"Provider unavailable ({provider}): {e}")
    return checked, added

def main():
    try:
        old = json.loads(PATH.read_text(encoding="utf-8")) if PATH.exists() else {}
    except (OSError, json.JSONDecodeError):
        old = {}
    items = {}
    for item in old.get("items", []):
        if isinstance(item, dict) and item.get("url"):
            key = normalize(item["url"])
            if key:
                items[key] = item
    checked, provider_added = monitor_sources(items)
    searches, discovered = search_discovery(items)
    payload = {
        "last_checked": NOW.isoformat(),
        "providers_checked": checked,
        "discovery_searches": searches,
        "discovery_candidates_added": discovered,
        "items": sorted(items.values(), key=lambda x: x.get("date_added", ""), reverse=True)[:MAX_ITEMS],
    }
    PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Providers checked: {len(checked)}; new provider leads: {provider_added}; "
          f"RSS queries: {len(searches)}; new search leads: {discovered}.")
    print("New leads are unverified. Free access does not necessarily mean approved CEU credit.")

if __name__ == "__main__":
    main()
