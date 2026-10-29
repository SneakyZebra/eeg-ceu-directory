"""Daily EEG CEU discovery. Free public RSS feeds plus existing provider pages.
Requires requests and beautifulsoup4, already in requirements.txt.
Results are discovery candidates, never automatically verified for ABRET credit.
"""
import datetime as dt
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs, unquote
import requests
from bs4 import BeautifulSoup

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
]
# A rotating selection keeps daily requests modest while expanding search coverage.
QUERIES = [
    '"EEG" "continuing education" "free" webinar',
    '"neurodiagnostic" "CEU" "free"',
    '"EEG technologist" "credits" webinar',
    '"ABRET" "CEU" webinar',
    '"clinical neurophysiology" "free" webinar',
    '"epilepsy monitoring" "continuing education" webinar',
    '"intraoperative monitoring" "CEU" webinar',
    '"long term monitoring" "CEU" free',
    '"evoked potentials" "continuing education" webinar',
    '"EEG" "on demand" "CEU" free',
    '"neurodiagnostic" "education" "credits" course',
    '"seizure" "EEG" "free" educational webinar',
]
PATH = Path("ceu-offerings.json")
MAX_ITEMS = 500
MAX_NEW_PER_RUN = 30
HEADERS = {"User-Agent": "EEGCEUDirectory/2.0 (+https://sneakyzebra.github.io/eeg-ceu-directory/)"}
session = requests.Session()
session.headers.update(HEADERS)
today = dt.datetime.now(dt.timezone.utc)
date = today.date().isoformat()

def normalize(url):
    try:
        u = urlparse(url)
        if u.scheme not in ("https", "http") or not u.netloc:
            return ""
        # Remove tracking fragments, but keep query strings needed by course pages.
        return u._replace(fragment="").geturl().rstrip("/")
    except ValueError:
        return ""

def clean_title(value):
    return " ".join(value.split())[:180]

def looks_relevant(text):
    return bool(re.search(r"\b(EEG|neurodiagnostic|neurophysiology|epilepsy|seizure|evoked potentials|intraoperative monitoring|long.term monitoring|ABRET)\b", text, re.I)) and bool(re.search(r"\b(CEUs?|CECs?|credits?|continuing education|webinars?|courses?|training)\b", text, re.I))

def add(items, title, provider, url, category, source):
    title = clean_title(title)
    url = normalize(url)
    if not url or len(title) < 12 or url in items:
        return False
    if len(items) >= MAX_ITEMS:
        return False
    items[url] = {
        "title": title, "provider": provider, "url": url,
        "category": category, "status": "Needs verification",
        "date_added": date, "discovery_source": source,
    }
    return True

def google_news_url(query):
    from urllib.parse import urlencode
    return "https://news.google.com/rss/search?" + urlencode({
        "q": query + " when:30d", "hl": "en-US", "gl": "US", "ceid": "US:en"
    })

def extract_news_link(entry):
    link = entry.find("link")
    if link:
        return link.get_text(strip=True) or (link.next_sibling or "").strip()
    return ""

def discover(items):
    # RSS indexes news and announcements, not the entire web.
    # Rotate four searches daily; every query is checked at least every three days.
    offset = today.date().toordinal() % len(QUERIES)
    selected = [QUERIES[(offset + i) % len(QUERIES)] for i in range(4)]
    count = 0
    checks = []
    for query in selected:
        try:
            response = session.get(google_news_url(query), timeout=18)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            entries = soup.find_all("item")[:25]
            checks.append({"query": query, "results": len(entries)})
            for entry in entries:
                title = clean_title(entry.title.get_text(" ", strip=True)) if entry.title else ""
                link = extract_news_link(entry)
                if not looks_relevant(title):
                    continue
                # Google News links are intermediary links; retain them as unverified
                # discovery leads rather than pretending they are direct course links.
                provider = entry.source.get_text(" ", strip=True) if entry.source else "Web discovery"
                if add(items, title, provider, link, "unknown", "Google News RSS"):
                    count += 1
                if count >= MAX_NEW_PER_RUN:
                    return checks, count
        except (requests.RequestException, ValueError) as exc:
            print(f"Discovery search unavailable: {query}: {exc}")
        time.sleep(0.3)
    return checks, count

def monitor_sources(items):
    checked = []
    added = 0
    for provider, url, category in SOURCES:
        try:
            response = session.get(url, timeout=18)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            checked.append(provider)
            for a in soup.select("a[href]"):
                title = clean_title(a.get_text(" ", strip=True))
                target = urljoin(url, a["href"])
                if not (12 <= len(title) <= 140 and re.search(r"\b(CEUs?|CECs?|continuing education|credits?)\b", title, re.I)):
                    continue
                if normalize(target) == normalize(url):
                    continue
                if add(items, title, provider, target, category, "Provider monitoring"):
                    added += 1
        except requests.RequestException as exc:
            print(f"Provider unavailable: {provider}: {exc}")
    return checked, added

def main():
    try:
        old = json.loads(PATH.read_text(encoding="utf-8")) if PATH.exists() else {}
    except (json.JSONDecodeError, OSError):
        old = {}
    items = {normalize(x["url"]): x for x in old.get("items", []) if isinstance(x, dict) and x.get("url") and normalize(x["url"])}
    checked, provider_added = monitor_sources(items)
    searches, discovered = discover(items)
    # Preserve existing entries, and sort newly discovered items first.
    ordered = sorted(items.values(), key=lambda x: x.get("date_added", ""), reverse=True)
    payload = {
        "last_checked": today.isoformat(),
        "providers_checked": checked,
        "discovery_searches": searches,
        "discovery_candidates_added": discovered,
        "items": ordered[:MAX_ITEMS],
    }
    PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Checked {len(checked)} providers, ran {len(searches)} free discovery searches, added {provider_added} provider links and {discovered} discovery candidates.")
    print("All new discoveries require human verification of course availability, cost, and ABRET eligibility.")

if __name__ == "__main__":
    main()
