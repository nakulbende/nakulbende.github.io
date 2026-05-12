import os
import glob
import random
import json
from datetime import datetime
from bs4 import BeautifulSoup

# =========================================================
# CONFIGURATION
# =========================================================
ROOT_DIR = "."
SITE_URL = "https://nakulbende.github.io"
FONT_URL = "https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,600&family=Poppins:ital,wght@0,300;0,400;0,500;0,600&family=Raleway:ital,wght@0,300;0,400;0,500;0,600&display=swap"
PROFILE_IMAGE = f"{SITE_URL}/assets/img/profile-img.jpg"

# ---> CHANGE YOUR JOB TITLE HERE <---
# This text will be propagated to the header of all pages automatically.
JOB_TAGLINE = "Fusion Materials Engineer @ CFS" 

IGNORE_DIRS = {".git", "venv", "__pycache__", "node_modules", "assets"}

# =========================================================
# PAGE-SPECIFIC SEO
# =========================================================
PAGE_METADATA = {
    "index.html": {
        "title": "Nakul Bende, PhD | Fusion Materials Engineer & Polymer Scientist",
        "description": "Portfolio of Nakul Bende, PhD — fusion materials engineer, polymer scientist, and multidisciplinary leader specializing in advanced materials, additive manufacturing and scientific visualization."
    },
    "photography.html": {
        "title": "Photography Portfolio | Nakul Bende",
        "description": "Landscape, travel, astrophotography, and experimental photography by Nakul Bende."
    },
    "hydrogel.html": {
        "title": "DLP Micro-Lithography Research | Nakul Bende",
        "description": "Research in hydrogel micro-lithography, programmable materials, and photopolymer fabrication systems."
    },
    "bendyshells.html": {
        "title": "Programming Shell Instabilities | Nakul Bende",
        "description": "Research into shell mechanics, instability programming, soft matter physics, and responsive polymer structures."
    },
    "astrotracker.html": {
        "title": "DIY Equatorial Astrotracker | Nakul Bende",
        "description": "Custom-built equatorial tracking mount for astrophotography and long-exposure night sky imaging."
    },
    "commute.html": {
        "title": "Commute Analytics Bot | Nakul Bende",
        "description": "Python-based commute logging, analytics, visualization, and optimization system."
    },
    "nes.html": {
        "title": "RaspberryPi NES Emulator | Nakul Bende",
        "description": "DIY 3D printed Nintendo Entertainment System (NES) emulator and media server powered by Raspberry Pi, RetroPie, and Kodi."
    },
    "eufy.html": {
        "title": "Smartify Vacuum with ESP32 | Nakul Bende",
        "description": "Hardware modification using an ESP32 to convert an unconnected robot vacuum cleaner into a smart home integrated device."
    },
    "cutthroatkitcken.html": {
        "title": "Cutthroat Kitchen Data Visualization | Nakul Bende",
        "description": "Data mining and visualization of winnings, spending, and contestant strategies in the TV show Cutthroat Kitchen."
    },
    "fireplace.html": {
        "title": "Hogwarts Fireplace Installation | Nakul Bende",
        "description": "Custom 3D printed Hogwarts castle fireplace installation and home DIY project."
    },
    "bhutan.html": {
        "title": "Bhutan Travel Photography | Nakul Bende",
        "description": "Travel photography and cultural exploration from the Kingdom of Bhutan (2013)."
    },
    "hawaii.html": {
        "title": "Hawaii Landscape Photography | Nakul Bende",
        "description": "Landscape and nature photography from the Big Island, Hawaii (2021)."
    },
    "kerala.html": {
        "title": "Kerala Travel Photography | Nakul Bende",
        "description": "Travel photography from God's Own Country: Kerala, India (2015 and 2019)."
    },
    "sarpass.html": {
        "title": "Sarpass Himalayas Trek | Nakul Bende",
        "description": "High-altitude landscape photography from a 14,000 ft trek in the Himalayas."
    },
    "outreach.html": {
        "title": "STEAM Outreach & Education | Nakul Bende",
        "description": "A decade of STEAM outreach, organizing educational modules in schools, museums, and universities."
    }
}

