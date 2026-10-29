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
from collections import deque
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
MAX_VERIFY_PER_RUN = 80
MAX_CATALOG_PAGES_PER_RUN = 65
MAX_CATALOG_DEPTH = 2

# The original nine sources remain. New sites provide additional entry points.
SOURCES = [
    ("Stratus EEG U", "https://www.stratusneuro.com/eeg-u", "free"),
    ("Neuro Pathway", "https://myneuropathway.com/ceus/", "free"),
    ("Next Gen Neuro", "https://www.teamngn.com/ngngivesback-sponsor", "free"),
    ("ASET Member Resources", "https://www.aset.org/free-and-exclusive-member-resources/", "paid"),
    ("ASET Webinars", "https://www.aset.org/events/webinars/", "paid"),
    ("American Epilepsy Society", "https://learn.aesnet.org/", "unknown"),
    ("American Epilepsy Society Courses", "https://learn.aesnet.org/Listing/EMU-Caring-Safety-in-the-Epilepsy-Monitoring-Unit-11333", "unknown"),
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
    # Never infer free access from a provider. A course can be paid or member only.
    # Automated discovery is always unverified until individually reviewed.
    items[url] = {
        "title": title, "provider": tidy(provider) or "Web discovery",
        "url": url, "category": "unknown", "status": "Needs verification",
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


# Only specific courses with separately checked evidence may enter the Free list.
# Add a course here only after confirming BOTH $0 cost and eligible CEU credit.
# The expiry date automatically removes it when the credit period ends.
VERIFIED_FREE_COURSES = [
    {
        "title": "EMU Caring: Safety in the Epilepsy Monitoring Unit",
        "provider": "American Epilepsy Society",
        "url": "https://learn.aesnet.org/Listing/EMU-Caring-Safety-in-the-Epilepsy-Monitoring-Unit-11333",
        "credits": 3.5,
        "credit_type": "ASET CEU",
        "cost": 0,
        "expires": "2027-12-31",
        "verified_on": "2026-10-29",
    },
    {
        "title": "Neonatal and Pediatric Epilepsy Syndromes",
        "provider": "TeleSpecialists",
        "url": "https://learning.tstelemed.com/content/neonatal-and-pediatric-epilepsy-syndromes",
        "credits": 1.0,
        "credit_type": "ASET CEU",
        "cost": 0,
        "expires": "2026-11-01",
        "verified_on": "2026-10-29",
    },
]

def sync_verified_free(items):
    """Fail closed: only allowlisted courses with a valid expiry and $0 credit."""
    allowed = set()
    today = NOW.date()
    for course in VERIFIED_FREE_COURSES:
        url = normalize(course.get("url", ""))
        try:
            expires = dt.date.fromisoformat(course["expires"])
        except (KeyError, TypeError, ValueError):
            continue
        if not url or expires < today or course.get("cost") != 0 or not course.get("credits", 0) > 0:
            continue
        allowed.add(url)
        items[url] = {
            "title": course["title"], "provider": course["provider"], "url": url,
            "category": "free", "status": "Verified free credit",
            "credits": course["credits"], "credit_type": course["credit_type"],
            "cost": 0, "expires": course["expires"],
            "verified_on": course["verified_on"], "date_added": course["verified_on"],
            "discovery_source": "Manually verified course allowlist",
        }
    # Expired or withdrawn entries are not shown as free.
    for url, item in list(items.items()):
        if item.get("discovery_source") == "Manually verified course allowlist" and url not in allowed:
            del items[url]
    return len(allowed)


# Automated course-level checks use a deliberately strict evidence standard.
# A course is published only when the *same course page* explicitly says that
# both participation AND credit are free, names ASET CEUs, and gives an amount.
# Ambiguous listings remain in Verify Cost and Credit.

# ASET evidence and cost evidence must both be present on the individual
# course page. Merely mentioning ASET or saying a webinar is free is not enough.
ASET_CREDIT_PATTERNS = [
    re.compile(r"\b(\d+(?:\.\d+)?)\s*(?:approved\s*)?ASET\s*(?:CEUs?|credits?|continuing education units?)\b", re.I),
    re.compile(r"\bASET\b.{0,100}?\b(\d+(?:\.\d+)?)\s*(?:CEUs?|credits?|continuing education units?)\b", re.I),
    re.compile(r"\b(\d+(?:\.\d+)?)\s*(?:CEUs?|credits?)\b.{0,90}?\bASET\b", re.I),
]
ASET_APPROVAL = re.compile(r"\b(?:ASET\s*(?:approved|accredited|recognized|CEUs?|credits?)|(?:approved|accredited|recognized)\s+by\s+ASET)\b", re.I)
NO_COST_PHRASES = [
    re.compile(r"\b(?:free|complimentary|no.cost|zero.cost|at no charge)\b.{0,85}?\b(?:ASET\s*)?(?:CEUs?|continuing education credits?|credits?|certificates?)\b", re.I),
    re.compile(r"\b(?:ASET\s*)?(?:CEUs?|continuing education credits?|credits?|certificates?)\b.{0,85}?\b(?:free|complimentary|no.cost|at no charge)\b", re.I),
    re.compile(r"\b(?:no (?:registration|participation|enrollment|course) fee|free registration|registration is free|register for free|no.cost registration)\b", re.I),
    re.compile(r"\b(?:no fee (?:to|for) (?:participate|register|enroll|receive|claim|earn)|free (?:to attend|to enroll|to register))\b", re.I),
    re.compile(r"\b(?:price|cost|registration fee|course fee)\s*[:\-]?\s*\$?\s*0(?:\.00)?\b", re.I),
]
FREE_CREDIT_EXPLICIT = re.compile(
    r"(?:no (?:fee|charge|cost).{0,85}(?:receive|claim|earn|obtain).{0,45}(?:credit|CEU|certificate)"
    r"|(?:credit|CEU|certificate).{0,60}(?:no (?:additional )?(?:fee|charge|cost)|free of charge))", re.I)
NO_CREDIT = re.compile(
    r"\b(?:no (?:CEUs?|credits?) (?:are |is )?(?:available|offered|provided|awarded)"
    r"|does not (?:offer|provide|award) (?:CEUs?|credits?)"
    r"|not eligible for (?:ASET|CEUs?)"
    r"|(?:CEUs?|credits?) (?:are |is )?not (?:available|offered|provided))\b", re.I)
CHARGE = re.compile(
    r"(?:\$\s*[1-9]\d*(?:\.\d+)?\b"
    r"|(?:CEU|credit|certificate).{0,55}(?:additional fee|fee required|purchase required|separate purchase)"
    r"|(?:additional fee|fee required|purchase required).{0,55}(?:CEU|credit|certificate))", re.I)
GENERIC_CATALOG = re.compile(r"/(?:catalog|search|browse|all-courses|courses/?$|webinars/?$|education/?$)", re.I)

def verify_course_page(url):
    """Conservative, course-specific verification using public HTML evidence.

    Free registration alone never proves a free CEU. Require ASET approval,
    an amount, a free-cost signal, and an explicit indication the credit or
    certificate itself is free. Pages with ambiguity remain unverified.
    """
    try:
        if GENERIC_CATALOG.search(urlparse(url).path):
            return None
        response = SESSION.get(url, timeout=18)
        response.raise_for_status()
        if "text/html" not in response.headers.get("Content-Type", "text/html").lower():
            return None
        if len(response.content) > 1_500_000:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        body = soup.select_one("main, article, [role=main]") or soup.body or soup
        text = re.sub(r"\s+", " ", body.get_text(" ", strip=True))[:90000]
        if not ASET_APPROVAL.search(text) or NO_CREDIT.search(text) or CHARGE.search(text):
            return None
        credit_amounts = []
        for pattern in ASET_CREDIT_PATTERNS:
            for match in pattern.finditer(text):
                amount = float(match.group(1))
                if 0 < amount <= 30:
                    credit_amounts.append(amount)
        if not credit_amounts:
            return None
        if not any(p.search(text) for p in NO_COST_PHRASES):
            return None
        # Critical second check: free entry alone is not free credit.
        if not FREE_CREDIT_EXPLICIT.search(text) and not any(
            p.search(text) for p in NO_COST_PHRASES[:2]
        ):
            return None
        title = tidy((soup.find("h1").get_text(" ", strip=True)
                      if soup.find("h1") else
                      soup.title.get_text(" ", strip=True) if soup.title else
                      urlparse(url).path.rsplit("/", 1)[-1]))
        evidence = FREE_CREDIT_EXPLICIT.search(text)
        if not evidence:
            evidence = next((p.search(text) for p in NO_COST_PHRASES[:2] if p.search(text)), None)
        return {"title": title, "credits": min(credit_amounts),
                "evidence": tidy(text[max(0, evidence.start()-65):evidence.end()+65])}
    except (requests.RequestException, ValueError, TypeError) as exc:
        print(f"Verification unavailable ({url}): {exc}")
        return None

def verify_discovered_courses(items):
    # Always recheck previously automatically verified courses first.
    previously = [(url, item) for url, item in items.items()
                  if item.get("discovery_source") == "Automated course verification"]
    pending = [(url, item) for url, item in items.items()
               if item.get("category") == "unknown" and
               item.get("discovery_source") != "Manually verified course allowlist"]
    # Rotate candidates daily so the same first 45 are not checked forever.
    pending.sort(key=lambda pair: pair[0])
    if pending:
        offset = NOW.date().toordinal() % len(pending)
        pending = pending[offset:] + pending[:offset]
    checked = 0
    verified = 0
    for url, item in previously + pending[:max(0, MAX_VERIFY_PER_RUN-len(previously))]:
        # Only examine course-like pages; don't turn broad provider homepages into courses.
        if not re.search(r"/(?:listing|content|course|learn|webinar|session|event)/|course|webinar", url, re.I):
            continue
        result = verify_course_page(url)
        checked += 1
        if result:
            item.update(category="free", status="Verified free credit", cost=0,
                        credits=result["credits"], credit_type="ASET CEU",
                        expires=(NOW.date()+dt.timedelta(days=2)).isoformat(),
                        verified_on=TODAY, verification_evidence=result["evidence"],
                        discovery_source="Automated course verification")
            verified += 1
        elif item.get("discovery_source") == "Automated course verification":
            # Fail closed when evidence is gone or a provider cannot be reached.
            item.update(category="unknown", status="Needs verification",
                        discovery_source="Automated verification withdrawn")
            for field in ("cost", "credits", "credit_type", "expires", "verified_on", "verification_evidence"):
                item.pop(field, None)
    return checked, verified

# Provider catalog exploration, bounded to a small set of trusted domains.
# Discover course pages first; the separate verifier makes the free-credit decision.
CATALOG_SEEDS = [
    ("American Epilepsy Society", "https://learn.aesnet.org/Public/Catalog/StackHome.aspx?Criteria=166&Option=585&SearchMode=1"),
    ("American Epilepsy Society", "https://learn.aesnet.org/Public/Catalog/StackHome.aspx?Criteria=165&Option=633&SearchMode=1"),
    ("American Epilepsy Society", "https://learn.aesnet.org/"),
    ("ASET", "https://www.aset.org/education/"),
    ("ASET", "https://www.aset.org/events/webinars/"),
    ("Stratus EEG U", "https://www.stratusneuro.com/eeg-u"),
    ("Neuro Pathway", "https://myneuropathway.com/ceus/"),
    ("Next Gen Neuro", "https://www.teamngn.com/ngngivesback-sponsor"),
    ("TeleSpecialists", "https://learning.tstelemed.com/"),
    ("Cadwell", "https://www.cadwell.com/"),
    ("NeuroEnlight", "https://neuroenlight.com/"),
]
CATALOG_HOSTS = {
    "learn.aesnet.org", "www.aset.org", "aset.org", "www.stratusneuro.com",
    "stratusneuro.com", "myneuropathway.com", "www.myneuropathway.com",
    "www.teamngn.com", "teamngn.com", "learning.tstelemed.com",
    "www.cadwell.com", "cadwell.com", "neuroenlight.com", "www.neuroenlight.com",
}
COURSE_LINK = re.compile(r"/(?:Listing|Public/Catalog/Details|content|courses?|webinars?|sessions?|events?)/|(?:[?&](?:id|LearningActivityID)=)", re.I)
CRAWL_LINK = re.compile(r"catalog|course|webinar|education|ceu|learn|training|epilepsy|eeg|neuro|event", re.I)
SKIP_LINK = re.compile(r"(?:login|sign.?in|logout|cart|checkout|account|privacy|terms|contact|donate|subscribe|\.pdf(?:$|\?)|\.zip(?:$|\?))", re.I)

def discover_catalog_courses(items):
    """Explore a rotating, bounded set of catalog pages without third-party APIs."""
    seen = set()
    queue = deque((provider, url, 0) for provider, url in CATALOG_SEEDS)
    added = 0
    scanned = 0
    # Seed pages are all visited first; deeper pages rotate across days.
    while queue and scanned < MAX_CATALOG_PAGES_PER_RUN and len(items) < MAX_ITEMS:
        provider, url, depth = queue.popleft()
        key = normalize(url)
        if not key or key in seen or urlparse(key).hostname not in CATALOG_HOSTS:
            continue
        seen.add(key)
        try:
            r = SESSION.get(url, timeout=13)
            r.raise_for_status()
            if 'text/html' not in r.headers.get('Content-Type', 'text/html').lower() or len(r.content) > 1_500_000:
                continue
            scanned += 1
            soup = BeautifulSoup(r.text, 'html.parser')
            links = []
            for a in soup.select('a[href]'):
                target = normalize(urljoin(r.url, a.get('href', '')))
                if not target or urlparse(target).hostname not in CATALOG_HOSTS or SKIP_LINK.search(target):
                    continue
                title = tidy(a.get_text(' ', strip=True) or a.get('title') or '')
                context = tidy(a.parent.get_text(' ', strip=True) if a.parent else title)
                if COURSE_LINK.search(target) and target != key and len(title) >= 8:
                    # The actual page must still independently prove free ASET credit.
                    if add(items, title, provider, target, 'unknown', 'Deep catalog discovery'):
                        added += 1
                if depth < MAX_CATALOG_DEPTH and CRAWL_LINK.search(title+' '+target):
                    if target not in seen and target != key:
                        links.append((provider, target, depth+1))
            # Prioritize specific courses and vary remaining exploration each day.
            links.sort(key=lambda x: (not bool(COURSE_LINK.search(x[1])), x[1]))
            if links:
                offset = NOW.date().toordinal() % len(links)
                links = links[offset:] + links[:offset]
            queue.extend(links[:35])
        except requests.RequestException as e:
            print(f'Catalog unavailable ({provider}, {url}): {str(e)[:90]}')
        time.sleep(0.1)
    return scanned, added

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
    # Repair older automatically discovered listings that were wrongly marked free
    # simply because their provider was assumed to offer free courses.
    corrected = 0
    for item in items.values():
        if (item.get("discovery_source") in ("Provider monitoring", "Google News RSS", "bing RSS", "google_news RSS")
                and item.get("category") == "free"
                and item.get("status") == "Needs verification"):
            item["category"] = "unknown"
            corrected += 1
    checked, provider_added = monitor_sources(items)
    searches, discovered = search_discovery(items)
    catalog_pages, catalog_added = discover_catalog_courses(items)
    verified_free = sync_verified_free(items)
    checked_courses, auto_verified = verify_discovered_courses(items)
    payload = {
        "last_checked": NOW.isoformat(),
        "providers_checked": checked,
        "discovery_searches": searches,
        "discovery_candidates_added": discovered,
        "catalog_pages_scanned": catalog_pages,
        "catalog_candidates_added": catalog_added,
        "items": sorted(items.values(), key=lambda x: x.get("date_added", ""), reverse=True)[:MAX_ITEMS],
    }
    PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Providers checked: {len(checked)}; new provider leads: {provider_added}; "
          f"RSS queries: {len(searches)}; new search leads: {discovered}.")
    print(f"Catalog pages scanned: {catalog_pages}; new course candidates: {catalog_added}.")
    print(f"Corrected {corrected} previously misclassified free listings; {verified_free} curated verified free course(s) active; {checked_courses} course pages reviewed; {auto_verified} automatically verified.")
    print("New leads are unverified. Free access does not necessarily mean approved CEU credit.")

if __name__ == "__main__":
    main()
