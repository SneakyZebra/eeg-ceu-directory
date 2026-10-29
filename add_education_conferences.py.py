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

# Automated organization logos and distinct brain artwork
# Paste this section at the end of add_education_conferences.py.py.
import base64
import hashlib
import html as htmlmod
import json as jsonmod
import re as regex
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from pathlib import Path as FilePath

website = FilePath("index.html")
page_html = website.read_text(encoding="utf-8")
BEGIN = "<!-- EEG LOGO LIBRARY START -->"
END = "<!-- EEG LOGO LIBRARY END -->"

# Read the previous library to preserve working logos if a site is temporarily offline.
old_library = {}
if BEGIN in page_html and END in page_html:
    previous = page_html.split(BEGIN, 1)[1].split(END, 1)[0]
    match = regex.search(r'<script id="eeg-logo-data" type="application/json">(.*?)</script>', previous, regex.S)
    if match:
        try:
            old_library = jsonmod.loads(match.group(1))
        except (ValueError, TypeError):
            pass
    page_html = page_html.split(BEGIN, 1)[0] + page_html.split(END, 1)[1]

class LogoFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.candidates = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag != "img":
            return
        src = a.get("src") or a.get("data-src") or ""
        if not src or src.startswith("data:"):
            return
        clues = " ".join(str(a.get(k, "")) for k in ("alt", "class", "id", "title", "src")).lower()
        if "logo" not in clues:
            return
        if any(x in clues for x in ("partner-logo", "sponsor-logo", "footer-logo", "advert", "testimonial")):
            return
        score = (4 if "logo" in str(a.get("alt", "")).lower() else 0)
        score += (3 if "logo" in str(a.get("class", "")).lower() else 0)
        score += (2 if "logo" in src.lower() else 0)
        score += (2 if "header" in clues or "brand" in clues else 0)
        self.candidates.append((score, src))

def fetch(url, limit=1500000):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; EEGDirectoryLogoBot/1.0)"})
    with urlopen(req, timeout=6) as response:
        if response.status != 200:
            return None, None
        content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
        data = response.read(limit + 1)
        if len(data) > limit:
            return None, None
        return data, content_type

def image_type(data):
    if data.startswith(b"\x89PNG\r\n\x1a\n"): return "image/png"
    if data.startswith(b"\xff\xd8\xff"): return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP": return "image/webp"
    if data.startswith((b"GIF87a", b"GIF89a")): return "image/gif"
    return None

def find_official_logo(address):
    parsed = urlparse(address)
    root = parsed.scheme + "://" + parsed.netloc + "/"
    body, _ = fetch(root, 450000)
    if not body:
        return None
    parser = LogoFinder()
    parser.feed(body.decode("utf-8", "replace"))
    # Require the image to come from the same website or a subdomain.
    host = (parsed.hostname or "").lower()
    for _, relative in sorted(parser.candidates, reverse=True)[:8]:
        url = urljoin(root, relative)
        asset_host = (urlparse(url).hostname or "").lower()
        if not (asset_host == host or asset_host.endswith("." + host)):
            continue
        if urlparse(url).scheme != "https":
            continue
        raw, _ = fetch(url, 400000)
        mime = image_type(raw or b"")
        if mime:
            return "data:" + mime + ";base64," + base64.b64encode(raw).decode("ascii")
    return None

# Collect organization websites from the directory's source lists.
sources = {}
for name, url, *_ in edu:
    sources[urlparse(url).hostname or ""] = url
for name, org, url in conf:
    sources[urlparse(url).hostname or ""] = url

# Include CEU cards, using the real provider domain.
for match in regex.finditer(r'"url"\s*:\s*"(https?[^"]+)"', page_html):
    url = match.group(1).replace("\\/", "/")
    host = urlparse(url).hostname
    if host and host not in sources:
        sources[host] = url

library = dict(old_library)
results = {"official_site_logos": 0, "brain_fallbacks": 0, "cached": 0}
for host, url in sorted(sources.items()):
    if not host:
        continue
    try:
        discovered = find_official_logo(url)
    except Exception:
        discovered = None
    if discovered:
        library[host] = discovered
        results["official_site_logos"] += 1
    elif host in library:
        results["cached"] += 1
    else:
        results["brain_fallbacks"] += 1

# Create eight distinct, original SVG brain icons with EEG waveforms.
colors = [
    ("#a4e7d0", "#176b6c"), ("#b5c9ff", "#3e4e9d"),
    ("#f8ce94", "#9b5b26"), ("#eeb8da", "#954976"),
    ("#c6eaa5", "#527d2c"), ("#a9e1ed", "#286e86"),
    ("#d7baf4", "#75529a"), ("#f0d98f", "#8c7330")
]
brain_icons = []
for i, (fill, line) in enumerate(colors):
    rotation = [-8, 5, 0, 10, -5, 8, -10, 3][i]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="10" fill="#f0f6f8"/>
