from pathlib import Path
import json,re,html
p=Path('index.html');s=p.read_text()
checked='2026-11-06'
book='https://www.ncbi.nlm.nih.gov/books/NBK390354/'
ifcn='https://ifcn.info/education/videos/masterclass-recordings'
ncs='https://learning.neurocriticalcare.org/'
icna='https://www.icnapedia.org/icntn'
asnm='https://asnm.org/literature/'
resources=[
 dict(title='AES EEG Textbook and Atlas',url=book,description='Free 2016 American Epilepsy Society textbook edited by Erik K. St. Louis, MD and Lauren C. Frey, MD. Normal and abnormal EEG, developmental patterns, artifacts and technical principles. Pair older clinical material with current guidelines. No CEU credit established.',badge='Free textbook · Published 2016',provider='AES / NCBI Bookshelf'),
 dict(title='IFCN Masterclass Recordings',url=ifcn,description='Complimentary expert lectures in EEG, quantitative EEG, neonatal epilepsy and clinical neurophysiology. Free website registration and login are required for older recordings. EEG technologist CEU credit has not been verified.',badge='Free education · Registration',provider='IFCN'),
 dict(title='Neurocritical Care Society Learning Center',url=ncs,description='Society courses, clinical references and learning tools for neurological emergencies and ICU care. Access varies by product: some resources are free, others require payment or membership. Check the individual activity for credit eligibility.',badge='Mixed free and paid education',provider='Neurocritical Care Society'),
 dict(title='NCS Brain Death Determination Toolkit',url=ncs+'products/brain-death-determination-toolkit',description='Free educational toolkit based on the 2023 multidisciplinary brain death guideline, with clinical tools and FAQs. Registration required. Separate certification courses are paid. No EEG technologist CEU credit established; use current institutional policies.',badge='Free toolkit · Registration',provider='Neurocritical Care Society'),
 dict(title='ASNM Position Statements and Literature',url=asnm,description='Official society index of EEG, SSEP, MEP, auditory response and professional practice references supporting CNIM study. Index is public; access and publication dates vary by document. Reading these references does not independently award CEUs.',badge='Public reference index',provider='ASNM'),
 dict(title='ICNA International Child Neurology Teaching Network',url=icna,description='Expert pediatric neurology webinars and modular learning covering epilepsy, neonatal neurology and neurophysiology. Certificate courses require a paid subscription; check individual webinar access. These are child neurology resources, not an ABRET exam preparation program. EEG technologist CEU eligibility is unverified.',badge='Mixed access · Paid certificate courses',provider='ICNA')
]
def change_array(key,fn):
 global s
 start=s.index(key)+len(key);rows,n=json.JSONDecoder().raw_decode(s[start:]);rows=fn(rows)
 s=s[:start]+json.dumps(rows,ensure_ascii=False)+s[start+n:]
def education(rows):
 for x in reversed(resources):
  if not any(r['url'].rstrip('/')==x['url'].rstrip('/') for r in rows):
   rows.insert(0,dict(x,category='general',verified=checked,logo='?'))
 return rows
change_array('const curatedEducation=',education)
# Reuse existing society artwork for NCBI's AES publication and all registry references.
pat=r'(<script[^>]*id="eeg-logo-data"[^>]*>)(.*?)(</script>)'
m=re.search(pat,s,re.S);logos=json.loads(m[2])
aes_logo=logos.get('aesnet.org') or logos['www.aesnet.org']
logos['www.ncbi.nlm.nih.gov']=aes_logo
ncs_logo="https://learning.neurocriticalcare.org/accounts/ncs/images/logo.png"
icna_logo="https://www.icnapedia.org/images/42/ICNA-new-header-logo-min.png"
for host in ['learning.neurocriticalcare.org','www.neurocriticalcare.org','neurocriticalcare.org']:logos[host]=ncs_logo
for host in ['www.icnapedia.org','icnapedia.org']:logos[host]=icna_logo
s=s[:m.start(2)]+json.dumps(logos,separators=(',',':'))+s[m.end(2):]
def card(x,logo):
 return '<article class="entry" data-reviewed="'+checked+'"><div class="logo"><img src="'+html.escape(logo,quote=True)+'" alt="'+html.escape(x['provider'])+' logo" loading="lazy"></div><div class="info"><strong>'+html.escape(x['title'])+'</strong><p>'+html.escape(x['description'])+'</p><span class="tag">'+html.escape(x['badge'])+'</span></div><a class="visit" href="'+html.escape(x['url'],quote=True)+'" target="_blank" rel="noopener noreferrer">Visit Site</a></article>'
