from bs4 import BeautifulSoup

with open("index.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), 'lxml')

# Find images inside the Isotope portfolio container and remove lazy loading
for img in soup.find_all('img'):
    parent = img.parent
    is_grid = False
    while parent:
        classes = parent.get("class", [])
        if any(c in classes for c in ["portfolio-item", "portfolio-container", "portfolio-wrap"]):
            is_grid = True
            break
        parent = parent.parent
        
    if is_grid and img.has_attr('loading'):
        del img['loading']

with open("index.html", "w", encoding="utf-8") as f:
    f.write(soup.prettify())

print("Cleaned lazy loading from portfolio grid images!")