"""Supplemental free CEU review. Keep all application and saved-data behavior intact."""
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import json, re, hashlib

root=Path(__file__).resolve().parents[1]
report=json.loads((root/'scripts/free-ceu-review-2026-11-07.json').read_text())
p=root/'index.html';s=original=p.read_text()
key='const curated=';start=s.index(key)+len(key)
rows,n=json.JSONDecoder().raw_decode(s[start:])

def canonical(url):
    u=urlsplit(url);host=(u.hostname or '').lower().removeprefix('www.')
    if host in {'youtube.com','youtu.be'}:
        return 'youtube:'+parse_qs(u.query).get('v',[u.path.strip('/')])[0]
    if host=='vimeo.com':
        return 'vimeo:'+u.path.strip('/').split('/')[0]
    return host+u.path.rstrip('/')+('?' + u.query if u.query else '')

for row in reversed(report['existing_provider_offerings']):
    match=next((i for i,x in enumerate(rows) if canonical(x['url'])==canonical(row['url']) or x['title'].casefold()==row['title'].casefold()),None)
    if match is None:rows.insert(0,row)
    else:rows[match]=row

for row in rows:
    if row['title']=='Stratus EEG U':
        row['description']='Free monthly ASET CEU webinars for neurodiagnostic professionals. Select credit when registering, use matching ASET account details and your individual Zoom link, and attend the overwhelming majority live. Allow 5 to 7 weeks for credit processing. No attendance certificate issued; recordings and Elevate U do not award CEUs.'
        row['verified']=report['checked']
    elif row['title']=='Cadwell Learning':
        row['url']='https://www.cadwell.com/webinars/'
        row['description']='Official upcoming webinars and free educational archives. Credit varies by activity; sleep CSTE is not automatically EEG ASET credit. Verify course cost, approval and completion requirements.'
    elif row['title']=='TeleSpecialists':
        row['url']='https://learning.tstelemed.com/'
        row['description']='Official education catalog. Selected EEG activities list ASET credit; verify each course date, fee, eligibility and completion requirements.'
    elif row['title']=='Pocket NeuroDiagnostics':
        row['url']='https://pndpocketneurodiagnostics.com/class-details'
        row['description']='Paid EEG and LTM board preparation. ASET credit requires the live class and ASET ID; replay access does not independently award CEUs. Free Zoom registration is separate from paid course enrollment.'

assert len({canonical(x['url']) for x in rows})==len(rows),'Duplicate curated URL'
assert sum(x['category']=='free' for x in report['existing_provider_offerings'])==1
assert next(x for x in rows if 'Tech Troubleshooting' in x['title'])['category']=='unknown'
assert next(x for x in rows if x['title']=='Natus: Nonconvulsive Seizures')['category']=='unknown'
s=s[:start]+json.dumps(rows,ensure_ascii=False)+s[start+n:]

m=re.search(r'(<script[^>]*id="eeg-logo-data"[^>]*>)(.*?)(</script>)',s,re.S)
logos=json.loads(m[2])
for target,sources in [
    ('stratusneuro.zoom.us',['www.stratusneuro.com','stratusneuro.com']),
    ('learning.tstelemed.com',['tstelemed.com','www.tstelemed.com']),
    ('pndpocketneurodiagnostics.com',['pocketneurodiagnostics.com','www.pocketneurodiagnostics.com'])
]:
    source=next((host for host in sources if logos.get(host)),None)
    if source:logos[target]=logos[source]
logos['pndpocketneurodiagnostics.com']='https://images.squarespace-cdn.com/content/v1/66247d27be37741c7d52bb6b/c0af291f-bdcd-4f98-91ff-2424740a6789/processed_PNDlogo.jpg?format=1500w'
logos['www.pndpocketneurodiagnostics.com']=logos['pndpocketneurodiagnostics.com']
s=s[:m.start(2)]+json.dumps(logos,ensure_ascii=False)+s[m.end(2):]

def scripts(doc):
    result=[]
    for block in re.findall(r'<script\b[^>]*>.*?</script>',doc,re.S):
        if 'id="eeg-logo-data"' in block:continue
        if key in block:
            i=block.index(key)+len(key);_,length=json.JSONDecoder().raw_decode(block[i:])
            block=block[:i]+'[]'+block[i+length:]
        result.append(hashlib.sha256(block.encode()).hexdigest())
    return result
assert scripts(s)==scripts(original),'Unexpected application behavior change'
assert "remaining.toLocaleString()" in s
p.write_text(s)

providers=root/'data/discovered_providers.json'
seeds=json.loads(providers.read_text())
for row in report['new_research_providers']:
    match=next((x for x in seeds['providers'] if x['name']==row['name']),None)
    if match is None:seeds['providers'].append(row)
    else:match.update(row)
providers.write_text(json.dumps(seeds,indent=2,ensure_ascii=False)+'\n')
(root/'data/free-ceu-review-2026-11-07.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('Added one verified free Stratus course, two reviewed Verify listings, and eight research provider seeds; app scripts preserved.')
