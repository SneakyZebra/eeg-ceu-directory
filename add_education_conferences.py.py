from pathlib import Path
import json
p=Path('index.html');s=p.read_text(encoding='utf-8')
edu=[('ACNS Practice Guidelines','https://www.acns.org/practice/guidelines','Technical EEG standards and clinical practice guidelines'),('Learning EEG','https://www.learningeeg.com/','Structured EEG interpretation lessons and quizzes'),('EEG Atlas Online','https://eegatlas-online.com/index.php/en/','Annotated EEG cases and waveform practice'),('EEG Master','https://eegmaster.com/','Interactive EEG interpretation exercises'),('EEG Pedia','https://eegpedia.org/index.php?title=Main_Page','EEG terminology and waveform reference'),('Yale EEG Modules','https://campuspress.yale.edu/eegmodules/','Academic EEG teaching modules'),('EEG Platform','https://eegplatform.com/','Interactive EEG cases'),('NAEC Workforce Resources','https://naec-epilepsy.org/neurodiagnostic-workforce-resources','Competencies and professional development'),('ILAE Education','https://www.ilae.org/education','Epilepsy education and training'),('Stratus EEG U Recordings','https://www.stratusneuro.com/eeg-u','Recorded webinars for learning; recorded attendance does not provide the live CEUs'),('AES Learning Center','https://learn.aesnet.org/','Epilepsy and EEG curricula; individual offerings may separately award credits'),('ACNS Education','https://www.acns.org/education','Clinical neurophysiology learning resources')]
conf=[('ACNS Annual Meeting and Courses','ACNS','https://www.acns.org/meetings/annual-meeting-and-courses'),('ASET Annual Conference','ASET','https://www.aset.org/annual-conference/'),('AES Annual Meeting','AES','https://aesnet.org/AES-annual-meeting/'),('AAN Annual Meeting','AAN','https://www.aan.com/events/annual-meeting'),('NANS Annual Meeting','NANS','https://www.neuromodulation.org/'),('AANS Annual Scientific Meeting','AANS','https://www.aans.org/annual-meeting/'),('European Congress of Clinical Neurophysiology','ECCN','https://www.ifcn.info/'),('International Congress of Clinical Neurophysiology','IFCN','https://www.ifcn.info/'),('ABRET Credentialing and Events (no annual meeting confirmed)','ABRET','https://abret.org/')]
if 'data-view="conferences"' not in s:
 s=s.replace('data-view="general" type="button">General Education</button>','data-view="general" type="button">General Education</button><button aria-pressed="false" class="ceu-tab" data-view="conferences" type="button">Conferences</button>')
 s=s.replace("general:document.getElementById('general-education-view'),toolkit:","general:document.getElementById('general-education-view'),conferences:document.getElementById('conferences-view'),toolkit:")
 html='<main class="ceu-view" id="conferences-view" hidden><div class="general-education-note"><strong>Conferences and Professional Meetings</strong><p>Major meetings and professional organizations for EEG, epilepsy, neurology and neurophysiology. Check the official organizer for current dates, registration and CEU eligibility.</p></div><div class="conference-grid" id="conference-list"></div></main>'
 s=s.replace('<main class="ceu-view" id="ceu-directory-view">',html+'<main class="ceu-view" id="ceu-directory-view">')
if 'const curatedEducation=' not in s:
 data=[dict(category='general',title=t,url=u,description=d,badge='Learning resource',logo='?') for t,u,d in edu]
 js='const curatedEducation='+json.dumps(data)+';\ncuratedEducation.forEach(x=>add(x));\n'
 s=s.replace('curated.forEach(x=>add(x));',js+'curated.forEach(x=>add(x));')
if 'const conferenceEvents=' not in s:
 js="""<script>(function(){const conferenceEvents=DATA;const host=document.getElementById('conference-list');if(!host)return;conferenceEvents.forEach(([name,org,url])=>{const card=document.createElement('article');card.className='conference-card';const label=document.createElement('small');label.textContent=org;const h=document.createElement('h3');h.textContent=name;const link=document.createElement('a');link.href=url;link.target='_blank';link.rel='noopener noreferrer';link.textContent='Official meeting information ↗';card.append(label,h,link);host.append(card)});})();</script>""".replace('DATA',json.dumps(conf))
 s=s.replace('</body></html>',js+'</body></html>')
css='<style>.conference-grid{max-width:1280px;margin:auto;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.conference-card{background:#061e32;border:1px solid #204357;border-radius:12px;padding:22px}.conference-card h3{font-size:18px}.conference-card small,.conference-card a{color:#a3e572}.conference-card a{font-weight:700}@media(max-width:700px){.conference-grid{grid-template-columns:1fr}.ceu-tabs{flex-wrap:wrap}.ceu-tab{flex:1 1 40%}}</style>'
if '.conference-grid{' not in s:s=s.replace('</head><body>',css+'</head><body>')
s=s.replace('General Education — No Credits Offered','General Education — Learn Beyond CEUs').replace('These resources provide educational information but do not award continuing education credits for the listed offerings. They are useful for learning and professional development, but should not be counted toward ASET CEU or ABRET recertification requirements. Only resources explicitly confirmed as offering no credits appear here; unknown credit status stays in Verify Cost and Credit.','Curated learning platforms, EEG case libraries, clinical guidelines and professional development. ASET CEU credit has not been confirmed for these linked activities. Do not count them toward recertification; some providers offer separate credit bearing courses.').replace('Educational resources with no continuing education credits offered','High value learning resources without confirmed CEUs')
p.write_text(s,encoding='utf-8');print('Updated',len(edu),'education resources and',len(conf),'organization listings')


