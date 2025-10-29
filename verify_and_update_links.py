import re
import json
import time
from pathlib import Path
import requests

LINKS_PATH = Path(r"c:\Users\Stack\Documents\trae_projects\moneyprinterg\MoneyPrinter G link.txt")
OUTPUT_JSON = Path(r"c:\Users\Stack\Documents\trae_projects\moneyprinterg\links.json")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def parse_links(text: str):
    lines = [l.strip() for l in text.splitlines()]
    pairs = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("http"):
            url = line
            # fix a common duplication issue (two https... concatenated)
            if url.count("https://www.youtube.com") > 1:
                first = url.find("https://www.youtube.com")
                second = url.find("https://www.youtube.com", first + 1)
                url = url[:second]
            # find next non-empty line as title
            j = i + 1
            title = None
            while j < len(lines):
                if lines[j]:
                    title = lines[j]
                    break
                j += 1
            if title:
                pairs.append({"title": title, "url": url})
                i = j + 1
            else:
                # URL with no title (artist pages at end)
                pairs.append({"title": "Untitled", "url": url})
                i += 1
        else:
            i += 1
    # Append explicit artist links if present but not parsed with titles
    if "apple.com" in text and not any("Apple Music" in p["title"] for p in pairs):
        # Find Apple link
        m = re.search(r"(https://music\.apple\.com/\S+)", text)
        if m:
            pairs.append({"title": "Apple Music (Artist)", "url": m.group(1)})
    if "open.spotify.com" in text and not any("Spotify" in p["title"] for p in pairs):
        m = re.search(r"(https://open\.spotify\.com/\S+)", text)
        if m:
            pairs.append({"title": "Spotify (Artist)", "url": m.group(1)})
    return pairs


def check_url(url: str):
    try:
        # Use HEAD first; if not allowed, fall back to GET
        resp = session.head(url, allow_redirects=True, timeout=15)
        if resp.status_code >= 400 or resp.status_code == 405:
            resp = session.get(url, allow_redirects=True, timeout=20)
        ok = 200 <= resp.status_code < 300
        final_url = str(resp.url)
        return {"ok": ok, "status": resp.status_code, "final_url": final_url}
    except Exception as e:
        return {"ok": False, "status": None, "error": str(e), "final_url": url}


def main():
    raw = LINKS_PATH.read_text(encoding="utf-8")
    pairs = parse_links(raw)

    results = []
    for p in pairs:
        r = check_url(p["url"])
        results.append({**p, **r})

    # Write cleaned text back, preserving order and improving clarity
    lines_out = []
    for r in results:
        status = "OK" if r["ok"] else f"BAD ({r['status']})"
        lines_out.append(f"{r['title']}\n{r['final_url']}\nStatus: {status}\n")
    LINKS_PATH.write_text("\n".join(lines_out).strip() + "\n", encoding="utf-8")

    # Also emit structured JSON for use in the site
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    OUTPUT_JSON.write_text(json.dumps({"updatedAt": now, "links": results}, indent=2), encoding="utf-8")

    print("Processed", len(results), "links")
    bad = [r for r in results if not r["ok"]]
    if bad:
        print("WARNING: ", len(bad), "links failed HTTP 200")
        for b in bad:
            print("-", b["title"], "=>", b.get("status"), b.get("error", ""))


if __name__ == "__main__":
    main()