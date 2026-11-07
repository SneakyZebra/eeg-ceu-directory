"""Audit free registration versus paid membership without changing application behavior."""
from pathlib import Path
import json, re, hashlib

root=Path(__file__).resolve().parents[1]
p=root/'index.html'
s=original=p.read_text()
key='const curated='
start=s.index(key)+len(key)
rows,n=json.JSONDecoder().raw_decode(s[start:])
before={x['title']:dict(x) for x in rows}
checked='2026-11-07'
changed=[]
for row in rows:
    title=row['title']
    if row['category']=='free' and title.startswith('Neuro Pathway'):
        prefix='Free registration; no paid membership required. '
        if not row['description'].startswith(prefix):
            row['description']=prefix+row['description']
        if 'Free registration' not in row['badge']:
            row['badge']+=' · Free registration'
        row['accessRequirement']='Free registration; no paid membership'
        row['accessChecked']=checked
    elif row['category']=='free' and title.startswith('Stratus EEG U'):
        prefix='Free webinar registration; no paid membership required. '
        if not row['description'].startswith(prefix):
            row['description']=prefix+row['description']
        note=' ASET tracks nonmember credits with a valid ASET account and ID; its separately purchased nonmember transcript costs $30.'
        if note not in row['description']:
            row['description']+=note
        row['accessRequirement']='Free webinar registration and ASET ID; no paid membership'
        row['accessChecked']=checked
        row['documentationCostNote']='ASET nonmember transcript: $30, separate from earning credit. Stratus does not issue attendance certificates.'
        row['documentationSource']='https://www.aset.org/faq/'
    elif title=='AES EMU Caring: Safety in the Epilepsy Monitoring Unit':
        row['description']=row['description'].replace('Registration required.','Free myAES account and activity registration required; no paid AES membership required.')
        if 'Free account' not in row['badge']:
            row['badge']+=' · Free account'
        row['accessRequirement']='Free myAES account and activity registration; no paid membership'
        row['accessChecked']=checked
    elif title=='ASET Member Resources':
        row['description']='Member webinars, quizzes and educational materials are benefits of paid ASET membership. A free ASET account or ASET ID does not include paid member benefits.'
        row['badge']='Paid membership benefits'
        row['accessRequirement']='Paid membership for member benefits'
        row['accessChecked']=checked
    elif title=='ASET Membership':
        row['description']='Paid professional society membership with member journal quizzes and webinar benefits. ASET can track nonmember credits with an account and accurate ASET ID; nonmembers can purchase an individual transcript for $30.'
        row['badge']='Paid membership'
        row['accessRequirement']='Paid membership; separate account for nonmember credit tracking'
        row['accessChecked']=checked
    elif title=='Natus Neuro Training Academy':
        row['description']='Free account access to neurodiagnostic education and selected credit bearing courses. A free account does not establish EEG technologist credit eligibility. Confirm the specific EEG course credit type, fees, current dates and completion requirements before claiming CEUs.'
        row['accessRequirement']='Free account; course credit and EEG eligibility require verification'
        row['accessChecked']=checked
    elif title=='Natus: Nonconvulsive Seizures':
        row['description']=row['description'].replace('Free course access with registration.','Free course access with a free Neuro Training Academy account and registration.')
        row['accessRequirement']='Free account; nursing credit does not establish EEG technologist eligibility'
        row['accessChecked']=checked
    if row!=before[title]:changed.append(title)

assert len(rows)==len(before)
assert all(row['category']==before[row['title']]['category'] for row in rows)
assert sum(row['category']=='free' for row in rows)==9
assert next(x for x in rows if x['title']=='Natus: Nonconvulsive Seizures')['category']=='unknown'
s=s[:start]+json.dumps(rows,ensure_ascii=False)+s[start+n:]
old='Providers with free education resources. Check each course and credit'
new='Free accounts or registration may be required. Paid memberships are listed separately.'
assert s.count(old)+s.count(new)==1
s=s.replace(old,new)

def protected_scripts(doc):
    result=[]
    for block in re.findall(r'<script\b[^>]*>.*?</script>',doc,re.S):
        if key in block:
            i=block.index(key)+len(key)
            _,length=json.JSONDecoder().raw_decode(block[i:])
            block=block[:i]+'[]'+block[i+length:]
        result.append(hashlib.sha256(block.encode()).hexdigest())
    return result
assert protected_scripts(s)==protected_scripts(original),'Unexpected application behavior change'
assert 'Show More (' in s
p.write_text(s)

