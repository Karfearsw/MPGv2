# Changelog

All notable changes to the MoneyPrinter G resources are documented here.

## [1.0.1] - 2025-10-26

### Updated
- Cleaned and verified `MoneyPrinter G link.txt`:
  - Fixed duplicated Ben_10 YouTube URL.
  - Normalized entries to `Title` / `URL` / `Status` format.
  - Verified all 20 links return HTTP 200; annotated as `Status: OK`.
- Generated `links.json` with structured link metadata for site consumption.
- Processed cover images in `covers/`:
  - Ensured minimum resolution of 1000x1000 by upscaling where needed (Lanczos).
  - Optimized PNG/JPEG for faster loads.
  - Backed up originals to `covers/_backup_originals/`.
  - Emitted `covers/metadata.json` with filename, format, original and final dimensions, timestamps, and whether upscaled.
- Updated site behavior (`Moneyprinterg/script.js`):
  - Dynamic music grid now uses `links.json` for direct per-track URLs, with YouTube search fallback.
- Updated footer links (`Moneyprinterg/index.html`):
  - Wired Spotify artist and Apple Music artist links.

### Performance & Compatibility
- Covers optimized to load quickly; target under 2s on typical broadband.
- Directory structure and filenames preserved for backward compatibility.
- Added `rel="noopener noreferrer"` and `target="_blank"` for external links.

### Testing
- Cross-device/browser spot-check via local server (`python -m http.server 5500`).
- Visual verification of dynamic grid, cover rendering, and footer links.

---

## [1.0.0] - 2025-10-26
- Initial static site scaffold (HTML/CSS/JS), blue/white/black theme.
- Base hero, music grid placeholder, sections, and micro-interactions.