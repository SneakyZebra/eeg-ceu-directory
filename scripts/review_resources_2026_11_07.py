"""Apply source reviewed Nov 7 resources without changing app behavior or saved data."""
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import json, re, html, hashlib

root = Path(__file__).resolve().parents[1]
p = root / 'index.html'
s = original = p.read_text()
payload = root / 'scripts/resource-review-2026-11-07.json'
if not payload.exists():
    payload = root / 'data/resource-review-2026-11-07.json'
review = json.loads(payload.read_text())
day = review['checked']

def canonical(url):
    u = urlsplit(url)
    host = (u.hostname or '').lower().removeprefix('www.')
    if host in {'youtube.com', 'youtu.be'}:
        return 'youtube:' + (parse_qs(u.query).get('v', [u.path.strip('/')])[0])
    if host == 'vimeo.com':
        return 'vimeo:' + u.path.strip('/').split('/')[0]
    return host + u.path.rstrip('/') + (('?' + u.query) if u.query else '')

def array(key, updates):
    global s
    start = s.index(key) + len(key)
    rows, length = json.JSONDecoder().raw_decode(s[start:])
    for row in reversed(updates):
        match = next((i for i, old in enumerate(rows) if canonical(old['url']) == canonical(row['url']) or old['title'].casefold() == row['title'].casefold()), None)
        if match is None:
            rows.insert(0, row)
        else:
            rows[match] = row
    assert len({canonical(x['url']) for x in rows}) == len(rows), key
    s = s[:start] + json.dumps(rows, ensure_ascii=False) + s[start + length:]

array('const curated=', review['changes']['ceu'])
array('const curatedEducation=', review['changes']['general'])

match = re.search(r'(<script[^>]*id="eeg-logo-data"[^>]*>)(.*?)(</script>)', s, re.S)
logos = json.loads(match[2])
for host in ['bscn.org.uk', 'www.bscn.org.uk']:
    logos[host] = 'https://bscn.org.uk/assets/img/logo.png'
for host in ['rhythmlink.com', 'www.rhythmlink.com']:
    logos[host] = 'https://rhythmlink.com/wp-content/themes/rhythmlink/images/logo_rhythmlink.svg'
s = s[:match.start(2)] + json.dumps(logos, ensure_ascii=False) + s[match.end(2):]

def card(x):
    logo = logos.get('myneuropathway.com') or logos['www.myneuropathway.com']
    esc = html.escape
    return ('<article class="entry" data-reviewed="' + day + '"><div class="logo"><img src="' + esc(logo, quote=True) + '" alt="Neuro Pathway logo" loading="lazy"></div><div class="info"><strong>' + esc(x['title']) + '</strong><p>' + esc(x['description']) + '</p><span class="tag">' + esc(x['badge']) + '</span></div><a class="visit" href="' + esc(x['url'], quote=True) + '" target="_blank" rel="noopener noreferrer">Visit Site</a></article>')

for x in review['changes']['registry']:
    marker = 'id="' + x['section'] + '">'
    start = s.index(marker) + len(marker)
    end = s.index('</section>', start)
    part = s[start:end]
    articles = list(re.finditer(r'<article\b[^>]*>.*?</article>', part, re.S))
    matching = [a for a in articles if x['title'] in html.unescape(a[0]) or x.get('match', '\0') in html.unescape(a[0]) or x['url'] in a[0]]
    assert len(matching) <= 1, x['title']
    if matching:
        a = matching[0]
        part = part[:a.start()] + card(x) + part[a.end():]
    else:
        part = card(x) + part
    s = s[:start] + part + s[end:]

brainstorm = {
    'Brainstorm R. EEG T. Prep Course': 'EEG exam review with recordings, outlines, flashcards, quizzes and tutoring. Listed at $250 for a one time purchase. Shop advertises access until passing; access and mentorship remain subject to provider policies and scheduling. Not endorsed by ABRET; no passing guarantee.',
    'Brainstorm CLTM / LTM Prep Course': 'CLTM review with an eight week or longer study plan, lectures, outlines, flashcards, quizzes and tutoring. Listed at $325 for a one time purchase. Access until passing is subject to provider policies; mentorship depends on scheduling. Not endorsed by ABRET; no passing guarantee.',
    'Brainstorm CNIM / IONM Board Prep Course': 'CNIM review in anatomy, modalities, instrumentation, anesthesia and troubleshooting. Listed at $375 for a one time purchase. Access until passing is subject to provider policies; mentorship depends on scheduling. Not endorsed by ABRET; no passing guarantee.'
}
for title, desc in brainstorm.items():
    pattern = r'(<strong>' + re.escape(title) + r'</strong>\s*<p>).*?(</p>)'
    s, n = re.subn(pattern, lambda m: m[1] + html.escape(desc) + m[2], s, flags=re.S)
    assert n == 1, (title, n)

# Verify the HTML's scripts outside the two content arrays and logo data are unchanged.
def behavior_scripts(doc):
    result = []
    for block in re.findall(r'<script\b[^>]*>.*?</script>', doc, re.S):
        if 'id="eeg-logo-data"' in block:
            continue
        for key in ['const curated=', 'const curatedEducation=']:
            if key in block:
                i = block.index(key) + len(key)
                _, n = json.JSONDecoder().raw_decode(block[i:])
                block = block[:i] + '[]' + block[i + n:]
        result.append(hashlib.sha256(block.encode()).hexdigest())
    return result

assert behavior_scripts(s) == behavior_scripts(original), 'Unexpected behavior or game modification'
assert 'assets/general-education-pagination.js' in s
assert 'assets/eeg-literature-search.js' in s
assert all(s.count('id="' + x + '"') == 1 for x in ['registry-free', 'registry-cltm-free', 'registry-cnim-free'])
p.write_text(s)

seeds_path = root / 'data/discovered_providers.json'
seeds = json.loads(seeds_path.read_text())
new_seeds = [
    dict(name='Rhythmlink', url='https://rhythmlink.com/', evidence_url=review['changes']['ceu'][1]['url'], checked_at=day),
    dict(name='British Society for Clinical Neurophysiology / ANS', url='https://bscn.org.uk/', evidence_url=review['changes']['general'][0]['url'], checked_at=day),
    dict(name='University Hospitals Cleveland EEG/Epilepsy Course', url='https://www.uhhospitals.org/', evidence_url='https://www.uhhospitals.org/for-clinicians/specialties/neurology-and-neurological-surgery/medical-education/eeg-epilepsy-course', checked_at=day, status='Research seed only; EEG technologist eligibility and applicable CEU approval unconfirmed'),
    dict(name='Neuro Pathway', url='https://myneuropathway.com/', evidence_url='https://myneuropathway.com/ceus/', checked_at=day)
]
for row in new_seeds:
    old = next((x for x in seeds['providers'] if x['name'] == row['name']), None)
    if old is None:
        seeds['providers'].append(row)
    else:
        old.update(row)
for row in seeds['providers']:
    if row['name'] in {'Neurodiagnostic Technology Institute', 'Brainstorm Board Prep', 'ACNS Guidelines'}:
        row['checked_at'] = day
seeds_path.write_text(json.dumps(seeds, indent=2, ensure_ascii=False) + '\n')
(root / 'data/resource-review-2026-11-07.json').write_text(json.dumps(review, indent=2, ensure_ascii=False) + '\n')
print('Applied Nov 7 reviewed resources; scripts, games, storage, pagination and search preserved.')
