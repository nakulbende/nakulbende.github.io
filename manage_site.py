import os
import glob
import random
import json
from bs4 import BeautifulSoup

# --- Configuration ---
ROOT_DIR = "."
SITE_URL = "https://nakulbende.github.io/"
FONT_URL = "https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,600&family=Poppins:ital,wght@0,300;0,400;0,500;0,600&family=Raleway:ital,wght@0,300;0,400;0,500;0,600&display=swap"

def clean_head_section(soup):
    """
    De-duplicates viewport, charset, and messy font links.
    Ensures the head is tidy before we inject new SEO data.
    """
    if not soup.head:
        return

    # 1. De-duplicate Viewport and Charset
    viewports = soup.find_all('meta', attrs={'name': 'viewport'})
    for tag in viewports[1:]:  # Keep only the first one
        tag.decompose()
    
    charsets = soup.find_all('meta', charset=True)
    for tag in charsets[1:]:
        tag.decompose()

    # 2. Remove messy or redundant Google Font links
    for link in soup.find_all('link', href=True):
        href = link['href']
        if "fonts.googleapis.com" in href or "fonts.gstatic.com" in href:
            link.decompose()

def inject_seo(soup, file_path, is_index=False):
    """Finds and updates SEO tags instead of appending duplicates."""
    modified = False
    page_title = "Nakul Bende" if is_index else f"Project | Nakul Bende"
    desc_content = "Fusion Materials Scientist: Leveraging engineering leadership and background in polymers, data-driven formulation + material qualification, and scientific visualization for humanity's most critical challenges"
    
    # Update Title
    if soup.title:
        if soup.title.string != page_title:
            soup.title.string = page_title
            modified = True
    else:
        new_title = soup.new_tag('title')
        new_title.string = page_title
        soup.head.insert(0, new_title)
        modified = True

    # Meta tags to manage (Type, Attribute Name, Attribute Value, Content)
    meta_configs = [
        ("name", "description", desc_content),
        ("property", "og:title", page_title),
        ("property", "og:description", desc_content),
        ("property", "og:url", SITE_URL),
        ("property", "og:type", "website"),
        ("property", "og:image", f"{SITE_URL}assets/img/profile-img.jpg"),
        ("name", "twitter:card", "summary_large_image")
    ]

    for attr, val, content in meta_configs:
        tag = soup.find('meta', attrs={attr: val})
        if tag:
            if tag.get('content') != content:
                tag['content'] = content
                modified = True
        else:
            new_meta = soup.new_tag('meta', content=content)
            new_meta[attr] = val
            soup.head.append(new_meta)
            modified = True

    # Schema JSON-LD (Replace entirely to ensure it's fresh)
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
        for s in soup.find_all('script', type='application/ld+json'):
            s.decompose()
        
        schema_tag = soup.new_tag('script', type='application/ld+json')
        schema_tag.string = json.dumps(schema, indent=2)
        soup.head.append(schema_tag)
        modified = True

    return modified

def optimize_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    
    # 1. Cleanup existing mess first
    clean_head_section(soup)
    
    is_index = os.path.basename(file_path) == "index.html"
    modified = inject_seo(soup, file_path, is_index)

    # 2. Re-inject Clean Fonts
    font_link = soup.new_tag('link', rel='stylesheet', href=FONT_URL)
    preconnect = soup.new_tag('link', rel='preconnect', href='https://fonts.gstatic.com', crossorigin='')
    dns_hint = soup.new_tag('link', rel='dns-prefetch', href='https://fonts.gstatic.com')
    soup.head.append(dns_hint)
    soup.head.append(preconnect)
    soup.head.append(font_link)

    # 3. Accessibility & Image Fluidity
    for img in soup.find_all('img'):
        if not img.has_attr('alt') or img['alt'] == "":
            img['alt'] = "Nakul Bende Portfolio Image"
        img['loading'] = 'lazy'
        classes = img.get('class', [])
        if 'img-fluid' not in classes:
            classes.append('img-fluid')
            img['class'] = classes

    # 4. Defer Scripts
    for script in soup.find_all('script', src=True):
        if not script.has_attr('defer') and "googletagmanager" not in script['src']:
            script['defer'] = None

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print(f"✨ Cleaned & Optimized: {file_path}")

def update_swiper_blocks(directory):
    img_path = os.path.join(directory, 'assets/img')
    if not os.path.exists(img_path): return
    files = glob.glob(img_path + '/*.png') + glob.glob(img_path + '/*.jpg')
    if not files: return
    random.shuffle(files)
    html_files = glob.glob(os.path.join(directory, '*.html'))
    if not html_files: return
    
    target_html = html_files[0]
    photo_string = ""
    for f in files:
        rel_path = os.path.relpath(f, directory)
        photo_string += f'\n<div class="swiper-slide"><img src="{rel_path}" class="img-fluid" alt="Portfolio Image" loading="lazy"></div>'

    with open(target_html, 'r', encoding='utf-8') as f:
        content = f.read()

    start_m, end_m = '<div class="swiper-wrapper align-items-center">', '<div class="swiper-pagination"></div>'
    s_idx, e_idx = content.find(start_m), content.find(end_m)

    if s_idx != -1 and e_idx != -1:
        final = content[:s_idx + len(start_m)] + photo_string + "\n</div>\n" + content[e_idx:]
        with open(target_html, 'w', encoding='utf-8') as f:
            f.write(final)
        print(f"📸 Swiper Rebuilt: {target_html}")

if __name__ == "__main__":
    # First rebuild swipers
    for subdir, dirs, files in os.walk(ROOT_DIR):
        if any(x in subdir for x in ['venv', '.git', 'assets']): continue
        if 'assets' in dirs: update_swiper_blocks(subdir)
            
    # Then clean and optimize everything
    for subdir, dirs, files in os.walk(ROOT_DIR):
        if any(x in subdir for x in ['venv', '.git']): continue
        for file in files:
            if file.endswith(".html"):
                optimize_html(os.path.join(subdir, file))

    print("\n✅ All files have been scrubbed of duplicates and optimized!")