import os
import json
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# =========================================================
# PATH & GLOBAL CONFIGURATION
# =========================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

JSON_FILE = os.path.join(ROOT_DIR, "site_meta.json")
IGNORE_DIRS = {".git", "venv", "__pycache__", "node_modules", "assets", "python"}
FONT_URL = "https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,600&family=Poppins:ital,wght@0,300;0,400;0,500;0,600&family=Raleway:ital,wght@0,300;0,400;0,500;0,600&display=swap"

# Initial seed datasets for dynamic JSON creation
ORIGINAL_METADATA = {
    "index.html": {"title": "Nakul Bende, PhD | Fusion Materials Engineer & Polymer Scientist", "description": "Portfolio of Nakul Bende, PhD — fusion materials engineer, polymer scientist, and multidisciplinary leader specializing in advanced materials, additive manufacturing and scientific visualization."},
    "photography.html": {"title": "Photography Portfolio | Nakul Bende", "description": "Landscape, travel, astrophotography, and experimental photography by Nakul Bende."},
    "hydrogel.html": {"title": "DLP Micro-Lithography Research | Nakul Bende", "description": "Research in hydrogel micro-lithography, programmable materials, and photopolymer fabrication systems."},
    "bendyshells.html": {"title": "Programming Shell Instabilities | Nakul Bende", "description": "Research into shell mechanics, instability programming, soft matter physics, and responsive polymer structures."},
    "astrotracker.html": {"title": "DIY Equatorial Astrotracker | Nakul Bende", "description": "Custom-built equatorial tracking mount for astrophotography and long-exposure night sky imaging."},
    "commute.html": {"title": "Commute Analytics Bot | Nakul Bende", "description": "Python-based commute logging, analytics, visualization, and optimization system."},
    "nes.html": {"title": "RaspberryPi NES Emulator | Nakul Bende", "description": "DIY 3D printed Nintendo Entertainment System (NES) emulator and media server powered by Raspberry Pi, RetroPie, and Kodi."},
    "eufy.html": {"title": "Smartify Vacuum with ESP32 | Nakul Bende", "description": "Hardware modification using an ESP32 to convert an unconnected robot vacuum cleaner into a smart home integrated device."},
    "cutthroatkitcken.html": {"title": "Cutthroat Kitchen Data Visualization | Nakul Bende", "description": "Data mining and visualization of winnings, spending, and contestant strategies in the TV show Cutthroat Kitchen."},
    "fireplace.html": {"title": "Hogwarts Fireplace Installation | Nakul Bende", "description": "Custom 3D printed Hogwarts castle fireplace installation and home DIY project."},
    "bhutan.html": {"title": "Bhutan Travel Photography | Nakul Bende", "description": "Travel photography and cultural exploration from the Kingdom of Bhutan (2013)."},
    "hawaii.html": {"title": "Hawaii Landscape Photography | Nakul Bende", "description": "Landscape and nature photography from the Big Island, Hawaii (2021)."},
    "kerala.html": {"title": "Kerala Travel Photography | Nakul Bende", "description": "Travel photography from God's Own Country: Kerala, India (2015 and 2019)."},
    "sarpass.html": {"title": "Sarpass Himalayas Trek | Nakul Bende", "description": "High-altitude landscape photography from a 14,000 ft trek in the Himalayas."},
    "outreach.html": {"title": "STEAM Outreach & Education | Nakul Bende", "description": "A decade of STEAM outreach, organizing educational modules in schools, museums, and universities."}
}

ORIGINAL_ALTS = {
    "sarpass": "Sarpass Himalayas mountain landscape photography",
    "bhutan": "Bhutan travel and cultural photography",
    "hawaii": "Big Island Hawaii landscape photography",
    "kerala": "Kerala India travel photography",
    "hydrogel": "Hydrogel micro-lithography experiment",
    "bendyshells": "Programmable shell instability experiment",
    "astrotracker": "DIY equatorial astrotracker mount",
    "commute": "Commute analytics and visualization dashboard",
    "outreach": "STEM outreach and science education activities",
    "eufy": "ESP32 smart vacuum hardware modification",
    "fireplace": "3D printed Hogwarts fireplace installation",
    "nes": "3D printed Raspberry Pi NES emulator and media center",
    "cutthroatkitcken": "Data visualization of Cutthroat Kitchen TV show"
}