<g transform="rotate({rotation} 32 30)">
<path d="M32 13C24 6 14 10 13 19 5 22 5 32 11 37c-3 8 4 15 12 13 4 5 9 3 9-2 0 5 6 7 10 2 9 2 15-6 11-14 7-6 4-16-3-18-2-9-13-12-18-5Z" fill="{fill}" stroke="{line}" stroke-width="2.3"/>
<path d="M32 14v29M20 19q8 4 6 11M14 33q8-3 12 7M45 19q-8 4-6 11M50 33q-8-3-12 7" fill="none" stroke="{line}" stroke-width="2" stroke-linecap="round"/>
</g><path d="M8 {48+i%3}h11l4-8 5 15 6-11 4 4h18" fill="none" stroke="{line}" stroke-width="2.2" stroke-linejoin="round"/></svg>"""
    brain_icons.append("data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode("ascii"))

# The old card renderer must use the library instead of a favicon.
page_html = regex.sub(
    r"image\.src\s*=\s*'https://www\.google\.com/s2/favicons\?domain='\s*\+\s*encodeURIComponent\(new URL\(item\.url\)\.hostname\)\s*\+\s*'&sz=128';",
    "image.src = window.eegLogoFor(item.url);",
    page_html,
    count=1,
)
page_html = page_html.replace(
    "logo.textContent = initials;\n};\n\nimage.src = window.eegLogoFor(item.url);",
    "logo.replaceChildren();\n  const fallback = document.createElement('img');\n"
    "  fallback.src = window.eegBrainFor(item.url);\n"
    "  fallback.alt = 'Illustrated brain icon';\n"
    "  logo.append(fallback);\n};\n\nimage.src = window.eegLogoFor(item.url);"
)
# In case this is the first run and the original renderer is still present.
page_html = page_html.replace(
    "logo.textContent=item.logo||item.title.split(' ').map(w=>w[0]).slice(0,3).join('');",
    "const image=document.createElement('img');"
    "image.alt=item.title+' logo';"
    "image.src=window.eegLogoFor(item.url);"
    "image.onerror=()=>{image.src=window.eegBrainFor(item.url);image.onerror=null};"
    "logo.replaceChildren(image);"
)

library_json = jsonmod.dumps(library, separators=(",", ":")).replace("<", "\\u003c")
brains_json = jsonmod.dumps(brain_icons, separators=(",", ":"))
script = f"""
{BEGIN}
<style>
.entry .logo {{ overflow:hidden; padding:2px; }}
.entry .logo img {{ display:block; width:100%; height:100%; object-fit:contain; object-position:center; }}
.conference-card .conference-logo {{ width:52px; height:52px; display:block; object-fit:contain; object-position:center; border-radius:7px; background:#eef5f8; padding:2px; margin-bottom:12px; }}
</style>
<script id="eeg-logo-data" type="application/json">{library_json}</script>
<script>
window.eegBrainIcons = {brains_json};
window.eegLogoLibrary = JSON.parse(document.getElementById('eeg-logo-data').textContent);
window.eegBrainFor = function(url) {{
  let hash=0;
  for (const c of url) hash=(hash*31+c.charCodeAt(0))>>>0;
  return window.eegBrainIcons[hash % window.eegBrainIcons.length];
}};
window.eegLogoFor = function(url) {{
  const host=new URL(url).hostname;
  return window.eegLogoLibrary[host] || window.eegBrainFor(url);
}};
document.addEventListener('DOMContentLoaded', function() {{
  document.querySelectorAll('.conference-card').forEach(card => {{
    const link=card.querySelector('a[href]');
    if (!link) return;
    const img=document.createElement('img');
    img.className='conference-logo';
    img.alt='Organization logo or brain illustration';
    img.src=window.eegLogoFor(link.href);
    img.onerror=()=>{{img.onerror=null;img.src=window.eegBrainFor(link.href)}};
    card.prepend(img);
  }});
}});
</script>
<!-- Logo scan report: {htmlmod.escape(jsonmod.dumps(results))} -->
{END}
"""
# Insert before other scripts, so the logo functions exist when cards are created.
page_html = page_html.replace("</head>", script + "\n</head>", 1)
website.write_text(page_html, encoding="utf-8")
print("Daily logo scan:", jsonmod.dumps(results))
print("Official website logo images are used only when confidently detected. Otherwise a distinct brain illustration is shown.")


# Fix logos across all EEG CEU Directory tabs
from pathlib import Path

page = Path("index.html")
html = page.read_text(encoding="utf-8")

start = html.find("function add(item,unverified=false)")
end = html.find("const curatedEducation=", start)

if start == -1 or end == -1:
    raise RuntimeError("Could not find the CEU card renderer.")

section = html[start:end]

old_start = section.find("const initials = item.title.split")
old_end = section.find(
    "const info=document.createElement('div');",
    old_start
)

if old_start == -1 or old_end == -1:
    raise RuntimeError("Could not find the old logo code.")

replacement = """
const image=document.createElement('img');
image.alt=item.title+' logo or brain illustration';
image.loading='eager';
image.decoding='async';
image.style.width='100%';
image.style.height='100%';
image.style.objectFit='contain';
image.style.objectPosition='center';

image.onerror=function(){
  this.onerror=null;
  this.src=window.eegBrainFor(item.url);
};

image.src=window.eegLogoFor(item.url);
logo.replaceChildren(image);
"""

section = (
    section[:old_start]
    + replacement
    + section[old_end:]
)

html = html[:start] + section + html[end:]

page.write_text(html, encoding="utf-8")

print("All EEG directory logos updated successfully.")
