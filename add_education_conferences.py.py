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
    print("Logo renderer already updated, continuing")

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

# Display six CEU resources with expandable sections
from pathlib import Path

page = Path("index.html")
html = page.read_text(encoding="utf-8")

start = "<!-- CEU SIX CARD LIMIT START -->"
end = "<!-- CEU SIX CARD LIMIT END -->"

if start in html and end in html:
    html = html.split(start, 1)[0] + html.split(end, 1)[1]

feature = """
<!-- CEU SIX CARD LIMIT START -->
<style>
.ceu-show-toggle {
  display:block;
  width:100%;
  margin:14px 0;
  padding:12px;
  background:#0d3048;
  color:#c9f6a8;
  border:1px solid #69be28;
  border-radius:9px;
  font:inherit;
  font-weight:700;
  cursor:pointer;
}
</style>
<script>
(function(){
  const limit=6;

  function setup(id){
    const host=document.getElementById(id);
    if(!host)return;

    const button=document.createElement('button');
    button.className='ceu-show-toggle';
    button.type='button';
    host.after(button);
    let visible=limit;

    function update(reset){
      if(reset===true)visible=limit;
      const all=Array.from(host.children)
        .filter(el=>el.classList.contains('entry'));
      const cards=all.filter(card=>card.dataset.eegMatch!=='no');
      all.forEach(card=>{card.style.display='none'});
      cards.forEach((card,i)=>{card.style.display=i<visible?'':'none'});
      const remaining=Math.max(0,cards.length-visible);
      button.style.display=cards.length>limit?'block':'none';
      button.textContent=remaining
        ? 'Show 6 More ('+remaining+' remaining)'
        : 'Show Less';
      button.setAttribute('aria-expanded',String(visible>limit));
    }

    button.addEventListener('click',()=>{
      const count=Array.from(host.children)
        .filter(el=>el.classList.contains('entry')&&el.dataset.eegMatch!=='no').length;
      visible=visible>=count?limit:Math.min(count,visible+limit);
      update();
    });

    new MutationObserver(()=>update(false))
      .observe(host,{childList:true});
    window.eegRefreshDirectoryCards=window.eegRefreshDirectoryCards||function(reset){
      document.querySelectorAll('.ceu-show-toggle').forEach(btn=>{
        if(btn._eegUpdate)btn._eegUpdate(reset);
      });
    };
    button._eegUpdate=update;
    update(false);
  }

  function init(){
    ['free','paid','unknown'].forEach(setup);
  }

  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',init);
  }else{
    init();
  }
})();
</script>
<!-- CEU SIX CARD LIMIT END -->
"""

html = html.replace("</body>", feature + "\n</body>", 1)
page.write_text(html, encoding="utf-8")

print("CEU directory expansion controls installed.")

# Enhanced directory filters, personal course planner, and new EEG tech learning pathway
# Replaces only its own generated block on each daily run.
from pathlib import Path as _EnhancePath
_enhance_page = _EnhancePath('index.html')
_enhance_html = _enhance_page.read_text(encoding='utf-8')
_enhance_start = '<!-- EEG ENHANCEMENTS START -->'
_enhance_end = '<!-- EEG ENHANCEMENTS END -->'
if _enhance_start in _enhance_html and _enhance_end in _enhance_html:
    _enhance_html = _enhance_html.split(_enhance_start, 1)[0] + _enhance_html.split(_enhance_end, 1)[1]
