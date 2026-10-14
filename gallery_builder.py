import os
import glob
import json
import re
from PIL import Image, ImageOps
from flask import Flask, render_template_string, request, jsonify, send_from_directory

app = Flask(__name__)

# Global variables to be set after user selection
WORK_DIR = ""
SRC_DIR = ""
LARGE_DIR = ""
THUMB_DIR = ""
JSON_FILE = ""
TARGET_HTML = ""

def setup_paths(selected_folder):
    global WORK_DIR, SRC_DIR, LARGE_DIR, THUMB_DIR, JSON_FILE, TARGET_HTML
    
    WORK_DIR = os.path.join(os.getcwd(), 'portfolio', selected_folder)
    SRC_DIR = os.path.join(WORK_DIR, 'assets', 'img')
    LARGE_DIR = os.path.join(SRC_DIR, 'large')
    THUMB_DIR = os.path.join(SRC_DIR, 'thumbs')
    JSON_FILE = os.path.join(WORK_DIR, 'gallery_data.json')
    
    for d in [SRC_DIR, LARGE_DIR, THUMB_DIR]:
        os.makedirs(d, exist_ok=True)
        
    # Auto-find the HTML file in this directory
    html_files = glob.glob(os.path.join(WORK_DIR, "*.html"))
    if html_files:
        TARGET_HTML = html_files[0]
    else:
        print(f"Error: No HTML file found in {WORK_DIR}")
        exit(1)

def load_data():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return {"settings": {"thumbnails": True, "transition": "lg-slide"}, "images": data}
            return data
    return {"settings": {"thumbnails": True, "transition": "lg-slide"}, "images": []}

def save_data(data):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def process_new_images():
    data = load_data()
    existing_originals = {item['original_name'] for item in data['images']}
    
    valid_exts = ('.jpg', '.jpeg', '.png')
    raw_files = [f for f in os.listdir(SRC_DIR) 
                 if f.lower().endswith(valid_exts) and os.path.isfile(os.path.join(SRC_DIR, f))]
    
    new_items = []
    files_to_delete = []
    
    for file in raw_files:
        if file in existing_originals:
            continue
            
        print(f"Processing new photo: {file}")
        file_path = os.path.join(SRC_DIR, file)
        base_name = os.path.splitext(file)[0]
        new_filename = f"{base_name}.webp"
        
        try:
            with Image.open(file_path) as img:
                img = ImageOps.exif_transpose(img)
                
                img_large = img.copy()
                img_large.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
                large_path = os.path.join(LARGE_DIR, new_filename)
                img_large.convert('RGB').save(large_path, 'WEBP', quality=82)
                width, height = img_large.size
                
                img_thumb = img.copy()
                img_thumb.thumbnail((300, 300), Image.Resampling.LANCZOS)
                thumb_path = os.path.join(THUMB_DIR, new_filename)
                img_thumb.convert('RGB').save(thumb_path, 'WEBP', quality=75)
                
            files_to_delete.append(file_path)
                
            new_items.append({
                "original_name": file,
                "filename": new_filename,
                "title": "",
                "caption": "",
                "width": width,
                "height": height
            })
        except Exception as e:
            print(f"Failed to process {file}: {e}")
    
    if new_items:
        data['images'].extend(new_items)
        save_data(data)
        
    if files_to_delete:
        choice = input(f"\nProcessed {len(files_to_delete)} new images. Delete original raw files? (y/N): ")
        if choice.lower() == 'y':
            for fp in files_to_delete:
                os.remove(fp)
            print("Original files deleted.")

def inject_html(data):
    MAX_VISIBLE = 12 
    
    html_content = """
    <style>
        #my-portfolio {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        #my-portfolio a.gallery-item { display: block; overflow: hidden; border-radius: 8px; }
        #my-portfolio a.gallery-item.hidden { display: none; }
        #my-portfolio img { width: 100%; height: 200px; object-fit: cover; transition: transform 0.3s ease; }
        #my-portfolio a.gallery-item:hover img { transform: scale(1.05); }
    </style>
"""
    
    for i, item in enumerate(data['images']):
        title_attr = f"<h4>{item['title']}</h4>" if item['title'] else ""
        caption_attr = f"<p>{item['caption']}</p>" if item['caption'] else ""
        sub_html = f"{title_attr}{caption_attr}"
        hidden_class = " hidden" if i >= MAX_VISIBLE else ""
        
        html_content += f"""
        <a href="assets/img/large/{item['filename']}" 
           class="gallery-item{hidden_class}"
           data-lg-size="{item['width']}-{item['height']}" 
           data-sub-html='{sub_html}'>
           <img src="assets/img/thumbs/{item['filename']}" alt="{item['title']}" />
        </a>"""
    
    thumb_flag = "true" if data['settings']['thumbnails'] else "false"
    transition_mode = data['settings']['transition']
    
    js_content = f"""<script>
    document.addEventListener("DOMContentLoaded", function() {{
        const galleryContainer = document.getElementById('my-portfolio');
        if (galleryContainer && typeof lightGallery !== 'undefined') {{
            lightGallery(galleryContainer, {{
                selector: '.gallery-item',
                plugins: [lgZoom, lgThumbnail],
                speed: 500,
                mode: '{transition_mode}',
                thumbnail: {thumb_flag},
                zoomFromOrigin: true,
                allowMediaOverlap: false
            }});
        }}
    }});
</script>"""

    with open(TARGET_HTML, 'r', encoding='utf-8') as f:
        file_text = f.read()
        
    pattern_html = re.compile(r'(<!-- GALLERY_START -->).*?(<!-- GALLERY_END -->)', re.DOTALL)
    new_text = pattern_html.sub(rf'\1{html_content}\n        \2', file_text)
    
    pattern_js = re.compile(r'(<!-- GALLERY_JS_START -->).*?(<!-- GALLERY_JS_END -->)', re.DOTALL)
    new_text = pattern_js.sub(rf'\1\n{js_content}\n<!-- \2 -->', new_text)
    
    with open(TARGET_HTML, 'w', encoding='utf-8') as f:
        f.write(new_text)

