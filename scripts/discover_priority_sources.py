#!/usr/bin/env python3
"""Discover potential EEG education resources from priority sites for human review."""
import json
import pathlib
import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

SOURCES = {
    "ACNS": "https://www.acns.org/",
    "Learning EEG": "https://www.learningeeg.com/",
    "Neurotech EEG Institute": "https://www.neurotecheeginstitute.com/",
    "Neurodiagnostic Niche": "https://neurodiagnosticniche.com/",
    "EpilepsyDiagnosis": "https://www.epilepsydiagnosis.org/",
    "Neurotech EEG Program": "https://www.neurotecheeginstitute.com/programs/eeg-program",
}
WORDS = re.compile(r"(eeg|ceu|cec|credit|webinar|course|conference|training|registry|video|certificate|education|epilepsy)", re.I)

class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.href = None
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.parts = []
    def handle_data(self, data):
        if self.href is not None:
            self.parts.append(data)
    def handle_endtag(self, tag):
        if tag == "a":
            if self.href:
                self.links.append((self.href, " ".join(" ".join(self.parts).split())))
            self.href = None

results = []
for name, url in SOURCES.items():
    entry = {"source": name, "source_url": url, "status": "ok", "candidates": []}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; EEG-CEU-Directory/1.0)"})
        with urllib.request.urlopen(req, timeout=20) as response:
            page = response.read(750000).decode("utf-8", "replace")
        parser = AnchorParser()
        parser.feed(page)
        seen = set()
        for href, title in parser.links:
            target = urljoin(url, href).split("#", 1)[0]
            if urlparse(target).scheme not in ("https", "http") or target in seen:
                continue
            if not WORDS.search(title + " " + target):
                continue
            seen.add(target)
            entry["candidates"].append({
                "title": title[:160] or "Review resource",
                "url": target,
                "suggested_tab": "Review for CEU Directory, General Education, Registry Prep, Conferences or Videos",
                "credit_status": "Unverified",
                "price_status": "Unverified"
            })
            if len(entry["candidates"]) >= 40:
                break
    except Exception as exc:
        entry["status"] = "fetch_error"
        entry["error"] = str(exc)[:180]
    results.append(entry)

path = pathlib.Path("data/priority_source_candidates.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Checked", len(results), "priority source URLs.")