report={
 'checked':checked,
 'scope':'Existing CEU Directory listings: free accounts and registration versus paid professional membership',
 'new_providers':[],
 'new_qualifying_free_courses':[],
 'reclassified_resources':[],
 'reviewed_listings':[row['title'] for row in rows if row.get('accessChecked')==checked],
 'summary':'No existing paid membership listing qualified for reclassification based on generally available free membership. Clarified nine existing free listings and four account or membership listings.',
 'verified_free_access':[
  {'provider':'American Epilepsy Society','offering':'EMU Caring: Safety in the Epilepsy Monitoring Unit',
   'account_or_membership':'Free myAES account plus activity registration; paid AES membership is not required',
   'access_cost_usd':0,'credit_cost_usd':0,'credit':'3.5 ASET credits','expires':'2027-12-31',
   'audience':'Electroneurodiagnostic technologists explicitly included',
   'completion':'Read disclosures, study modules, satisfactorily complete pre and post assessments and submit evaluation',
   'sources':['https://learn.aesnet.org/Listing/EMU-Caring-Safety-in-the-Epilepsy-Monitoring-Unit-11333','https://aesnet.org/AES-annual-meeting/general-information/faqs']},
  {'provider':'Stratus','offering':'EEG U, including Neonatal EEG on November 12, 2026',
   'account_or_membership':'Free individual webinar registration and accurate ASET account details and ID; paid professional membership is not required',
   'access_cost_usd':0,'credit_cost_usd':0,'credit':'ASET CEUs; Neonatal EEG awards 1',
   'availability':'Registration open; Neonatal EEG live November 12, 2026 at noon Pacific / 3 PM Eastern',
   'completion':'Select credit at registration; attend overwhelming majority live using individual Zoom link; allow 5 to 7 weeks for posting',
   'restrictions':['No replay credit','Elevate U does not award CEUs','No attendance certificates issued'],
   'documentation_fee_note':'ASET charges nonmembers $30 for an individually purchased transcript, separate from earning credit. Do not imply a Zoom email is necessarily sufficient for ABRET.',
   'sources':['https://www.stratusneuro.com/eeg-u','https://stratusneuro.zoom.us/webinar/register/WN_uCIu9F4SQUeOJJZ-Avzr1w','https://www.aset.org/faq/']},
  {'provider':'Neuro Pathway','offering':'Five current ASET credit lectures',
   'account_or_membership':'Free registration; no paid membership required',
   'access_cost_usd':0,'credit_cost_usd':0,'credit':'ASET CEU',
   'availability':'Each current lecture limited to first 300 viewers; remaining places not exposed; no calendar expiration published',
   'completion':'Register, watch lecture and follow postlecture survey instructions',
   'current_titles':['Causation is Not Always Correlation','The ECG and EEG Connection','EEG Report Writing','From Onboarding to Excellence','Frontal and Temporal Lobe Epilepsies'],
   'restrictions':['Preserve first 300 viewers cap','Lectures marked closed no longer award ASET credit'],
   'sources':['https://myneuropathway.com/ceus/']}
 ],
 'paid_membership_checks':[
  {'provider':'ASET','finding':'Standard membership has dues. A free account/ASET ID for credit tracking is distinct from paid member benefits. Nonmember individual transcript costs $30.',
   'sources':['https://www.aset.org/membership/','https://www.aset.org/faq/']},
  {'provider':'ACNS','finding':'Standard membership has dues. Complimentary emeritus membership is restricted and requires approval; it is not a general free enrollment route.',
   'sources':['https://www.acns.org/membership/member-types']},
  {'provider':'ASNM','finding':'Webinar benefits are included with paid membership; nonmembers purchase access. No general free membership verified.',
   'sources':['https://asnm.org/member-benefits/','https://asnm.org/upcoming-webinars/']},
  {'provider':'American Epilepsy Society','finding':'Free myAES account differs from paid professional membership. Restricted senior membership is not a general free enrollment route.',
   'sources':['https://aesnet.org/aes-membership/become-a-member/dues','https://aesnet.org/AES-annual-meeting/general-information/faqs']}
 ],
 'free_account_not_sufficient':[
  {'provider':'Natus Neuro Training Academy','offering':'Nonconvulsive Seizures',
   'finding':'Free account and course access. Listed 1.5 contact hours are California BRN nursing credit, provider 16614. EEG technologist eligibility, ABRET acceptance, separate credit fees and expiration are unconfirmed. Retain Verify Cost and Credit.',
   'sources':['https://neuro-training.academy/about/','https://neuro-training.academy/online-courses/nonconvulsive-seizures/']},
  {'provider':'Rhythmlink','finding':'An ASET ID does not require ASET membership, but that does not establish that the event and credit are free. Preserve Verify Cost and Credit pending explicit fee evidence.',
   'sources':['https://rhythmlink.com/events/pediatric-patients-sports-epilepsy-webinar/']}
 ],
 'future_scan_rule':'Treat generally available free membership like free account registration only when both course access and applicable EEG technologist credit are independently verified at no charge. Check certificate/transcript charges separately; retain viewer caps, live-only rules and expiration.'
}
(root/'data/membership-access-review-2026-11-07.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('Clarified',len(changed),'existing listings; categories, branding and all application scripts preserved.')
