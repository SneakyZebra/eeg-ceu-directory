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
# Provider discovery is deliberately extensible; verified additions are reviewed separately.
SOURCES.update(json.loads("{\"ASET Education\":\"https://www.aset.org/education/\",\"ABRET Education Links\":\"https://abret.org/about/links\",\"AES Learning Center\":\"https://learn.aesnet.org/\",\"ILAE Webinars\":\"https://www.ilae.org/congresses/webinars\",\"Neuro Pathway CEUs\":\"https://myneuropathway.com/ceus/\",\"NGN Institute\":\"https://www.teamngn.com/ngngivesback-sponsor\",\"Natus Neuro Training Academy\":\"https://neuro-training.academy/eeg-ltm/\",\"CortiCare Webinars\":\"https://corticare.com/webinars/\",\"TeleSpecialists Learning Center\":\"https://learning.tstelemed.com/courses\",\"Cadwell Education\":\"https://www.cadwell.com/webinars/\",\"Persyst Grand Rounds\":\"https://www.persyst.com/grandrounds/\",\"Yale EEG Education\":\"https://medicine.yale.edu/neurology/education/educationaltools/\",\"Rutgers EEG Education Directory\":\"https://sites.rutgers.edu/ru-cecnj/education/online-eeg-education-resources/\",\"Pocket NeuroDiagnostics\":\"https://pndpocketneurodiagnostics.com/ceu-opportunities\"}"))
registry_path = pathlib.Path("data/discovered_providers.json")
if registry_path.exists():
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for provider in registry.get("providers", []):
        name, url = provider.get("name"), provider.get("url")
        if name and url and urlparse(url).scheme in ("http", "https"):
            SOURCES[name] = url

WORDS = re.compile(r"(eeg|ceu|cec|credit|webinar|course|conference|training|registry|video|certificate|education|epilepsy)", re.I)

class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.href = None
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag == "iframe":
            source = dict(attrs).get("src", "")
            if any(host in source for host in ("youtube.com/embed/", "youtube-nocookie.com/embed/", "player.vimeo.com/video/")):
                self.links.append((source, "Educational video: verify free public playback"))
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