for section,x,logo in [('registry-free',resources[0],aes_logo),('registry-cnim-free',resources[4],logos.get('asnm.org') or logos['www.asnm.org'])]:
 marker='id="'+section+'">';assert marker in s
 start=s.index(marker);end=s.index('</section>',start)
 if x['url'] not in s[start:end]:s=s[:start+len(marker)]+card(x,logo)+s[start+len(marker):]
# Clarify the already listed ASNM paid CEU provider rather than add a duplicate.
def ceus(rows):
 for x in rows:
  if x.get('title')=='ASNM Education':
   x.update(url='https://asnm.org/upcoming-webinars/',category='paid',description='Webinars offer one ASNM CEU and are included with membership; nonmembers purchase access. Confirm credential eligibility and event completion rules. ASNM CEUs are distinct from ASET CEUs.',badge='ASNM CEU · Paid or membership',verified=checked)
 return rows
change_array('const curated=',ceus)
p.write_text(s)
providers=Path('data/discovered_providers.json');pd=json.loads(providers.read_text())
for name,url in [('Neurocritical Care Society',ncs),('ICNA / ICNTN',icna),('AES Textbook on NCBI Bookshelf',book),('IFCN Education',ifcn),('ASNM Literature',asnm)]:
 if not any(x['name']==name for x in pd['providers']):pd['providers'].append(dict(name=name,url=url,evidence_url=url,checked_at=checked))
providers.write_text(json.dumps(pd,indent=2,ensure_ascii=False)+'\n')
evidence=dict(checked=checked,requested_sources=resources,placements={'General Education':[x['title'] for x in resources],'Registry Prep R. EEG T. Free':['AES EEG Textbook and Atlas'],'Registry Prep CNIM Free':['ASNM Position Statements and Literature'],'Paid/Membership CEU Resources':['Existing ASNM Education listing clarified and linked to webinar information'],'Free CEU Resources':[]},credit_review=[
 {'provider':'IFCN','source':ifcn,'decision':'Free access with registration; no separately verified eligible CEU amount, expiration and completion rules. General Education only.'},
 {'provider':'NCS','source':ncs+'products/brain-death-determination-toolkit','decision':'Free access confirmed for nonmembers and nonphysicians; no verified EEG technologist credit. General Education only.'},
 {'provider':'NCS','source':ncs+'products/n-case-neurocritical-care-basics-curriculum-bundle','decision':'Members free, nonmember nonphysicians $39; explicitly no credits available. Not a free CEU source.'},
 {'provider':'ASNM','source':'https://asnm.org/upcoming-webinars/','decision':'One ASNM CEU; included with membership or purchased by nonmembers. Paid/Membership only. Current advertised event: Intraoperative Electrocorticography, Michelle Mora DO, November 18 2026, 7 through 8:30 PM Eastern.'},
 {'provider':'ASNM','source':'https://asnm.org/accreditation/','decision':'Provider distinguishes ASNM CEUs from ASET CEUs. EEG exam eligibility and credential recertification rules differ; users must confirm credential requirements.'},
 {'provider':'ASNM','source':'https://asnm.org/purchase-past-webinars/','decision':'Recorded webinars complimentary for members; $59 nonmembers. Not universally free.'},
 {'provider':'ICNA','source':'https://icnapedia.org/icntn-modules/icntn-subscription-plans','decision':'Certificate subscription $24.99 monthly, $130 six months or $225 yearly; webinar access must be checked individually. No verified technologist CEUs.'},
 {'provider':'AES / NCBI','source':book,'decision':'Free 2016 textbook by named clinical experts; no independent course credit.'}],
notes=['No resource added to Free CEU Resources without verified free eligible credit.','IFCN recordings belong in General Education because account access is required and public playback has not been independently validated.','No games, audio, trackers, favorites, header Easter eggs or layout scripts edited.'])
Path('data/requested-five-sources-2026-11-06.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\n')
print('Added six General Education listings, two registry supporting references; clarified paid ASNM credit. No unsupported free CEU additions.')