def get_html_files():
    """Recursively crawls website root directory for valid HTML files."""
    html_files = []
    for subdir, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(subdir, file))
    return html_files

def save_data(data):
    """Persists global settings and SEO metadata to JSON state file."""
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_data():
    """Loads state from JSON or seeds initial values from original dictionaries."""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    files = get_html_files()
    data = {
        "global": {
            "job_tagline": "Fusion Materials Engineer @ CFS",
            "site_url": "https://nakulbende.github.io",
            "profile_image_path": "/assets/img/profile-img.jpg"
        },
        "pages": {}
    }

    for fp in files:
        rel = os.path.relpath(fp, ROOT_DIR).replace("\\", "/")
        if rel.startswith("forms/") or "TEMPLATE" in rel:
            continue
            
        filename = os.path.basename(fp)
        name_key = filename.replace(".html", "").lower()
        
        meta = ORIGINAL_METADATA.get(filename, {
            "title": f"{filename.replace('.html', '').title()} | Nakul Bende",
            "description": f"Portfolio page for {filename.replace('.html', '').title()}."
        })
        
        alt_text = "Nakul Bende Portfolio Image"
        for k, v in ORIGINAL_ALTS.items():
            if k in name_key:
                alt_text = v
                break
                
        data["pages"][rel] = {
            "title": meta["title"],
            "description": meta["description"],
            "alt_keyword": alt_text
        }
        
    save_data(data)
    return data

def relative_url(path):
    return os.path.relpath(path, ROOT_DIR).replace("\\", "/")

def page_url(path, site_url):
    rel = relative_url(path)
    return site_url + "/" if rel == "index.html" else f"{site_url}/{rel.lstrip('/')}"

def clean_head_section(soup):
    """Strips redundant viewport/font declarations to prevent head bloat."""
    if not soup.head: return
    for tag in soup.find_all('meta', attrs={'name': 'viewport'})[1:]: tag.decompose()
    for tag in soup.find_all('meta', charset=True)[1:]: tag.decompose()
    for link in soup.find_all('link', href=True):
        if "fonts.googleapis.com" in link['href'] or "fonts.gstatic.com" in link['href']:
            link.decompose()

def inject_seo(soup, file_path, page_data, global_data):
    """Injects dynamic page titles, descriptions, OpenGraph tags, and Schema.org structures."""
    page_title = page_data["title"]
    desc_content = page_data["description"]
    site_url = global_data["site_url"].rstrip('/')
    full_profile_img = f"{site_url}{global_data['profile_image_path']}"
    url = page_url(file_path, site_url)
    job_tag = global_data["job_tagline"]

    if soup.title:
        soup.title.string = page_title
    else:
        new_title = soup.new_tag('title')
        new_title.string = page_title
        soup.head.insert(0, new_title)

    meta_configs = [
        ("name", "description", desc_content),
        ("name", "author", "Nakul Bende"),
        ("name", "theme-color", "#0f172a"),
        ("property", "og:title", page_title),
        ("property", "og:description", desc_content),
        ("property", "og:url", url),
        ("property", "og:type", "website"),
        ("property", "og:image", full_profile_img)
    ]

    for attr, val, content in meta_configs:
        tag = soup.find('meta', attrs={attr: val})
        if tag: tag['content'] = content
        else:
            new_meta = soup.new_tag('meta', content=content)
            new_meta[attr] = val
            soup.head.append(new_meta)

    for tag in soup.find_all("link", rel="canonical"): tag.decompose()
    soup.head.append(soup.new_tag("link", rel="canonical", href=url))

    for s in soup.find_all('script', type='application/ld+json'): s.decompose()
    schema = [
        {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": "Nakul Bende",
            "url": site_url,
            "image": full_profile_img,
            "jobTitle": job_tag.split("@")[0].strip() if "@" in job_tag else job_tag,
            "description": desc_content,
            "sameAs": ["https://github.com/nakulbende", "https://www.linkedin.com/in/nakulbende"]
        },
        {"@context": "https://schema.org", "@type": "WebSite", "name": "Nakul Bende", "url": site_url}
    ]
    schema_tag = soup.new_tag('script', type='application/ld+json')
    schema_tag.string = json.dumps(schema, indent=2)
    soup.head.append(schema_tag)

