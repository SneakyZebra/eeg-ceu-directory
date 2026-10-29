import json, re, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

SOURCES = [
 ('Stratus EEG U','https://www.stratusneuro.com/eeg-u','free'),
 ('Neuro Pathway','https://myneuropathway.com/ceus/','free'),
 ('Next Gen Neuro','https://www.teamngn.com/ngngivesback-sponsor','free'),
 ('ASET Member Resources','https://www.aset.org/free-and-exclusive-member-resources/','paid'),
 ('ASET Webinars','https://www.aset.org/events/webinars/','paid'),
 ('American Epilepsy Society','https://learn.aesnet.org/','free'),
 ('ACNS','https://www.acns.org/meetings/fall-courses/principles-of-clinical-neurophysiology/cme--ceu-information','paid'),
 ('ILAE','https://www.ilae.org/education','free'),
 ('EpiCARE','https://epi-care.eu/webinars/','free'),
]
path=Path('ceu-offerings.json')
old=json.loads(path.read_text()) if path.exists() else {'items':[]}
items={x['url']:x for x in old.get('items',[]) if x.get('url')}
headers={'User-Agent':'Mozilla/5.0 (compatible; EEGCEUDirectory/1.0)'}
checked=[]
for provider,url,category in SOURCES:
 try:
  response=requests.get(url,headers=headers,timeout=20)
  response.raise_for_status()
  soup=BeautifulSoup(response.text,'html.parser')
  checked.append(provider)
  # Only direct activity links with explicit credit terminology; candidates remain unverified.
  for a in soup.select('a[href]'):
   title=' '.join(a.get_text(' ',strip=True).split())
   target=urljoin(url,a['href']).split('#')[0]
   if not 12 <= len(title) <= 140 or not re.search(r'\b(CEUs?|continuing education|credits?)\b',title,re.I):continue
   if urlparse(target).scheme not in ('http','https') or target.rstrip('/')==url.rstrip('/'):continue
   if target not in items:
    items[target]={'title':title,'provider':provider,'url':target,'category':category,'status':'Needs verification'}
 except requests.RequestException as exc:
  print(f'Provider unavailable: {provider}: {exc}')
if checked:
 payload={'last_checked':datetime.datetime.now(datetime.timezone.utc).isoformat(),'providers_checked':checked,'items':list(items.values())[:250]}
 path.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
