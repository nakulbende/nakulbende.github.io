import os
import glob
import random
import json
from bs4 import BeautifulSoup

# --- Configuration ---
ROOT_DIR = "."
SITE_URL = "https://nakulbende.github.io/"
FONT_URL = "https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,600&family=Poppins:ital,wght@0,300;0,400;0,500;0,600&family=Raleway:ital,wght@0,300;0,400;0,500;0,600&display=swap"

def inject_seo(soup, file_path, is_index=False):
    """Injects JSON-LD, Meta Tags, Open Graph, and Accessibility hints."""
    modified = False
    page_title = "Nakul Bende | Staff Materials Engineer" if is_index else f"Project | Nakul Bende"
    
    # 1. Update Title Tag
    if soup.title:
        if soup.title.string != page_title:
            soup.title.string = page_title
            modified = True
    else:
        new_title = soup.new_tag('title')
        new_title.string = page_title
        soup.head.append(new_title)
        modified = True

    # 2. Meta Description & Open Graph (Social Media)
    desc_content = "Fusion Materials Scientist engineering resilient solutions for humanity's most critical challenges. Expert in polymers, data-driven formulation + material qualification, and scientific visualization."
    
    meta_map = {
        "description": desc_content,
        "og:title": page_title,
        "og:description": desc_content,
        "og:url": SITE_URL,
        "og:type": "website",
        "og:image": f"{SITE_URL}assets/img/profile-img.jpg",
        "twitter:card": "summary_large_image"
    }

    for name, content in meta_map.items():
        attr = "property" if name.startswith("og:") else "name"
        if not soup.find('meta', attrs={attr: name}):
            tag = soup.new_tag('meta', content=content)
            tag[attr] = name
            soup.head.append(tag)
            modified = True

    # 3. JSON-LD Schema (The "Hard Tech" version)
    if is_index:
        schema = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": "Nakul Bende",
            "url": SITE_URL,
            "jobTitle": "Staff Materials Engineer",
            "worksFor": [
                {"@type": "Organization", "name": "Commonwealth Fusion Systems (CFS)"},
                {"@type": "Organization", "name": "Formlabs"},
                {"@type": "Organization", "name": "PolyOne (Avient)"},
                {"@type": "Organization", "name": "University of Massachusetts Amherst"}
            ],
            "alumniOf": [
                {"@type": "CollegeOrUniversity", "name": "University of Massachusetts Amherst"},
                {"@type": "CollegeOrUniversity", "name": "Indian Institute of Technology Roorkee"}
            ],
            "knowsAbout": [
                "Polymer Science", "Materials Science", "Data-driven Formulation", 
                "Scientific Visualization", "Photopolymer Formulation", 
                "3D Printing Formulation", "Thin Shell Mechanics", 
                "Stimuli Responsive Polymers", "Cryogenic Polymers", 
                "Fusion Materials Science"
            ],
            "image": f"{SITE_URL}assets/img/profile-img.jpg",
            "description": desc_content,
            "sameAs": [
                "https://github.com/nakulbende",
                "https://www.linkedin.com/in/nakulbende",
                "http://www.nakulbende.com"
            ]
        }
        
        # Inject Schema
        for old_s in soup.find_all('script', type='application/ld+json'):
            old_s.decompose()
        schema_tag = soup.new_tag('script', type='application/ld+json')
        schema_tag.string = json.dumps(schema, indent=2)
        soup.head.append(schema_tag)
        modified = True

    return modified

def optimize_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    
    is_index = os.path.basename(file_path) == "index.html"
    modified = inject_seo(soup, file_path, is_index)

    # 4. Accessibility: Ensure Navigation role and Image Alts
    nav_menu = soup.find('nav') or soup.find('ul', id='navbar')
    if nav_menu and not nav_menu.has_attr('role'):
        nav_menu['role'] = 'navigation'
        modified = True

    for img in soup.find_all('img'):
        if not img.has_attr('alt') or img['alt'] == "":
            img['alt'] = "Nakul Bende Portfolio Image"
            modified = True
        img['loading'] = 'lazy'
        classes = img.get('class', [])
        if 'img-fluid' not in classes:
            classes.append('img-fluid')
            img['class'] = classes
        modified = True

    # 5. Performance: Scripts & Fonts
    for script in soup.find_all('script', src=True):
        if not script.has_attr('defer'):
            script['defer'] = None
            modified = True

    # Preconnect for Fonts
    if not soup.find('link', rel="dns-prefetch", href="https://fonts.gstatic.com"):
        hint = soup.new_tag('link', rel="dns-prefetch", href="https://fonts.gstatic.com")
        soup.head.append(hint)
        modified = True

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"✅ Full Optimization & SEO: {file_path}")

def update_swiper_blocks(directory):
    """Automatically finds images and rebuilds the Swiper slider for project pages."""
    img_path = os.path.join(directory, 'assets/img')
    if not os.path.exists(img_path):
        return

    files = glob.glob(img_path + '/*.png') + glob.glob(img_path + '/*.jpg')
    if not files: return
    
    random.shuffle(files)
    html_files = glob.glob(os.path.join(directory, '*.html'))
    if not html_files: return
    
    target_html = html_files[0]
    photo_string = ""
    for f in files:
        rel_path = os.path.relpath(f, directory)
        photo_string += f"""
                  <div class="swiper-slide">
                    <img src="{rel_path}" class="img-fluid" alt="Portfolio Image" loading="lazy">
                  </div>"""

    with open(target_html, 'r', encoding='utf-8') as f:
        html_content = f.read()

    start_marker = '<div class="swiper-wrapper align-items-center">'
    end_marker = '<div class="swiper-pagination"></div>'
    start_idx = html_content.find(start_marker)
    end_idx = html_content.find(end_marker)

    if start_idx != -1 and end_idx != -1:
        final_html = (
            html_content[:start_idx + len(start_marker)] + 
            photo_string + 
            "\n              </div>\n              " + 
            html_content[end_idx:]
        )
        with open(target_html, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"📸 Swiper updated: {target_html}")

if __name__ == "__main__":
    print("🚀 Starting Unified Site Management...")
    # Walk folders for Swiper updates
    for subdir, dirs, files in os.walk(ROOT_DIR):
        if any(x in subdir for x in ['venv', '.git', 'assets']): continue
        if 'assets' in dirs:
            update_swiper_blocks(subdir)
            
    # Global optimization and SEO injection
    for subdir, dirs, files in os.walk(ROOT_DIR):
        if any(x in subdir for x in ['venv', '.git']): continue
        for file in files:
            if file.endswith(".html"):
                optimize_html(os.path.join(subdir, file))

    print("\n--- Site is now fast, mobile-friendly, and SEO-ready! ---")