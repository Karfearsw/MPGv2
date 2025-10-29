import re
import json
import time
from pathlib import Path
import requests

ROOT = Path(r"c:\Users\Stack\Documents\trae_projects\moneyprinterg")
LINKS_JSON = ROOT / "links.json"
COVERS_DIR = ROOT / "covers"
OUTPUT = ROOT / "discography.json"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", re.sub(r"_mpg$", "", s.lower()))


def title_from_filename(name: str) -> str:
    base = re.sub(r"\.(png|jpe?g)$", "", name, flags=re.I)
    base = re.sub(r"_mpg$", "", base, flags=re.I)
    base = base.replace("_", " ")
    return re.sub(r"\b(\w)", lambda m: m.group(1).upper(), base)


def get_youtube_publish_date(url: str):
    try:
        r = session.get(url, timeout=20)
        if r.status_code >= 400:
            return None
        html = r.text
        # Try itemprop meta tag
        m = re.search(r'<meta itemprop="datePublished" content="(.*?)"', html)
        if m:
            return m.group(1)
        # Try JSON field publishDate
        m2 = re.search(r'"publishDate":"(\d{4}-\d{2}-\d{2})"', html)
        if m2:
            return m2.group(1)
        return None
    except Exception:
        return None


def build():
    links = json.loads(LINKS_JSON.read_text(encoding="utf-8"))
    link_map = {}
    for entry in links.get("links", []):
        t = entry.get("title", "")
        u = entry.get("final_url", entry.get("url"))
        if t and u:
            link_map[norm(t)] = u

    tracks = []
    for p in sorted(COVERS_DIR.iterdir()):
        if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg") and not p.name.startswith("_"):
            title = title_from_filename(p.name)
            key = norm(p.name)
            yt = link_map.get(key)
            date = get_youtube_publish_date(yt) if yt else None
            track = {
                "title": title,
                "cover": f"covers/{p.name}",
                "releaseDate": date,  # ISO YYYY-MM-DD or None
                "platforms": {
                    "youtube": yt,
                    "spotify": f"https://open.spotify.com/search/{requests.utils.quote('MoneyPrinter G ' + title)}",
                    "apple": f"https://music.apple.com/us/search?term={requests.utils.quote('MoneyPrinter G ' + title)}",
                    "hyperfollow": "https://hyperfollow.com/moneyprinterg"
                },
                "credits": {
                    "artist": "MoneyPrinter G",
                    "producer": "Unknown",
                    "writers": ["MoneyPrinter G"],
                    "label": "Independent"
                }
            }
            tracks.append(track)

    # Sort chronologically; None dates last
    tracks.sort(key=lambda t: (t["releaseDate"] is None, t["releaseDate"] or "9999-12-31"))

    OUTPUT.write_text(json.dumps({"updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "tracks": tracks}, indent=2), encoding="utf-8")
    print("Wrote", len(tracks), "tracks to", OUTPUT)


if __name__ == "__main__":
    build()