# Website logo and wording improvements
from pathlib import Path

page = Path("index.html")
html = page.read_text(encoding="utf-8")

start_marker = "<!-- BRANDING UPDATE START -->"
end_marker = "<!-- BRANDING UPDATE END -->"

branding = r"""
<!-- BRANDING UPDATE START -->
<style>
.entry .logo {
  overflow: hidden;
  padding: 5px;
}
.entry .logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.conference-card .conference-logo {
  width: 49px;
  height: 49px;
  border-radius: 7px;
  background: #eef5f8;
  padding: 6px;
  object-fit: contain;
  margin-bottom: 12px;
}
</style>
<script>
(function () {
  function improve() {
    document.querySelectorAll(".entry").forEach(card => {
      const square = card.querySelector(".logo");
      const link = card.querySelector("a[href]");
      if (!square || !link || square.dataset.updated) return;

      square.dataset.updated = "yes";
      const initials = square.textContent.trim();
      const domain = new URL(link.href).hostname;
      const img = document.createElement("img");
      img.alt = "Organization icon";
      img.loading = "lazy";
      img.src = "https://www.google.com/s2/favicons?domain=" +
        encodeURIComponent(domain) + "&sz=128";
      img.onerror = () => {
        img.remove();
        square.textContent = initials === "?" ? "EEG" : initials;
      };
      square.replaceChildren(img);
    });

    document.querySelectorAll(".conference-card").forEach(card => {
      if (card.dataset.updated) return;
      const link = card.querySelector("a[href]");
      if (!link) return;

      card.dataset.updated = "yes";
      const img = document.createElement("img");
      img.className = "conference-logo";
      img.alt = "Organization icon";
      img.loading = "lazy";
      img.src = "https://www.google.com/s2/favicons?domain=" +
        encodeURIComponent(new URL(link.href).hostname) +
        "&sz=128";
      img.onerror = () => img.remove();
      card.prepend(img);
    });

    const sections = document.querySelectorAll(
      ".entry .info, .conference-card, .general-education-note, .footer"
    );
    sections.forEach(section => {
      const walker = document.createTreeWalker(
        section, NodeFilter.SHOW_TEXT
      );
      while (walker.nextNode()) {
        const node = walker.currentNode;
        const original = node.nodeValue;
        const revised = original
          .replace(/\s*[—–]\s*/g, ", ")
          .replace(/\s+-\s+/g, ", ");
        if (original !== revised) node.nodeValue = revised;
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    improve();
    const observer = new MutationObserver(improve);
    ["free", "paid", "unknown", "general", "conference-list"]
      .forEach(id => {
        const element = document.getElementById(id);
        if (element) observer.observe(element, {childList: true});
      });
  });
})();
</script>
<!-- BRANDING UPDATE END -->
"""

if start_marker in html and end_marker in html:
    beginning = html.index(start_marker)
    ending = html.index(end_marker) + len(end_marker)
    html = html[:beginning] + html[ending:]

html = html.replace("</body>", branding + "\n</body>")
page.write_text(html, encoding="utf-8")
print("Branding and wording improvements applied")


# Fix organization icons directly in the website card renderer

from pathlib import Path

page = Path("index.html")
html = page.read_text(encoding="utf-8")

# Remove the previous logo replacement script
start = "<!-- BRANDING UPDATE START -->"
end = "<!-- BRANDING UPDATE END -->"

if start in html and end in html:
    a = html.index(start)
    b = html.index(end) + len(end)
    html = html[:a] + html[b:]

old = (
    "logo.textContent=item.logo||item.title.split(' ')"
    ".map(w=>w[0]).slice(0,3).join('');"
)

new = """
const initials = item.title.split(' ')
  .filter(w => w.length)
  .map(w => w[0])
  .slice(0,3)
  .join('')
  .toUpperCase();

logo.textContent = initials;

const image = document.createElement('img');
image.alt = item.title + ' logo';
image.loading = 'lazy';
image.style.width = '100%';
image.style.height = '100%';
image.style.objectFit = 'contain';

image.onload = () => {
  logo.replaceChildren(image);
};

image.onerror = () => {
  logo.textContent = initials;
};

image.src = 'https://www.google.com/s2/favicons?domain='
  + encodeURIComponent(new URL(item.url).hostname)
  + '&sz=128';
"""

if old in html:
    html = html.replace(old, new, 1)
    print("Card logo renderer updated")
elif "const initials = item.title.split" in html:
    print("Card logo renderer already updated")
else:
    raise RuntimeError("Could not find the card logo renderer")

# Preserve the square logo styling
css = """
<style>
.entry .logo {
  overflow: hidden;
  padding: 5px;
}
.entry .logo img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
"""

if ".entry .logo img {" not in html:
    html = html.replace("</head>", css + "</head>")

# Clean up unnecessary dashes in displayed descriptions
html = html.replace(" — ", ", ")
html = html.replace(" – ", ", ")

page.write_text(html, encoding="utf-8")
print("Logo and wording corrections saved")