# --- Flask Routes ---

@app.route('/')
def index():
    data = load_data()
    return render_template_string(HTML_TEMPLATE, data=data)

@app.route('/assets/img/<path:filename>')
def serve_photos(filename):
    # Serve dynamically from whichever portfolio folder was selected
    return send_from_directory(SRC_DIR, filename)

@app.route('/save', methods=['POST'])
def save():
    updated_data = request.json
    save_data(updated_data)
    inject_html(updated_data)
    return jsonify({"status": "success", "message": f"Updated & saved to {os.path.basename(TARGET_HTML)}!"})

# --- Local Dashboard UI ---
# (Using the exact same UI as before)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Portfolio Gallery CMS</title>
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 840px; margin: 30px auto; background: #f8fafc; color: #0f172a; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;}
        .settings-panel { background: #ffffff; padding: 16px 20px; border-radius: 8px; margin-bottom: 20px; display: flex; gap: 24px; align-items: center; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.05);}
        button { background: #0f172a; color: #fff; border: none; padding: 10px 22px; border-radius: 6px; cursor: pointer; font-size: 15px; font-weight: 500;}
        button:hover { background: #334155; }
        .row { display: flex; background: #ffffff; padding: 16px; margin-bottom: 12px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.04); cursor: grab; align-items: center;}
        .row:active { cursor: grabbing; }
        .thumb { width: 90px; height: 90px; object-fit: cover; border-radius: 6px; margin-right: 20px; background: #e2e8f0; }
        .inputs { display: flex; flex-direction: column; flex-grow: 1; gap: 8px; }
        input[type="text"], textarea, select { width: 100%; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-family: inherit; font-size: 14px; box-sizing: border-box;}
        textarea { resize: vertical; height: 54px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Gallery Manager</h2>
        <button onclick="saveData()">Save & Inject HTML</button>
    </div>
    
    <div class="settings-panel">
        <label>
            <input type="checkbox" id="setting-thumbnails" {% if data.settings.thumbnails %}checked{% endif %}> 
            Thumbnail Bar Active
        </label>
        <label style="margin-left: auto;">
            Transition:
            <select id="setting-transition" style="width: auto; display: inline-block;">
                <option value="lg-slide" {% if data.settings.transition == 'lg-slide' %}selected{% endif %}>Slide</option>
                <option value="lg-fade" {% if data.settings.transition == 'lg-fade' %}selected{% endif %}>Fade</option>
                <option value="lg-zoom-in" {% if data.settings.transition == 'lg-zoom-in' %}selected{% endif %}>Zoom In</option>
                <option value="lg-zoom-out" {% if data.settings.transition == 'lg-zoom-out' %}selected{% endif %}>Zoom Out</option>
            </select>
        </label>
    </div>

    <div id="gallery-list">
        {% for item in data.images %}
        <div class="row" data-orig="{{ item.original_name }}" data-file="{{ item.filename }}" data-w="{{ item.width }}" data-h="{{ item.height }}">
            <img src="/assets/img/thumbs/{{ item.filename }}" class="thumb">
            <div class="inputs">
                <input type="text" class="title-input" placeholder="Title (optional)" value="{{ item.title }}">
                <textarea class="caption-input" placeholder="Caption/Description...">{{ item.caption }}</textarea>
            </div>
        </div>
        {% endfor %}
    </div>

    <script>
        const el = document.getElementById('gallery-list');
        Sortable.create(el, { animation: 150 });

        async function saveData() {
            const rows = document.querySelectorAll('.row');
            const images = [];
            
            rows.forEach(row => {
                images.push({
                    original_name: row.dataset.orig,
                    filename: row.dataset.file,
                    width: parseInt(row.dataset.w),
                    height: parseInt(row.dataset.h),
                    title: row.querySelector('.title-input').value,
                    caption: row.querySelector('.caption-input').value
                });
            });
            
            const payload = {
                settings: {
                    thumbnails: document.getElementById('setting-thumbnails').checked,
                    transition: document.getElementById('setting-transition').value
                },
                images: images
            };

            const response = await fetch('/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            alert(result.message);
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    # 1. Scan for portfolio folders
    portfolio_dir = os.path.join(os.getcwd(), 'portfolio')
    if not os.path.exists(portfolio_dir):
        print(f"Error: Could not find 'portfolio' directory at {portfolio_dir}")
        exit(1)
        
    folders = [f for f in os.listdir(portfolio_dir) if os.path.isdir(os.path.join(portfolio_dir, f))]
    
    if not folders:
        print("No folders found in /portfolio/")
        exit(1)
        
    print("\nWhich portfolio would you like to edit?")
    for i, folder in enumerate(folders):
        print(f"[{i}] {folder}")
        
    try:
        choice = int(input("\nEnter number: "))
        selected_folder = folders[choice]
    except (IndexError, ValueError):
        print("Invalid selection.")
        exit(1)
        
    # 2. Setup paths and process images
    setup_paths(selected_folder)
    print(f"\nTargeting: {TARGET_HTML}")
    print("Checking for new images...")
    process_new_images()
    
    # 3. Run UI
    print("\nOpening Dashboard... Navigate to http://127.0.0.1:5000 in your browser.")
    app.run(debug=False, port=5000)