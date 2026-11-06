"""Evidence reviewed additions, 2026-11-06. Preserve the existing app and storage."""
from pathlib import Path
import json,re,html
from urllib.parse import urlparse
p=Path('index.html');s=p.read_text()
checked='2026-11-06'
def replace_array(key,fn):
 global s
 start=s.index(key)+len(key)
 rows,n=json.JSONDecoder().raw_decode(s[start:])
 rows=fn(rows)
 s=s[:start]+json.dumps(rows,ensure_ascii=False)+s[start+n:]
general=[
 dict(title='Neurovirtual: Video EEG',url='https://neurovirtualeducation.com/courses/video-eeg/',description='Free Spanish language course by Dr. Jorge G. Burneo of Western University. Surface video EEG, SEEG, ECoG and cortical stimulation. About 45 minutes; account and enrollment required. EEG technologist CEU credit has not been verified.',badge='Free course · Spanish · Registration'),
 dict(title='NIH / NCCIH: EEG Brain Mapping and BCI',url='https://www.nccih.nih.gov/training/videolectures/how-to-map-the-dynamics-of-your-brain',description='Bin He, PhD presents EEG brain mapping and brain computer interfaces in a free ten chapter NIH lecture. The page mentions credit, but current EEG technologist credit eligibility and expiration have not been verified.',badge='Free learning · CEUs unverified'),
 dict(title='ACNS Critical Care EEG Terminology: Condensed Version',url='https://cdn-links.lww.com/permalink/jcnp/a/jcnp_2020_12_21_fong_00313_sdc098.pdf',description='Public three page companion to the 2021 ACNS terminology, linked by the society. Background, rhythmic and periodic pattern reference. No CEU credit.',badge='Free society reference PDF'),
 dict(title='ACNS Critical Care EEG Examples',url='https://cdn-links.lww.com/permalink/jcnp/a/jcnp_2020_11_20_fong_1_sdc1.pdf',description='Public 36 page EEG example supplement linked by ACNS alongside its 2021 critical care EEG terminology. Supporting waveform reference for CLTM preparation; no CEU credit.',badge='Free EEG examples PDF')
]
def education(rows):
 for x in reversed(general):
  if not any(r['url'].rstrip('/')==x['url'].rstrip('/') for r in rows):
   rows.insert(0,dict(x,category='general',verified=checked,logo='?'))
 return rows
