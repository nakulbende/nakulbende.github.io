# Website Modernization & Optimization Action Plan

**Target Site:** https://nakulbende.github.io/
**Goal:** Reduce page weight, improve load times, and fix mobile responsiveness without altering the existing visual design.

---

## Phase 1: Performance & Weight Reduction (The "Heavy" Feel)

### 1. Optimize the Google Fonts Payload
**File to edit:** `index.html` and `bhutan.html` (and any other subpages)
**Issue:** Loading multiple font families (Open Sans, Raleway, Poppins) across all weights and italics slows down the initial paint of the website.
**Action:** Replace your current Google Fonts `<link>` tags in the `<head>` section with this optimized version that preconnects to Google's servers and only downloads the essential weights.

```html
<link rel="preconnect" href="[https://fonts.googleapis.com](https://fonts.googleapis.com)">
<link rel="preconnect" href="[https://fonts.gstatic.com](https://fonts.gstatic.com)" crossorigin>
<link href="[https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,600&family=Poppins:ital,wght@0,300;0,400;0,500;0,600&family=Raleway:ital,wght@0,300;0,400;0,500;0,600&display=swap](https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,600&family=Poppins:ital,wght@0,300;0,400;0,500;0,600&family=Raleway:ital,wght@0,300;0,400;0,500;0,600&display=swap)" rel="stylesheet">
```

### 2. Implement Lazy Loading for Images
**File to edit:** `index.html`, `bhutan.html`, and all subpages
**Issue:** The browser is downloading all portfolio images when the page loads, even those at the very bottom.
**Action:** Add the `loading="lazy"` attribute to every `<img>` tag.

```html
<img src="portfolio/bhutan/0.png" class="img-fluid" alt="">

<img src="portfolio/bhutan/0.png" class="img-fluid" alt="" loading="lazy">
```

### 3. Replace Heavy GIF Animations
**Files to update:** Portfolio images folder
**Issue:** GIFs (like `0.gif` for Bendy shells and DLP µ-lithography) are massive files that stall mobile networks.
**Action:** 1. Convert your `.gif` files to silent `.mp4` or `.webm` videos using an online converter (like CloudConvert).
2. Alternatively, convert them to animated `.webp` files.
3. Update the HTML tags to either use the new `.webp` format or use the `<video>` tag.

```html
<video autoplay loop muted playsinline class="img-fluid">
  <source src="portfolio/bendyshells/0.webm" type="video/webm">
  <source src="portfolio/bendyshells/0.mp4" type="video/mp4">
</video>
```

### 4. Defer Render-Blocking JavaScript
**File to edit:** `index.html` and `bhutan.html`
**Issue:** Scripts like `swiper-bundle.min.js` and `main.js` force the browser to stop rendering the visual design while they download and execute.
**Action:** Add the `defer` attribute to your `<script>` tags just before the closing `</body>` tag.

```html
<script src="assets/vendor/swiper/swiper-bundle.min.js" defer></script>
<script src="assets/js/main.js" defer></script>
```

---

## Phase 2: Mobile Responsiveness (Fixing the Layout)

### 1. Fix the Sidebar / Main Content Overlap
**File to edit:** `assets/css/style.css`
**Issue:** The fixed desktop sidebar menu crushes the main content on smaller screens.
**Action:** Locate your media queries at the bottom of `style.css`. Ensure you have the following rules to hide the fixed sidebar off-screen and allow the main content wrapper to stretch to 100% width on mobile and tablet screens.

```css
/* Mobile Navigation & Layout Adjustments */
@media (max-width: 1199px) {
  #header {
    left: -300px; /* Hides the sidebar off-screen */
    transition: all 0.5s;
  }
  
  /* When the hamburger menu is clicked, JS will add a class to body to slide it back in */
  .mobile-nav-active #header {
    left: 0;
  }

  #main {
    margin-left: 0; /* Lets the main content fill the screen */
  }
}
```

### 2. Ensure Image Fluidity in Project Details
**File to edit:** `bhutan.html` and other project subpages
**Issue:** Large images inside project descriptions can break out of their containers on mobile devices, causing horizontal scrolling.
**Action:** Ensure every image inside your portfolio details section has Bootstrap's `img-fluid` class.

```html
<div class="portfolio-details-slider swiper">
  <div class="swiper-wrapper align-items-center">
    <div class="swiper-slide">
      <img src="portfolio/bhutan/1.jpg" class="img-fluid" alt="Bhutan project detail 1">
    </div>
  </div>
</div>
```

### 3. Verify the Viewport Meta Tag
**File to edit:** `index.html` and `bhutan.html`
**Issue:** Mobile browsers might try to display the desktop version zoomed out if this is missing.
**Action:** Verify that this tag exists in the `<head>` section of every HTML file:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

---
**Final Tip:** After making these changes locally, test them on your desktop browser by shrinking the window width down to a narrow rectangle to simulate a mobile device before pushing the changes to GitHub Pages!