def update_job_tagline(soup, job_tag):
    """Updates header job tagline globally across pages."""
    header = soup.find("header", id="header")
    if header and (tagline_p := header.find("p", class_="tagline")) and (a_tag := tagline_p.find("a")):
        a_tag.string = job_tag

def optimize_dom(soup, page_data):
    """Enforces responsive image classes and prevents lazy loading bugs on gallery grid items."""
    alt_base = page_data["alt_keyword"]
    
    for img in soup.find_all('img'):
        if not img.has_attr('alt') or img['alt'].strip() == "" or img['alt'] == "Nakul Bende Portfolio Image":
            img['alt'] = alt_base
            
        classes = img.get('class', [])
        if 'img-fluid' not in classes:
            classes.append('img-fluid')
            img['class'] = classes

        in_gallery = False
        parent = img.parent
        while parent:
            if parent.get("id") == "my-portfolio":
                in_gallery = True
                break
            parent = parent.parent

        src = img.get('src', '')
        if 'profile-img' in src:
            img['loading'] = 'eager'
            img['fetchpriority'] = 'high'
        elif in_gallery:
            if img.has_attr('loading'): del img['loading']
        else:
            img['loading'] = 'lazy'

    for script in soup.find_all('script', src=True):
        src = script['src']
        if all(x not in src for x in ["googletagmanager", "bootstrap.bundle.min.js", "main.js", "isotope.pkgd.min.js"]):
            if not script.has_attr('defer'): script['defer'] = None

    for a in soup.find_all('a', target="_blank"):
        a['rel'] = "noopener noreferrer"