_enhance_feature = r'''
<!-- EEG ENHANCEMENTS START -->
<style>
.eeg-enhance-panel{background:#0b2b40;color:#e9f5f8;border:1px solid #39617a;border-radius:13px;padding:18px;margin:16px 0 24px}
.eeg-enhance-panel h2,.eeg-enhance-panel h3{color:#d6f6b8;margin:0 0 9px}
.eeg-enhance-panel p{margin:7px 0 12px}
.eeg-enhance-controls{display:flex;flex-wrap:wrap;gap:12px;align-items:end}
.eeg-enhance-controls label{display:flex;flex-direction:column;gap:5px;flex:1 1 145px;font-size:14px;font-weight:600}
.eeg-enhance-controls select,.eeg-enhance-controls input,.eeg-enhance-controls button,.eeg-enhance-button{min-height:42px;box-sizing:border-box;border-radius:7px;border:1px solid #7896a6;padding:9px;background:#f8fcfd;color:#102a39;font:inherit}
.eeg-enhance-button{cursor:pointer;font-weight:700;background:#b5ef85;color:#123127}
.eeg-enhance-controls button{cursor:pointer}
.eeg-enhance-muted{color:#c3d4dd;font-size:13px}
.eeg-enhance-table{display:grid;gap:9px;margin-top:15px}
.eeg-enhance-record{background:#12374c;border:1px solid #376078;padding:12px;border-radius:9px;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.eeg-enhance-record small{display:block;color:#c4d8e3}
.eeg-enhance-progress{height:16px;border-radius:20px;background:#31516a;overflow:hidden;margin:10px 0}
.eeg-enhance-progress>div{height:100%;background:#9fe46f;width:0%;transition:width .2s}
.eeg-pathway-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:15px;margin:16px 0}
.eeg-pathway-card{border:1px solid #3b6478;border-radius:12px;padding:18px;background:#103148}
.eeg-pathway-card h3{color:#b5ef85;margin-top:0}
.eeg-pathway-card li{margin:9px 0}
.eeg-pathway-card a{color:#b5ef85}
#eeg-learning-view[hidden]{display:none!important}
@media(max-width:640px){.eeg-enhance-panel{padding:13px}.eeg-enhance-controls label{flex-basis:100%}}
</style>
<script>
(function(){
'use strict';
const KEY='eeg-ceu-course-planner-v1';
const GOAL='eeg-ceu-course-goal-v1';
const get=(k,fallback)=>{try{const v=JSON.parse(localStorage.getItem(k));return v===null?fallback:v}catch(e){return fallback}};
const put=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v));return true}catch(e){alert('Browser storage is unavailable. Export your records for safekeeping.');return false}};
const el=(tag,props={},txt)=>{const node=document.createElement(tag);Object.assign(node,props);if(txt!==undefined)node.textContent=txt;return node};
const cleanCsv=v=>{let s=String(v??'');if(/^[\s]*[=+@-]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"'};
const safeNumber=v=>{const n=Number(v);return Number.isFinite(n)&&n>=0?n:0};
function init(){
  // Filtering is applied to the same cards controlled by the six-at-a-time feature.
  const directory=document.getElementById('ceu-directory-view');
  if(directory){
    const panel=el('section',{className:'eeg-enhance-panel'});
    panel.append(el('h2',{},'Quick Filters'),el('p',{className:'eeg-enhance-muted'},'Filter existing listings. Course format and credit amounts are shown only when explicitly stated in the listing. Confirm credit eligibility with the provider.'));
    const controls=el('div',{className:'eeg-enhance-controls'});
    function choice(label,values){const wrap=el('label',{},label),sel=el('select');values.forEach(([v,t])=>sel.append(el('option',{value:v},t)));wrap.append(sel);controls.append(wrap);return sel}
    const cost=choice('Cost',[['all','Free and Paid'],['free','Free'],['paid','Paid']]);
    const format=choice('Format',[['all','Any format'],['live','Live Webinar'],['demand','On Demand']]);
    const credit=choice('Credit amount',[['all','Any amount'],['known','Specified amount'],['1','1 or more CEUs'],['2','2 or more CEUs'],['5','5 or more CEUs']]);
    const reset=el('button',{type:'button'},'Reset Filters');controls.append(reset);
    const summary=el('p',{className:'eeg-enhance-muted',id:'eeg-filter-summary'});
    panel.append(controls,summary);
    const grid=directory.querySelector('.grid');if(grid)directory.insertBefore(panel,grid);else directory.prepend(panel);
    const lists=['free','paid','unknown'].map(id=>document.getElementById(id)).filter(Boolean);
    let applying=false;
    function apply(){
      if(applying)return;applying=true;
      let matches=0;
      lists.forEach(host=>{
        const group=host.id;
        host.querySelectorAll(':scope > .entry').forEach(card=>{
          const t=card.textContent.toLowerCase();
          const category=group==='free'?'free':group==='paid'?'paid':'unknown';
          const matchCost=cost.value==='all'||cost.value===category;
          const live=/\blive\b|webinar|scheduled session/.test(t)&&!/recorded only/.test(t);
          const demand=/on[ -]?demand|self[ -]?paced|recorded|asynchronous/.test(t);
          const matchFormat=format.value==='all'||(format.value==='live'&&live)||(format.value==='demand'&&demand);
          const amounts=[...t.matchAll(/(?:\b(\d+(?:\.\d+)?)\s*(?:aset\s*)?(?:ceu|ceus|cec|cecs|credits?)\b|\b(?:ceu|ceus|cec|cecs|credits?)\s*[:=]?\s*(\d+(?:\.\d+)?))/g)].map(m=>Number(m[1]||m[2]));
          const max=amounts.length?Math.max(...amounts):null;
          const matchCredit=credit.value==='all'||(credit.value==='known'&&max!==null)||(Number(credit.value)>0&&max!==null&&max>=Number(credit.value));
          const ok=matchCost&&matchFormat&&matchCredit;
          card.dataset.eegMatch=ok?'yes':'no';if(ok)matches++;
        });
      });
      summary.textContent=matches+' matching resources. Use Show 6 More to reveal additional matches.';
      if(typeof window.eegRefreshDirectoryCards==='function')window.eegRefreshDirectoryCards(true);
      else lists.forEach(host=>host.querySelectorAll(':scope > .entry').forEach(card=>{card.style.display=card.dataset.eegMatch==='no'?'none':''}));
      applying=false;
    }
    [cost,format,credit].forEach(sel=>sel.addEventListener('change',apply));
    reset.addEventListener('click',()=>{cost.value='all';format.value='all';credit.value='all';apply()});
    lists.forEach(host=>new MutationObserver(()=>{if(!applying)apply()}).observe(host,{childList:true}));
    apply();
  }
  // A course planner complements the existing completed-course tracker without overwriting old records.
  const toolkit=document.getElementById('ceu-tools');
  if(toolkit){
    const panel=el('section',{className:'eeg-enhance-panel',id:'eeg-course-planner'});
    panel.append(el('h2',{},'My CEU Course Planner'),el('p',{className:'eeg-enhance-muted'},'Save a course, track progress, and enter earned credits after completion. Records stay in this browser. Export regularly and keep your certificates.'));
    const controls=el('div',{className:'eeg-enhance-controls'});
    function field(label,type,placeholder){const w=el('label',{},label),input=el('input',{type,placeholder:placeholder||''});w.append(input);controls.append(w);return input}
    const title=field('Course name','text','Course or webinar');title.maxLength=180;
    const provider=field('Provider','text','Optional');provider.maxLength=120;
    const statusWrap=el('label',{},'Status'),status=el('select');['Saved','In Progress','Completed'].forEach(s=>status.append(el('option',{value:s},s)));statusWrap.append(status);controls.append(statusWrap);
    const earned=field('Earned CEUs','number','0');earned.min='0';earned.max='1000';earned.step='0.25';earned.value='0';
    const add=el('button',{type:'button',className:'eeg-enhance-button'},'Save Course');controls.append(add);
    const goalRow=el('div',{className:'eeg-enhance-controls'});
    const goalLabel=el('label',{},'My recertification CEU goal'),goal=el('input',{type:'number',min:'1',max:'10000',step:'0.25',value:String(get(GOAL,30))});goalLabel.append(goal);goalRow.append(goalLabel);
    const exportBtn=el('button',{type:'button',className:'eeg-enhance-button'},'Export Planner CSV');goalRow.append(exportBtn);
    const progressText=el('p',{className:'eeg-enhance-muted'}),bar=el('div',{className:'eeg-enhance-progress'}),fill=el('div');bar.append(fill);
    const list=el('div',{className:'eeg-enhance-table'});
    panel.append(controls,goalRow,progressText,bar,list);
    const oldTracker=document.getElementById('tracker-form');
    if(oldTracker&&oldTracker.closest('.tool-panel'))oldTracker.closest('.tool-panel').before(panel);else toolkit.append(panel);
    function records(){return get(KEY,[])}
    function render(){
      const rows=records();list.replaceChildren();
      const total=rows.filter(r=>r.status==='Completed').reduce((n,r)=>n+safeNumber(r.credits),0);
      const target=Math.max(1,safeNumber(goal.value)||30);
      progressText.textContent=total.toFixed(2)+' of '+target+' CEUs earned ('+Math.min(100,Math.round(total/target*100))+'%). Only completed courses count.';
      fill.style.width=Math.min(100,total/target*100)+'%';
      if(!rows.length)list.append(el('p',{className:'eeg-enhance-muted'},'No courses saved yet.'));
      rows.forEach(r=>{
        const row=el('div',{className:'eeg-enhance-record'}),details=el('div');details.append(el('strong',{},r.title),el('small',{},(r.provider||'Provider not entered')+' · '+r.status+' · '+safeNumber(r.credits)+' earned CEUs'));
        const buttons=el('div',{className:'eeg-enhance-controls'}),state=el('select');['Saved','In Progress','Completed'].forEach(s=>state.append(el('option',{value:s},s)));state.value=r.status;
        state.setAttribute('aria-label','Status for '+r.title);
        state.addEventListener('change',()=>{const data=records(),item=data.find(x=>x.id===r.id);if(item){item.status=state.value;put(KEY,data);render()}});
        const edit=el('button',{type:'button'},'Edit CEUs');edit.addEventListener('click',()=>{const v=prompt('Earned CEUs for '+r.title,String(r.credits));if(v===null)return;const n=Number(v);if(!Number.isFinite(n)||n<0||n>1000){alert('Enter a valid CEU amount.');return}const data=records(),item=data.find(x=>x.id===r.id);if(item){item.credits=n;put(KEY,data);render()}});
        const remove=el('button',{type:'button'},'Remove');remove.addEventListener('click',()=>{if(!confirm('Remove '+r.title+'?'))return;put(KEY,records().filter(x=>x.id!==r.id));render()});
        buttons.append(state,edit,remove);row.append(details,buttons);list.append(row);
      });
    }
    add.addEventListener('click',()=>{
      const name=title.value.trim();if(!name){alert('Enter a course name.');title.focus();return}
      const n=Number(earned.value);if(!Number.isFinite(n)||n<0||n>1000){alert('Enter a valid earned CEU amount.');return}
      const data=records();data.push({id:Date.now()+'-'+Math.random().toString(36).slice(2),title:name,provider:provider.value.trim(),status:status.value,credits:n});
      if(put(KEY,data)){title.value='';provider.value='';status.value='Saved';earned.value='0';render()}
    });
    goal.addEventListener('change',()=>{const n=Number(goal.value);if(n>0&&n<=10000){put(GOAL,n);render()}else{alert('Enter a valid goal.');goal.value=String(get(GOAL,30))}});
    exportBtn.addEventListener('click',()=>{
      const rows=[['Course','Provider','Status','Earned CEUs'],...records().map(r=>[r.title,r.provider,r.status,r.credits])];
      const csv=rows.map(row=>row.map(cleanCsv).join(',')).join('\r\n');
      const url=URL.createObjectURL(new Blob(['\ufeff'+csv],{type:'text/csv;charset=utf-8'}));
      const link=el('a',{href:url,download:'eeg-ceu-course-planner.csv'});document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
    });
    window.eegSaveCourse=function(name,providerName){title.value=name;provider.value=providerName||'';status.value='Saved';earned.value='0';add.click()};
    render();
  }
  // Learning pathway is a dedicated navigation tab, not a credit-bearing course catalog.
  const nav=document.querySelector('.ceu-tabs');
  if(nav){
    const tab=el('button',{type:'button',className:'ceu-tab',dataset:{view:'learning'},textContent:'New EEG Tech Pathway'});
    tab.setAttribute('aria-pressed','false');nav.append(tab);
    const view=el('main',{className:'ceu-view',id:'eeg-learning-view',hidden:true});
    const intro=el('section',{className:'eeg-enhance-panel'});
    intro.append(el('h2',{},'New EEG Tech Learning Pathway'),el('p',{},'A progressive learning guide from foundational EEG skills to advanced clinical interpretation. These links are educational resources; CEU credit is not guaranteed. Follow your department training, supervision, and competency requirements.'));
    const grid=el('div',{className:'eeg-pathway-grid'});
    const levels=[
      {name:'Beginner',topics:[['Electrode placement and the 10–20 system','https://www.acns.org/practice/guidelines'],['EEG fundamentals and terminology','https://www.learningeeg.com/'],['Recognizing common artifacts','https://eegpedia.org/index.php?title=Main_Page']]},
      {name:'Intermediate',topics:[['Normal variants and sleep patterns','https://www.learningeeg.com/'],['Seizure patterns and EEG interpretation','https://eegatlas-online.com/index.php/en/'],['Practice with clinical EEG examples','https://eegpedia.org/index.php?title=Main_Page']]},
      {name:'Advanced',topics:[['ICU EEG and critical care monitoring','https://www.acns.org/practice/guidelines'],['Continuous EEG and seizure terminology','https://www.acns.org/practice/guidelines'],['Advanced seizure and epilepsy education','https://www.ilae.org/education']]}
    ];
    levels.forEach(level=>{
      const card=el('section',{className:'eeg-pathway-card'});card.append(el('h3',{},level.name));
      const ul=el('ul');level.topics.forEach(([topic,url])=>{const li=el('li'),a=el('a',{href:url,target:'_blank',rel:'noopener noreferrer'},topic+' ↗');li.append(a);ul.append(li)});card.append(ul);grid.append(card)
    });intro.append(grid,el('p',{className:'eeg-enhance-muted'},'Suggested sequence only. Source pages may contain a mix of introductory and advanced material. Confirm individual course availability and credit status.'));view.append(intro);
    const directory=document.getElementById('ceu-directory-view');if(directory)directory.after(view);else nav.after(view);
    function showLearning(){
      document.querySelectorAll('.ceu-view,.tools-shell').forEach(v=>{v.hidden=v===view?false:true});
      nav.querySelectorAll('.ceu-tab').forEach(t=>{const active=t===tab;t.classList.toggle('active',active);t.setAttribute('aria-pressed',String(active))});
    }
    tab.addEventListener('click',e=>{e.stopImmediatePropagation();showLearning()},true);
    nav.querySelectorAll('.ceu-tab:not([data-view="learning"])').forEach(t=>t.addEventListener('click',()=>{view.hidden=true},true));
  }
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
</script>
<!-- EEG ENHANCEMENTS END -->
'''
_enhance_html = _enhance_html.replace('</body>', _enhance_feature + '\n</body>', 1)
_enhance_page.write_text(_enhance_html, encoding='utf-8')
print('Quick filters, course planner, and EEG learning pathway installed.')