# =========================================================
# ALT TEXT MAPPING
# =========================================================
ALT_KEYWORDS = {
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

# =========================================================
# HELPERS
# =========================================================

def relative_url(path):
    """
    Converts an absolute or deep file path into a clean relative path 
    from the root directory. Also standardizes slashes for web URLs.
    """
    rel = os.path.relpath(path, ROOT_DIR)
    return rel.replace("\\", "/")

def page_url(path):
    """
    Constructs the full canonical URL for a given file path by combining
    the SITE_URL configuration with the file's relative path.
    """
    rel = relative_url(path)
    if rel == "index.html":
        return SITE_URL + "/"
    return f"{SITE_URL}/{rel.lstrip('/')}"

def is_portfolio_image(img):
    """
    Detects if an image tag is located inside your Isotope portfolio grid.
    This is critical because lazy-loading grid images often breaks the Isotope 
    layout calculation. Returns True if the image is in the grid.
    """
    parent = img.parent
    while parent:
        classes = parent.get("class", [])
        if any(c in classes for c in ["portfolio-item", "portfolio-wrap", "portfolio-links"]):
            return True
        parent = parent.parent
    return False

def clean_head_section(soup):
    """
    Strips out duplicate or outdated viewport, charset, and Google Font tags 
    from the <head> section to prevent clutter before injecting fresh SEO tags.
    """
    if not soup.head: return
    for tag in soup.find_all('meta', attrs={'name': 'viewport'})[1:]: tag.decompose()
    for tag in soup.find_all('meta', charset=True)[1:]: tag.decompose()
    for link in soup.find_all('link', href=True):
        if "fonts.googleapis.com" in link['href'] or "fonts.gstatic.com" in link['href']:
            link.decompose()

def inject_seo(soup, file_path):
    """
    The main SEO engine. Looks up the specific file in PAGE_METADATA to inject 
    custom <title> and <meta description> tags. It also generates OpenGraph 
    tags for social sharing (LinkedIn/Twitter), canonical links, and Schema.org 
    JSON-LD data to help Google understand the page contents.
    """
    filename = os.path.basename(file_path)
    default_title = f"{filename.replace('.html', '').replace('_', ' ').title()} | Nakul Bende"
    meta_data = PAGE_METADATA.get(filename, {
        "title": default_title if filename != "index.html" else "Nakul Bende | Portfolio",
        "description": "Project portfolio page by Nakul Bende."
    })
    
    page_title = meta_data["title"]
    desc_content = meta_data["description"]
    url = page_url(file_path)

    # 1. Title
    if soup.title:
        soup.title.string = page_title
    else:
        new_title = soup.new_tag('title')
        new_title.string = page_title
        soup.head.insert(0, new_title)

    # 2. Meta Tags
    meta_configs = [
        ("name", "description", desc_content),
        ("name", "author", "Nakul Bende"),
        ("name", "theme-color", "#0f172a"),
        ("property", "og:title", page_title),
        ("property", "og:description", desc_content),
        ("property", "og:url", url),
        ("property", "og:type", "website"),
        ("property", "og:image", PROFILE_IMAGE)
    ]

    for attr, val, content in meta_configs:
        tag = soup.find('meta', attrs={attr: val})
        if tag:
            tag['content'] = content
        else:
            new_meta = soup.new_tag('meta', content=content)
            new_meta[attr] = val
            soup.head.append(new_meta)

    # 3. Canonical Link
    for tag in soup.find_all("link", rel="canonical"): tag.decompose()
    canonical = soup.new_tag("link", rel="canonical", href=url)
    soup.head.append(canonical)

    # 4. Schema JSON-LD
    for s in soup.find_all('script', type='application/ld+json'): s.decompose()
    schema = [
        {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": "Nakul Bende",
            "url": SITE_URL,
            "image": PROFILE_IMAGE,
            "jobTitle": JOB_TAGLINE.split("@")[0].strip() if "@" in JOB_TAGLINE else JOB_TAGLINE,
            "description": desc_content,
            "sameAs": [
                "https://github.com/nakulbende",
                "https://www.linkedin.com/in/nakulbende"
            ]
        },
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Nakul Bende",
            "url": SITE_URL
        }
    ]
    schema_tag = soup.new_tag('script', type='application/ld+json')
    schema_tag.string = json.dumps(schema, indent=2)
    soup.head.append(schema_tag)

def update_swiper_blocks_in_soup(soup, directory):
    """
    Finds the Swiper.js wrapper inside a portfolio page, reads all available 
    images in that specific project's asset folder, shuffles them randomly, 
    and dynamically builds the HTML required to populate the slider.
    """
    img_path = os.path.join(directory, 'assets', 'img')
    if not os.path.exists(img_path): return
    
    files = glob.glob(os.path.join(img_path, '*.png')) + glob.glob(os.path.join(img_path, '*.jpg'))
    if not files: return
    random.shuffle(files)
    
    wrapper = soup.find('div', class_='swiper-wrapper')
    if wrapper:
        wrapper.clear() # Clear out the old images safely
        for f in files:
            rel_path = os.path.relpath(f, directory).replace("\\", "/")
            
            # Build <div class="swiper-slide"><img src="..." class="img-fluid" loading="lazy"></div>
            slide = soup.new_tag('div', attrs={'class': 'swiper-slide'})
            img = soup.new_tag('img', src=rel_path, alt="Portfolio Image", loading="lazy")
            img['class'] = ['img-fluid']
            slide.append(img)
            wrapper.append(slide)

