import os
import re
import glob
from PIL import Image, ImageOps

# =========================================================
# PHASE 1: LIGHTGALLERY MIGRATION
# =========================================================
html_files = glob.glob("portfolio/*/*.html")

swiper_css_pattern = re.compile(r'<link href="\.\./\.\./assets/vendor/swiper/swiper-bundle\.min\.css" rel="stylesheet"/>')
lg_css = '<link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lightgallery@2.7.2/css/lightgallery-bundle.min.css" />'

swiper_js_pattern = re.compile(r'<script defer="" src="\.\./\.\./assets/vendor/swiper/swiper-bundle\.min\.js"></script>')

gallery_block_pattern = re.compile(r'<div class="portfolio-details-slider swiper">.*?<div class="swiper-scrollbar">\s*</div>\s*</div>', re.DOTALL)
new_gallery_markers = """<div id="my-portfolio">
            <!-- GALLERY_START -->
            <!-- GALLERY_END -->
       </div>"""

js_markers = """
  <script src="https://cdn.jsdelivr.net/npm/lightgallery@2.7.2/lightgallery.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/lightgallery@2.7.2/plugins/thumbnail/lg-thumbnail.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/lightgallery@2.7.2/plugins/zoom/lg-zoom.min.js"></script>
  <!-- GALLERY_JS_START -->
  <!-- GALLERY_JS_END -->
</body>"""

print("--- Phase 1: Prepping Portfolio Galleries ---")
for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = swiper_css_pattern.sub(lg_css, html)
    html = swiper_js_pattern.sub('', html)
    
    if 'id="my-portfolio"' not in html:
        html = gallery_block_pattern.sub(new_gallery_markers, html)
        
    if '<!-- GALLERY_JS_START -->' not in html:
        html = html.replace('</body>', js_markers)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)

print(f"Successfully prepped {len(html_files)} HTML files for LightGallery.\n")

# =========================================================
# PHASE 2: INDEX PAGE WEBP OPTIMIZATION
# =========================================================
print("--- Phase 2: Optimizing Index Page Images to WebP ---")
if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
        index_html = f.read()

    # Find all local image src attributes ending in jpg, jpeg, png
    img_pattern = re.compile(r'src=["\']([^"\']+\.(?:jpg|jpeg|png))["\']', re.IGNORECASE)
    matches = img_pattern.findall(index_html)
    
    converted_count = 0
    for src in set(matches):
        if src.startswith("http"): 
            continue
        
        local_path = os.path.normpath(os.path.join(os.getcwd(), src))
        if os.path.exists(local_path):
            base_name = os.path.splitext(src)[0]
            new_src = f"{base_name}.webp"
            new_local_path = os.path.normpath(os.path.join(os.getcwd(), new_src))
            
            try:
                # Convert and resize if the webp doesn't already exist
                if not os.path.exists(new_local_path):
                    with Image.open(local_path) as img:
                        img = ImageOps.exif_transpose(img) # Fix rotation issues
                        img.thumbnail((800, 800), Image.Resampling.LANCZOS) # Resize for grid
                        img.convert('RGB').save(new_local_path, 'WEBP', quality=82)
                
                # Update HTML to point to the new .webp file
                index_html = index_html.replace(f'src="{src}"', f'src="{new_src}"')
                index_html = index_html.replace(f"src='{src}'", f"src='{new_src}'")
                converted_count += 1
                print(f"Converted & Linked: {src} -> {new_src}")
            except Exception as e:
                print(f"Failed to convert {src}: {e}")
                
    if converted_count > 0:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(index_html)
        print(f"\nUpdated index.html with {converted_count} optimized WebP images!")
    else:
        print("No images needed conversion on index.html.")
else:
    print("index.html not found in the root directory.")