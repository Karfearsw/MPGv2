// Simple micro-interactions and scroll reveal
(function () {
  // Subscribe button checkmark feedback
  const form = document.querySelector('.subscribe-form');
  if (form) {
    form.addEventListener('submit', function () {
      const btn = form.querySelector('button');
      btn.disabled = true;
      btn.textContent = 'Subscribed ✓';
      setTimeout(() => { btn.disabled = false; btn.textContent = 'Subscribe'; }, 2000);
    });
  }

  // Core Web Vitals tracking (LCP, CLS, FID)
  (function trackVitals() {
    const ENABLE_ANALYTICS = !!window.__ENABLE_ANALYTICS;
    const ANALYTICS_URL = typeof window.__ANALYTICS_URL === 'string' ? window.__ANALYTICS_URL : null;
    const vitals = { lcp: null, cls: 0, fid: null, ua: navigator.userAgent, ts: Date.now() };
    try {
      const lcpObs = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const last = entries[entries.length - 1];
        vitals.lcp = last && (last.renderTime || last.loadTime || last.startTime);
      });
      lcpObs.observe({ type: 'largest-contentful-paint', buffered: true });
    } catch (e) {}

    try {
      const clsObs = new PerformanceObserver((list) => {
        for (const e of list.getEntries()) {
          if (!e.hadRecentInput) vitals.cls += e.value;
        }
      });
      clsObs.observe({ type: 'layout-shift', buffered: true });
    } catch (e) {}

    try {
      const fidObs = new PerformanceObserver((list) => {
        const first = list.getEntries()[0];
        if (first) vitals.fid = first.processingStart - first.startTime;
      });
      fidObs.observe({ type: 'first-input', buffered: true });
    } catch (e) {}

    function sendVitals() {
      if (!ENABLE_ANALYTICS || !ANALYTICS_URL) return;
      const payload = JSON.stringify(vitals);
      const url = ANALYTICS_URL;
      if (navigator.sendBeacon) {
        navigator.sendBeacon(url, payload);
      } else {
        fetch(url, { method: 'POST', body: payload, keepalive: true }).catch(() => {});
      }
    }

    if (ENABLE_ANALYTICS && ANALYTICS_URL) {
      addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') sendVitals();
      });
      addEventListener('pagehide', sendVitals);
    }
  }());

  // Scroll reveal for sections
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.section').forEach((el) => {
    el.classList.add('reveal');
    observer.observe(el);
  });

  // Dynamic music grid from covers folder
  const musicGrid = document.getElementById('music-grid');
  if (musicGrid) {
    const files = [
      'No_Diddy_mpg.png',
      'Hellen_keller_mpg.png',
      'Wow_mpg.png',
      '2_U_4_PrinterFest.png',
      '24_mpg.png',
      'Addy_Bruh_mpg.png',
      'Andrew_Tate_mpg.png',
      'Ben_10_mpg.png',
      'Bond_A_Hunnit_Freestyle_mpg.png',
      'Gansta_w_feeling_mpg.png',
      'Keep_It_G_mpg.jpeg',
      'Never_Lose_mpg.png',
      'Onnamanapeea_mpg.png',
      'Run_Forest_mpg.png',
      'Scottie_Pippen_mpg.png',
      'Still_The_Same_Freestyle_mpg.png',
      'Talk_My_Shit_mpg.png',
      'Y_U_mad_mpg.png'
    ];

    const norm = (s) => s.toLowerCase()
      .replace(/\.(png|jpeg|jpg)$/i, '')
      .replace(/_mpg$/i, '')
      .replace(/[^a-z0-9]+/g, '');

    const titleFromFile = (name) => {
      const base = name.replace(/\.(png|jpeg|jpg)$/i, '')
                       .replace(/_mpg$/i, '')
                       .replace(/_/g, ' ');
      return base.replace(/\b(\w)/g, (m) => m.toUpperCase());
    };

    // Fetch direct links mapping from links.json
    fetch('../links.json')
      .then((r) => r.json())
      .then((data) => {
        const map = {};
        (data.links || []).forEach((entry) => {
          if (entry && entry.title && entry.final_url) {
            map[norm(entry.title)] = entry.final_url;
          }
        });

        const items = files.map((f) => {
          const key = norm(f);
          const direct = map[key];
          const fallback = `https://www.youtube.com/results?search_query=${encodeURIComponent('MoneyPrinter G ' + titleFromFile(f))}`;
          return {
            title: titleFromFile(f),
            img: `../covers/${f}`,
            link: direct || fallback,
            platform: 'YouTube'
          };
        });

        const frag = document.createDocumentFragment();
        items.forEach((item) => {
          const card = document.createElement('article');
          card.className = 'card';

          const cover = document.createElement('div');
          cover.className = 'cover';
          const img = document.createElement('img');
          img.src = item.img;
          img.alt = item.title + ' cover';
          img.loading = 'lazy';
          img.decoding = 'async';
          cover.appendChild(img);

          const h3 = document.createElement('h3');
          h3.textContent = item.title;

          const actions = document.createElement('div');
          actions.className = 'card-actions';

          const playBtn = document.createElement('a');
          playBtn.className = 'btn btn-primary';
          playBtn.href = item.link;
          playBtn.target = '_blank';
          playBtn.rel = 'noopener noreferrer';
          playBtn.textContent = 'Play';

          const platformLink = document.createElement('a');
          platformLink.className = 'btn btn-outline';
          platformLink.href = item.link;
          platformLink.target = '_blank';
          platformLink.rel = 'noopener noreferrer';
          platformLink.textContent = item.platform;

          actions.appendChild(playBtn);
          actions.appendChild(platformLink);

          card.appendChild(cover);
          card.appendChild(h3);
          card.appendChild(actions);

          frag.appendChild(card);
        });

        musicGrid.appendChild(frag);
      })
      .catch(() => {
        // Fallback: do nothing; existing grid will stay empty
      });
  }

  // Discography page rendering
  const discographyList = document.getElementById('discography-list');
  if (discographyList) {
    fetch('../discography.json')
      .then((r) => r.json())
      .then((data) => {
        const tracks = (data.tracks || []).slice();
        // Already sorted chronologically in build script; ensure any null dates at end
        const frag = document.createDocumentFragment();
        tracks.forEach((t) => {
          const card = document.createElement('article');
          card.className = 'card';

          const cover = document.createElement('div');
          cover.className = 'cover';
          const img = document.createElement('img');
          img.src = `../${t.cover}`;
          img.alt = `${t.title} cover`;
          img.loading = 'lazy';
          img.decoding = 'async';
          cover.appendChild(img);

          const h3 = document.createElement('h3');
          h3.textContent = t.title;

          const year = document.createElement('div');
          year.className = 'year';
          year.textContent = t.releaseDate ? new Date(t.releaseDate).toLocaleDateString() : 'Release date: N/A';

          const actions = document.createElement('div');
          actions.className = 'card-actions';

          const y = document.createElement('a');
          y.className = 'btn btn-primary';
          // Fallback: if per-track YouTube link is missing, use a search query
          const ytSearch = `https://www.youtube.com/results?search_query=${encodeURIComponent('MoneyPrinter G ' + t.title)}`;
          y.href = t.platforms.youtube || ytSearch;
          y.target = '_blank'; y.rel = 'noopener noreferrer';
          y.textContent = 'YouTube';

          const sp = document.createElement('a');
          sp.className = 'btn btn-outline';
          sp.href = t.platforms.spotify; sp.target = '_blank'; sp.rel = 'noopener noreferrer';
          sp.textContent = 'Spotify';

          const ap = document.createElement('a');
          ap.className = 'btn btn-outline';
          ap.href = t.platforms.apple; ap.target = '_blank'; ap.rel = 'noopener noreferrer';
          ap.textContent = 'Apple Music';

          const hf = document.createElement('a');
          hf.className = 'btn btn-outline';
          hf.href = t.platforms.hyperfollow; hf.target = '_blank'; hf.rel = 'noopener noreferrer';
          hf.textContent = 'Hyperfollow';

          actions.appendChild(y);
          actions.appendChild(sp);
          actions.appendChild(ap);
          actions.appendChild(hf);

          // Credits
          const credits = document.createElement('div');
          credits.style.color = 'var(--color-muted)';
          credits.style.fontSize = '14px';
          const cText = `Artist: ${t.credits.artist} • Producer: ${t.credits.producer} • Label: ${t.credits.label}`;
          credits.textContent = cText;

          card.appendChild(cover);
          card.appendChild(h3);
          card.appendChild(year);
          card.appendChild(actions);
          card.appendChild(credits);

          frag.appendChild(card);
        });
        discographyList.appendChild(frag);
      })
      .catch(() => {
        const msg = document.createElement('div');
        msg.textContent = 'Unable to load discography.';
        discographyList.appendChild(msg);
      });
  }

  // Events teaser on Home
  const teaser = document.getElementById('event-teaser');
  if (teaser) {
    fetch('../events.json')
      .then((r) => r.json())
      .then((data) => {
        const events = (data.events || []).filter((e) => e.date && new Date(e.date) >= new Date());
        events.sort((a, b) => new Date(a.date) - new Date(b.date));
        const next = events[0];
        if (!next) return;
        const titleEl = teaser.querySelector('.event-title');
        const metaEl = teaser.querySelector('.event-meta');
        const btn = teaser.querySelector('a.btn');
        titleEl.textContent = next.title;
        const dateStr = new Date(next.date + 'T00:00:00').toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
        metaEl.textContent = `${dateStr} • ${next.venue}`;
        btn.href = next.ticketsUrl || '#';
        btn.target = '_blank';
        btn.rel = 'noopener noreferrer';
      })
      .catch(() => {
        // leave teaser as-is on error
      });
  }

  // Full Events page rendering
  const eventsList = document.getElementById('events-list');
  if (eventsList) {
    fetch('../events.json')
      .then((r) => r.json())
      .then((data) => {
        const events = (data.events || []).filter((e) => e.date && new Date(e.date) >= new Date());
        events.sort((a, b) => new Date(a.date) - new Date(b.date));
        const frag = document.createDocumentFragment();
        const ld = [];
        events.forEach((e) => {
          const card = document.createElement('article');
          card.className = 'event-card';

          const info = document.createElement('div');
          const title = document.createElement('div');
          title.className = 'event-title';
          title.textContent = e.title;
          const meta = document.createElement('div');
          meta.className = 'event-meta';
          const dateStr = new Date(e.date + 'T00:00:00').toLocaleDateString(undefined, { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
          meta.textContent = `${dateStr} • ${e.city} • ${e.venue}`;
          info.appendChild(title);
          info.appendChild(meta);

          const cta = document.createElement('a');
          cta.className = 'btn btn-primary';
          cta.href = e.ticketsUrl || '#';
          cta.target = '_blank';
          cta.rel = 'noopener noreferrer';
          cta.textContent = 'Get Tickets';

          card.appendChild(info);
          card.appendChild(cta);
          frag.appendChild(card);

          // JSON-LD Event schema
          ld.push({
            '@context': 'https://schema.org',
            '@type': 'Event',
            'name': e.title,
            'startDate': e.date,
            'eventAttendanceMode': 'https://schema.org/OfflineEventAttendanceMode',
            'eventStatus': 'https://schema.org/EventScheduled',
            'location': {
              '@type': 'Place',
              'name': e.venue,
              'address': e.city
            },
            'performer': {
              '@type': 'MusicGroup',
              'name': 'MoneyPrinter G'
            },
            'offers': e.ticketsUrl ? {
              '@type': 'Offer',
              'url': e.ticketsUrl,
              'availability': 'https://schema.org/InStock'
            } : undefined
          });
        });
        eventsList.appendChild(frag);
        if (ld.length) {
          const script = document.createElement('script');
          script.type = 'application/ld+json';
          script.textContent = JSON.stringify(ld, null, 2);
          document.head.appendChild(script);
        }
      })
      .catch(() => {
        const msg = document.createElement('div');
        msg.textContent = 'Unable to load events.';
        eventsList.appendChild(msg);
      });
  }
  // ===== Header Enhancements =====
  (function headerEnhancements() {
    const header = document.querySelector('.site-header');
    if (!header) return;

    // Active link on scroll for anchors
    const navLinks = Array.from(document.querySelectorAll('a[data-nav]'));
    const sectionIds = navLinks.map((a) => a.getAttribute('href') || '').filter((h) => h.startsWith('#'));
    const sections = sectionIds.map((id) => document.querySelector(id)).filter(Boolean);
    const activeClass = 'active';
    if (sections.length) {
      const secObs = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          const id = '#' + (entry.target.id || '');
          const link = navLinks.find((a) => a.getAttribute('href') === id);
          if (!link) return;
          if (entry.isIntersecting) {
            navLinks.forEach((l) => { l.classList.remove(activeClass); l.removeAttribute('aria-current'); });
            link.classList.add(activeClass);
            link.setAttribute('aria-current', 'true');
          }
        });
      }, { threshold: 0.4 });
      sections.forEach((s) => secObs.observe(s));
    }

    // Mobile menu toggle
    const toggle = document.querySelector('.menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    if (toggle && mobileMenu) {
      const setOpen = (open) => {
        toggle.setAttribute('aria-expanded', String(open));
        mobileMenu.hidden = !open;
        document.body.style.overflow = open ? 'hidden' : '';
      };
      toggle.addEventListener('click', () => {
        const open = toggle.getAttribute('aria-expanded') === 'true';
        setOpen(!open);
      });
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') setOpen(false);
      });
    }

    // Predictive search suggestions from discography and links
    const searchInputs = Array.from(document.querySelectorAll('.search input[type="search"]'));
    if (searchInputs.length) {
      let dataset = [];
      Promise.all([
        fetch('../discography.json').then((r) => r.ok ? r.json() : { tracks: [] }).catch(() => ({ tracks: [] })),
        fetch('../links.json').then((r) => r.ok ? r.json() : { links: [] }).catch(() => ({ links: [] }))
      ]).then(([discog, links]) => {
        const titles = (discog.tracks || []).map((t) => ({ label: t.title, url: (t.platforms && t.platforms.youtube) || '#' }));
        const more = (links.links || []).map((l) => ({ label: l.title, url: l.final_url || l.url || '#' }));
        dataset = titles.concat(more);
      });

      searchInputs.forEach((input) => {
        const list = input.parentElement.querySelector('.search-suggestions');
        let idx = -1; // keyboard selection index

        const render = (items) => {
          if (!list) return;
          list.innerHTML = '';
          items.slice(0, 6).forEach((it, i) => {
            const li = document.createElement('li');
            li.textContent = it.label;
            li.setAttribute('role', 'option');
            li.addEventListener('click', () => { window.open(it.url, '_blank'); hide(); });
            if (i === idx) li.setAttribute('aria-selected', 'true');
            list.appendChild(li);
          });
          list.style.display = items.length ? 'block' : 'none';
        };
        const hide = () => { if (list) list.style.display = 'none'; idx = -1; };

        input.addEventListener('input', () => {
          const q = input.value.trim().toLowerCase();
          if (!q) { hide(); return; }
          const filtered = dataset.filter((d) => d.label && d.label.toLowerCase().includes(q));
          idx = -1; render(filtered);
        });
        input.addEventListener('keydown', (e) => {
          const items = Array.from((list || document.createElement('ul')).querySelectorAll('li'));
          if (e.key === 'ArrowDown') { idx = Math.min(idx + 1, items.length - 1); e.preventDefault(); render(items.map((li) => ({ label: li.textContent, url: dataset.find((d) => d.label === li.textContent)?.url })) ); }
          else if (e.key === 'ArrowUp') { idx = Math.max(idx - 1, 0); e.preventDefault(); render(items.map((li) => ({ label: li.textContent, url: dataset.find((d) => d.label === li.textContent)?.url })) ); }
          else if (e.key === 'Enter') {
            const sel = items[idx];
            const label = sel ? sel.textContent : input.value;
            const match = dataset.find((d) => d.label && (d.label.toLowerCase() === label.toLowerCase() || d.label.toLowerCase().includes(label.toLowerCase())));
            if (match) window.open(match.url, '_blank');
            hide();
          } else if (e.key === 'Escape') { hide(); }
        });
        document.addEventListener('click', (evt) => {
          if (!input.parentElement.contains(evt.target)) hide();
        });
      });
    }

    // Language selector
    const langSel = document.querySelector('.language-selector');
    if (langSel) {
      langSel.addEventListener('change', () => {
        document.documentElement.lang = langSel.value || 'en';
      });
    }

    // Variant B: shrink header on scroll
    if (header.classList.contains('variant-b')) {
      const onScroll = () => {
        if (window.scrollY > 80) header.classList.add('shrink'); else header.classList.remove('shrink');
      };
      addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    }

    // Variant C: mega-menu panels
    if (header.classList.contains('variant-c')) {
      const triggers = Array.from(header.querySelectorAll('.has-panel > button'));
      triggers.forEach((btn) => {
        const panel = btn.parentElement.querySelector('.menu-panel');
        if (!panel) return;
        const setOpen = (open) => {
          btn.setAttribute('aria-expanded', String(open));
          panel.style.display = open ? 'block' : 'none';
        };
        btn.addEventListener('click', () => {
          const open = btn.getAttribute('aria-expanded') === 'true';
          // Close others
          triggers.forEach((b) => { if (b !== btn) { const p = b.parentElement.querySelector('.menu-panel'); b.setAttribute('aria-expanded', 'false'); if (p) p.style.display = 'none'; } });
          setOpen(!open);
        });
        document.addEventListener('click', (e) => {
          if (!btn.parentElement.contains(e.target)) setOpen(false);
        });
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setOpen(false); });
      });
    }
  }());
}());