def update_job_tagline(soup):
    """
    Updates the text of the job tagline in the header across all pages.
    Assumes the structural standardization has already occurred.
    """
    header = soup.find("header", id="header")
    if not header:
        return
    
    tagline_p = header.find("p", class_="tagline")
    if tagline_p:
        a_tag = tagline_p.find("a")
        if a_tag:
            a_tag.string = JOB_TAGLINE

def optimize_dom(soup, file_path):
    """
    Scans the HTML body to optimize UI elements:
    1. Injects relevant alt text for accessibility and image SEO.
    2. Enforces responsive image classes (img-fluid).
    3. Handles lazy vs eager loading to improve PageSpeed scores.
    4. Secures external target="_blank" links with noopener tags.
    """
    path_lower = file_path.lower()
    alt_base = "Nakul Bende Portfolio Image"
    
    for key, val in ALT_KEYWORDS.items():
        if key in path_lower:
            alt_base = val
            break

    # Fix Images
    for img in soup.find_all('img'):
        if not img.has_attr('alt') or img['alt'].strip() == "" or img['alt'] == "Nakul Bende Portfolio Image":
            img['alt'] = alt_base
            
        classes = img.get('class', [])
        if 'img-fluid' not in classes:
            classes.append('img-fluid')
            img['class'] = classes

        src = img.get('src', '')
        if 'profile-img' in src:
            img['loading'] = 'eager'
            img['fetchpriority'] = 'high'
        elif is_portfolio_image(img):
            if img.has_attr('loading'):
                del img['loading'] # Strip lazy loading so Isotope Grid calculates correctly
        else:
            img['loading'] = 'lazy'

    # Secure Scripts (Ensures core scripts are NOT deferred to protect your UI)
    for script in soup.find_all('script', src=True):
        src = script['src']
        if all(x not in src for x in ["googletagmanager", "bootstrap.bundle.min.js", "main.js", "isotope.pkgd.min.js"]):
            if not script.has_attr('defer'):
                script['defer'] = None

    # Fix target blanks
    for a in soup.find_all('a', target="_blank"):
        a['rel'] = "noopener noreferrer"

def optimize_html(file_path):
    """
    The master function for processing a single HTML file. It opens the file, 
    parses it into a DOM tree, runs it through all the helper functions, 
    re-injects required external assets, and writes it back to the disk.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        # lxml is significantly more robust than html.parser and won't delete broken DOMs
        soup = BeautifulSoup(f.read(), 'lxml')
    
    clean_head_section(soup)
    inject_seo(soup, file_path)
    update_job_tagline(soup) 
    optimize_dom(soup, file_path)
    update_swiper_blocks_in_soup(soup, os.path.dirname(file_path))

    # Re-inject clean Google Fonts
    font_link = soup.new_tag('link', rel='stylesheet', href=FONT_URL)
    preconnect = soup.new_tag('link', rel='preconnect', href='https://fonts.gstatic.com', crossorigin='')
    dns_hint = soup.new_tag('link', rel='dns-prefetch', href='https://fonts.gstatic.com')
    soup.head.append(dns_hint)
    soup.head.append(preconnect)
    soup.head.append(font_link)

    # Safe writing mechanism to preserve formatting
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
        
    print(f"✨ Successfully Optimized & Preserved: {file_path}")

def generate_sitemap_and_robots(html_files):
    """
    Generates the sitemap.xml and robots.txt files required for search engines.
    It automatically excludes templates and hidden forms, assigns crawling priority 
    based on page depth, and updates the 'lastmod' timestamp dynamically.
    """
    sitemap_path = os.path.join(ROOT_DIR, "sitemap.xml")
    urls = []

    for file_path in html_files:
        rel = relative_url(file_path)
        
        # Exclusions: Skip forms, and skip the portfolio template file so Google ignores it
        if rel.startswith("forms/") or "TEMPLATE" in rel: 
            continue
        
        url = page_url(file_path)
        priority = "1.0" if rel == "index.html" else "0.8" if "portfolio" in rel else "0.7"
        
        # W3C Datetime formatting for better SEO tracking
        ts = os.path.getmtime(file_path)
        lastmod = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%S+00:00")

        urls.append(f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{priority}</priority>\n  </url>")

    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{"".join(urls)}\n</urlset>'
    
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(xml)
    print("✓ Generated optimized sitemap.xml")

    # Build Robots.txt string, adding block rules for templates and heavy assets
    robots = f"""User-agent: *
Allow: /
Disallow: /forms/
Disallow: /portfolio/TEMPLATE/
Disallow: /assets/vendor/

Sitemap: {SITE_URL}/sitemap.xml
"""
    with open("robots.txt", "w", encoding="utf-8") as f:
        f.write(robots)
    print("✓ Generated optimized robots.txt")

if __name__ == "__main__":
    html_files = []
    
    # Process files recursively through the directory structure
    for subdir, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(subdir, file)
                html_files.append(file_path)
                optimize_html(file_path)

    # Generate meta files at the very end
    generate_sitemap_and_robots(html_files)
    
    print("\n✅ Run complete. Your layout is completely protected and updated.")