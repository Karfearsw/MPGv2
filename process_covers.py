from pathlib import Path
from PIL import Image
import shutil
import json
import time

COVERS_DIR = Path(r"c:\Users\Stack\Documents\trae_projects\moneyprinterg\covers")
BACKUP_DIR = COVERS_DIR / "_backup_originals"
METADATA_JSON = COVERS_DIR / "metadata.json"

MIN_SIZE = 1000  # minimum width and height


def ensure_backup_dir():
    BACKUP_DIR.mkdir(exist_ok=True)


def upscale_if_needed(img_path: Path):
    with Image.open(img_path) as im:
        im.load()
        w, h = im.size
        fmt = (im.format or "").upper()
        original = {"width": w, "height": h, "format": fmt}

        # Determine if upscaling is needed
        if w >= MIN_SIZE and h >= MIN_SIZE:
            # Optionally optimize and resave to improve load performance
            save_kwargs = {}
            if fmt == "JPEG" or img_path.suffix.lower() in (".jpg", ".jpeg"):
                save_kwargs = {"quality": 85, "optimize": True, "subsampling": 0}
            else:
                save_kwargs = {"optimize": True}
            im.save(img_path, **save_kwargs)
            return {"changed": False, **original, "width": w, "height": h}

        # Compute scale to make both dimensions >= MIN_SIZE
        scale = max(MIN_SIZE / w, MIN_SIZE / h)
        new_w = int(round(w * scale))
        new_h = int(round(h * scale))

        # Backup original
        backup_path = BACKUP_DIR / img_path.name
        if not backup_path.exists():
            shutil.copy2(img_path, backup_path)

        # Resize with high-quality filter
        up = im.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Save optimized
        save_kwargs = {}
        if fmt == "JPEG" or img_path.suffix.lower() in (".jpg", ".jpeg"):
            save_kwargs = {"quality": 85, "optimize": True, "subsampling": 0}
        else:
            save_kwargs = {"optimize": True}
        up.save(img_path, **save_kwargs)

        return {
            "changed": True,
            **original,
            "width": new_w,
            "height": new_h,
            "format": fmt or ("JPEG" if img_path.suffix.lower() in (".jpg", ".jpeg") else "PNG"),
        }


def main():
    ensure_backup_dir()
    meta = []
    for p in sorted(COVERS_DIR.iterdir()):
        if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg"):
            info = upscale_if_needed(p)
            info.update({"filename": p.name})
            meta.append(info)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    METADATA_JSON.write_text(json.dumps({"updatedAt": now, "covers": meta}, indent=2), encoding="utf-8")
    print("Processed", len(meta), "images. Metadata written to", METADATA_JSON)


if __name__ == "__main__":
    main()