def generate_sitemap_and_robots(html_files, site_url):
    """Rebuilds sitemap.xml and robots.txt in the root directory."""
    site_url = site_url.rstrip('/')
    sitemap_path = os.path.join(ROOT_DIR, "sitemap.xml")
    robots_path = os.path.join(ROOT_DIR, "robots.txt")
    urls = []
    
    for file_path in html_files:
        rel = relative_url(file_path)
        if rel.startswith("forms/") or "TEMPLATE" in rel: continue
        
        url = page_url(file_path, site_url)
        priority = "1.0" if rel == "index.html" else "0.8" if "portfolio" in rel else "0.7"
        ts = os.path.getmtime(file_path)
        lastmod = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        urls.append(f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{priority}</priority>\n  </url>")

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{"".join(urls)}\n</urlset>')

    with open(robots_path, "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nDisallow: /forms/\nDisallow: /portfolio/TEMPLATE/\nDisallow: /assets/vendor/\n\nSitemap: {site_url}/sitemap.xml\n")

# =========================================================
# FLASK CONTROL PANEL SERVER
# =========================================================
@app.route('/')
def index():
    data = load_data()
    return render_template_string(HTML_TEMPLATE, data=data)

@app.route('/propagate', methods=['POST'])
def propagate():
    payload = request.json
    save_data(payload)
    
    files = get_html_files()
    processed_count = 0
    
    for fp in files:
        rel = relative_url(fp)
        if rel not in payload["pages"]: continue
        
        with open(fp, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
            
        clean_head_section(soup)
        inject_seo(soup, fp, payload["pages"][rel], payload["global"])
        update_job_tagline(soup, payload["global"]["job_tagline"])
        optimize_dom(soup, payload["pages"][rel])
        
        soup.head.append(soup.new_tag('link', rel='dns-prefetch', href='https://fonts.gstatic.com'))
        soup.head.append(soup.new_tag('link', rel='preconnect', href='https://fonts.gstatic.com', crossorigin=''))
        soup.head.append(soup.new_tag('link', rel='stylesheet', href=FONT_URL))

        with open(fp, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        processed_count += 1
            
    generate_sitemap_and_robots(files, payload["global"]["site_url"])
    return jsonify({"status": "success", "message": f"Successfully optimized {processed_count} pages and rebuilt sitemap!"})

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Site SEO Manager</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 1000px; margin: 30px auto; background: #f8fafc; color: #0f172a; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;}
        .global-panel { background: #ffffff; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.05); display: grid; grid-template-columns: 1fr 1fr; gap: 16px;}
        .global-panel .full-width { grid-column: span 2; }
        button { background: #0f172a; color: #fff; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 15px; font-weight: 600;}
        button:hover { background: #334155; }
        .page-card { background: #ffffff; padding: 20px; margin-bottom: 16px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.04);}
        .page-title { font-weight: 600; font-size: 16px; margin-bottom: 12px; color: #3b82f6; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px;}
        .form-group { margin-bottom: 12px; }
        label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 4px; color: #475569;}
        input[type="text"], textarea { width: 100%; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-family: inherit; font-size: 14px; box-sizing: border-box;}
        textarea { resize: vertical; height: 60px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Global SEO & Site Manager</h2>
        <button onclick="propagateData()">Save & Propagate Changes</button>
    </div>
    
    <div class="global-panel">
        <div class="form-group full-width">
            <label>Global Job Tagline (Sidebar/Header)</label>
            <input type="text" id="global-job" value="{{ data.global.job_tagline }}">
        </div>
        <div class="form-group">
            <label>Site URL</label>
            <input type="text" id="global-url" value="{{ data.global.site_url }}">
        </div>
        <div class="form-group">
            <label>Profile Image Path</label>
            <input type="text" id="global-profile" value="{{ data.global.profile_image_path }}">
        </div>
    </div>

    <div id="pages-list">
        {% for rel_path, page_data in data.pages.items() %}
        <div class="page-card" data-path="{{ rel_path }}">
            <div class="page-title">{{ rel_path }}</div>
            <div class="form-group">
                <label>Page Title (&lt;title&gt;)</label>
                <input type="text" class="input-title" value="{{ page_data.title }}">
            </div>
            <div class="form-group">
                <label>Meta Description</label>
                <textarea class="input-desc">{{ page_data.description }}</textarea>
            </div>
            <div class="form-group">
                <label>Image Alt-Text Keyword (Fallback)</label>
                <input type="text" class="input-alt" value="{{ page_data.alt_keyword }}">
            </div>
        </div>
        {% endfor %}
    </div>

    <script>
        async function propagateData() {
            const btn = document.querySelector('button');
            btn.innerText = "Processing...";
            
            const payload = {
                global: { 
                    job_tagline: document.getElementById('global-job').value,
                    site_url: document.getElementById('global-url').value,
                    profile_image_path: document.getElementById('global-profile').value
                },
                pages: {}
            };
            
            document.querySelectorAll('.page-card').forEach(card => {
                payload.pages[card.dataset.path] = {
                    title: card.querySelector('.input-title').value,
                    description: card.querySelector('.input-desc').value,
                    alt_keyword: card.querySelector('.input-alt').value
                };
            });

            const response = await fetch('/propagate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            alert(result.message);
            btn.innerText = "Save & Propagate Changes";
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("Starting SEO & Site Manager...")
    print("Navigate to http://127.0.0.1:5001 in your browser.")
    app.run(debug=False, port=5001)