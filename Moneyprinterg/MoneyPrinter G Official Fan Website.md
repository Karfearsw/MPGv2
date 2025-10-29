# MoneyPrinter G — Official Fan Website

Updated: 2025-10-29

This document summarizes the header redesign and how it integrates with the existing site. It includes three prototype variations, verified external links, and guidance for previewing and usability testing.

## Header Redesign Overview

Objectives
- Enhance visual appeal and clarity without disrupting existing functionality.
- Improve navigation discoverability and utility access (search, CTA, language).
- Maintain brand consistency across color and typography.

Deliverables (Prototypes)
- Variant A — Minimal horizontal bar: `index.html`
- Variant B — Centered stacked layout with tagline: `header-b.html`
- Variant C — Brand-left layout with mega-menu: `header-c.html`

Core Features
- Responsive layout with breakpoints for mobile, tablet, desktop.
- Intuitive navigation with active states and smooth transitions.
- Prominent branding: high-res logo, brand name, optional tagline (B).
- Integrated search with predictive suggestions.
- Primary CTA button (Listen) and secondary Subscribe.
- Language selector (EN/ES placeholder) ready for future i18n.

Accessibility & UX
- Keyboard navigable menus; ESC to close mega-menu; focus-visible states.
- Sufficient contrast for text and indicators; touch-friendly targets.
- Shrink-on-scroll behavior in Variant B to maintain context while reading.

## Verified Platform Links
- Spotify: `https://open.spotify.com/artist/7IwhfPG4odhVlv8a7LtFBJ`
- Apple Music: `https://music.apple.com/us/artist/moneyprinter-g/1689807983`
- YouTube: `https://www.youtube.com/watch?v=UKbBp5BnPYM&list=OLAK5uy_kXfIyEiZgvuZrX6LrvDnkXT3mLascrOHE`

## Preview & Testing

Local preview
- Serve `dist/site` at `http://localhost:8000/` and navigate to:
  - Variant A: `/index.html`
  - Variant B: `/header-b.html`
  - Variant C: `/header-c.html`

Usability checks
- Navigation: Active state reflects current section/hash; keyboard traversal.
- Search: Suggestions appear for partial queries; mouse and keyboard supported.
- Mobile: Menu toggle opens panel; body scroll locked; close restores scroll.
- Mega-menu (Variant C): Hover/focus to open; ESC/blur to close.

## Notes
- All prototypes follow the site’s existing color palette and typography.
- Functionality aligns with current content loading for music and events.
- See `MoneyPrinter G Fan Website Design.txt` for detailed design specs.