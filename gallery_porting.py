import os
import re
import glob

# Search for all HTML files in the portfolio subdirectories
html_files = glob.glob("portfolio/*/*.html")

swiper_css_pattern = re.compile(r'<link href="\.\./\.\./assets/vendor/swiper/swiper-bundle\.min\.css" rel="stylesheet"/>')
lg_css = '<link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lightgallery@2.7.2/css/lightgallery-bundle.min.css" />'

swiper_js_pattern = re.compile(r'<script defer="" src="\.\./\.\./assets/vendor/swiper/swiper-bundle\.min\.js"></script>')

# Matches the old Swiper gallery block
gallery_block_pattern = re.compile(r'<div class="portfolio-details-slider swiper">.*?<div class="swiper-scrollbar">\s*</div>\s*</div>', re.DOTALL)
new_gallery_markers = """<div id="my-portfolio">
            <!-- GALLERY_START -->
            <!-- GALLERY_END -->
       </div>"""

# Ensure we don't duplicate the JS markers
js_markers = """
  <script src="https://cdn.jsdelivr.net/npm/lightgallery@2.7.2/lightgallery.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/lightgallery@2.7.2/plugins/thumbnail/lg-thumbnail.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/lightgallery@2.7.2/plugins/zoom/lg-zoom.min.js"></script>
  <!-- GALLERY_JS_START -->
  <!-- GALLERY_JS_END -->
</body>"""

for file_path in html_files:
    print(f"Migrating: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Replace CSS
    html = swiper_css_pattern.sub(lg_css, html)
    
    # 2. Remove Swiper JS
    html = swiper_js_pattern.sub('', html)
    
    # 3. Replace HTML Gallery Block (only if my-portfolio isn't already there)
    if 'id="my-portfolio"' not in html:
        html = gallery_block_pattern.sub(new_gallery_markers, html)
        
    # 4. Inject JS Markers before closing body (if not already there)
    if '<!-- GALLERY_JS_START -->' not in html:
        html = html.replace('</body>', js_markers)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)

print(f"\nSuccessfully prepped {len(html_files)} HTML files for LightGallery!")