replace_array('const curatedEducation=',education)
lib=json.loads(re.search(r'<script[^>]*id="eeg-logo-data"[^>]*>(.*?)</script>',s,re.S)[1])
def registry_card(x):
 logo=lib.get('www.acns.org') or lib.get('acns.org')
 return '<article class="entry" data-reviewed="'+checked+'"><div class="logo"><img src="'+html.escape(logo,quote=True)+'" alt="ACNS logo" loading="lazy"></div><div class="info"><strong>'+html.escape(x['title'])+'</strong><p>'+html.escape(x['description'])+'</p><span class="tag">'+html.escape(x['badge'])+'</span></div><a class="visit" href="'+html.escape(x['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">Visit Site</a></article>'
marker='id="registry-cltm-free">'
assert marker in s
# Only deduplicate inside this credential subsection: repeated supporting references across tabs are intentional.
start=s.index(marker);end=s.index('</section>',start);part=s[start:end]
for x in general[2:]:
 if x['url'] not in part:
  s=s[:start+len(marker)]+registry_card(x)+s[start+len(marker):]
  end=s.index('</section>',start);part=s[start:end]
handbook='https://abret.org/application/files/2917/7245/9922/CLTM_Handbook_2026.pdf'
pattern=r'(<article class="entry"[^>]*>(?:(?!</article>).)*?<strong>ABRET CLTM Candidate Handbook</strong>.*?</article>)'
def handbook_card(m):
 return m[0].replace('https://abret.org/resources/handbooks',handbook).replace('Select the current CLTM handbook for the official examination outline, eligibility requirements and reference list.','Official 2026 CLTM candidate handbook with eligibility, examination outline, sample questions and references. Use ABRET for subsequent revisions.')
s,n=re.subn(pattern,handbook_card,s,flags=re.S)
assert n==1,('CLTM handbook match count',n)
p.write_text(s)
# Remove search/news/dictionary results from discovery data and an obsolete duplicate of EMU Caring.
q=Path('ceu-offerings.json');d=json.loads(q.read_text());removed=[]
def unsuitable(x):
 u=x.get('url','');host=urlparse(u).hostname or ''
 return host in {'news.google.com','www.merriam-webster.com','en.m.wikipedia.org','en.wikipedia.org'} or x.get('title')=='Jump to content' or ('EMU Caring' in x.get('title','') and '/Public/Catalog/' in u)
kept=[]
for x in d.get('items',[]):
 if unsuitable(x):removed.append(dict(title=x.get('title'),url=x.get('url'),reason='Unreviewed news/search/dictionary/navigation result or obsolete duplicate'))
 else:kept.append(x)
d['items']=kept
q.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
# Guard future discovery results before they are persisted; never turn them into verified resources.
up=Path('update_ceus.py');code=up.read_text()
guard='''    # Editorial safety filter: search/news wrappers are research leads, never education listings.
    for key,item in list(items.items()):
        host=(urlparse(item.get("url","")).hostname or "").lower()
        if host in {"news.google.com","www.merriam-webster.com","en.m.wikipedia.org","en.wikipedia.org"} or item.get("title")=="Jump to content":
            del items[key]
'''
if guard not in code:
 assert '    payload = {' in code
 code=code.replace('    payload = {',guard+'    payload = {',1)
up.write_text(code)
registry=Path('data/registry-credential-resources.json')
rd=json.loads(registry.read_text())
for row in rd['credentials']['CLTM']['free']:
 if row[0]=='ABRET CLTM Candidate Handbook':
  row[1]=handbook;row[2]='Official 2026 CLTM handbook, outline, sample questions and references. Rechecked November 6, 2026.'
registry.write_text(json.dumps(rd,indent=2,ensure_ascii=False)+'\n')
providers=Path('data/discovered_providers.json');pd=json.loads(providers.read_text())
for name,url,evidence in [
 ('Neurovirtual Education','https://neurovirtualeducation.com/','https://neurovirtualeducation.com/courses/video-eeg/'),
 ('NIH NCCIH','https://www.nccih.nih.gov/','https://www.nccih.nih.gov/training/videolectures/how-to-map-the-dynamics-of-your-brain'),
 ('EEGTeaching / Michel van Putten','https://eegteaching.org/','https://eegteaching.org/')]:
 if not any(x['name']==name for x in pd['providers']):
  pd['providers'].append(dict(name=name,url=url,evidence_url=evidence,checked_at=checked))
providers.write_text(json.dumps(pd,indent=2,ensure_ascii=False)+'\n')
report=dict(checked=checked,new_listed_providers=['Neurovirtual Education','NIH NCCIH'],new_research_provider_only=['EEGTeaching / Michel van Putten'],general_additions=general,CLTM_reference_additions=[x['url'] for x in general[2:]],handbook=dict(url=handbook,index_link_status='Index CLTM 2026 target returned 404; alternative official 2026 PDF verified'),removed_discovery_items=removed,
tabs={
'CEU Directory':{'new_verified_free_courses':0,'retained_verified':['AES EMU Caring: 3.5 ASET, $0, expires 2027-12-31; technologists in target audience','Neuro Pathway: first 300 viewers only for four open lectures; closed notices preserved','Stratus EEG U: live only; unique Zoom link and ASET ID; replays no credit; Elevate U no credit'],'sources':['https://learn.aesnet.org/Listing/EMU-Caring-Safety-in-the-Epilepsy-Monitoring-Unit-11333','https://myneuropathway.com/ceus/','https://www.stratusneuro.com/eeg-u','https://neuro-training.academy/eeg-ltm/','https://www.teamngn.com/ngngivesback-sponsor','https://www.cadwell.com/webinars/']},
'Videos':{'added':0,'sources':['https://corticare.com/webinars/','https://www.persyst.com/grandrounds/','https://sites.rutgers.edu/ru-cecnj/education/online-eeg-education-resources/'],'candidate':{'provider':'NIH NCCIH','youtube_id':'Vknf3KelgNo','runtime':'5:43','url':'https://www.nccih.nih.gov/training/videolectures/16/1','decision':'Withheld from Videos: source identifies free lecture and runtime but public YouTube playback not independently confirmed; embed fetch throttled. General Education landing page added with no credit claim.'}},
'Conferences':{'changed':False,'sources':['https://www.acns.org/news/2027-annual-meeting--courses---new-dates','https://www.aset.org/aset-conference-save-the-date/','https://www.ilae.org/congresses/37th-international-epilepsy-congress'],'notes':'ACNS March 6 through 9, 2027 Seattle and ASET August 5 through 7, 2027 Orlando agree with current cards. No new credit claims.'},
'Registry Prep':{'sources':['https://www.brainstormboardprep.com/shop','https://www.brainstormboardprep.com/terms-disclosures-and-policies','https://neurodiagnostictechnologyinstitute.com/pay-fees/','https://neurodiagnostictechnologyinstitute.com/our-program/','https://www.acns.org/practice/guidelines',handbook],'notes':'Brainstorm EEG $250, LTM $325, CNIM $375 paid one time; access subject to policies, independent of ABRET. NTI paid 12 month EEG program; no confirmed CLTM course. Added two public ACNS reference supplements to CLTM.'},
'Toolkit':{'source':'https://www.abret.org/recertification/recertification-faq','changed':False,'notes':'Official recertification guidance rechecked. No tracker, favorites, local storage or progress code touched.'}},
limitations=['This is a bounded source scan, not a full HTTP audit of every existing URL.','Public YouTube playback checks limited by fetch throttling; no unverified video added.','NIH credit mentioned but EEG technologist eligibility, expiration and completion rules unverified; no free CEU claim.'])
Path('data/resource-review-2026-11-06.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('Added 4 General Education references, 2 CLTM reference cards; updated official CLTM handbook; removed',len(removed),'discovery entries')
