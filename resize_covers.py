import os
import json
import shutil
from datetime import datetime
from PIL import Image, ImageOps
try:
    from PIL import ImageCms
    HAS_CMS = True
except Exception:
    HAS_CMS = False

# Configuration — chosen to meet your requirements
TARGET_WIDTH = 500   # pixels
TARGET_HEIGHT = 500  # pixels
MAINTAIN_ASPECT = True  # use cover-fit with center crop to exact size
OUTPUT_FORMAT = 'preserve'  # 'preserve' keeps original format per file
JPEG_QUALITY = 92  # percent
JPEG_SUBSAMPLING = 0  # 4:4:4 to avoid chroma softness
PNG_COMPRESS_LEVEL = 6  # 0-9, Pillow default ~6
CONVERT_TO_SRGB = True  # ensure consistent web color

COVERS_DIR = os.path.abspath('covers')
BACKUP_DIR = os.path.join(COVERS_DIR, '_backup_resized_originals')
REPORT_PATH = os.path.join(COVERS_DIR, 'resize_report.json')

VALID_EXTS = {'.png', '.jpg', '.jpeg'}


def ensure_dirs():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def get_srgb_profile_bytes():
    if not CONVERT_TO_SRGB or not HAS_CMS:
        return None
    try:
        srgb = ImageCms.createProfile('sRGB')
        return srgb.tobytes()
    except Exception:
        return None


SRGB_BYTES = get_srgb_profile_bytes()


def load_image(path):
    img = Image.open(path)
    img.load()
    return img


def convert_to_srgb(img):
    if not CONVERT_TO_SRGB:
        return img, None
    if not HAS_CMS:
        # Fallback: simply ensure an RGB/RGBA mode
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
        return img, None
    try:
        # If ICC present, attempt transform to sRGB
        icc = img.info.get('icc_profile')
        if icc:
            src = ImageCms.getOpenProfile(io.BytesIO(icc))
            dst = ImageCms.createProfile('sRGB')
            intent = ImageCms.INTENT_PERCEPTUAL
            img = ImageCms.profileToProfile(img, src, dst, renderingIntent=intent, outputMode='RGB')
            return img, dst.tobytes()
        else:
            # No ICC; just convert to RGB
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            return img, SRGB_BYTES
    except Exception:
        # Robust fallback
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
        return img, SRGB_BYTES


def resize_exact(img):
    # Use high-quality LANCZOS for resizing; center crop to exact target
    size = (TARGET_WIDTH, TARGET_HEIGHT)
    method = Image.LANCZOS
    if MAINTAIN_ASPECT:
        # Fit to cover, cropping as needed
        return ImageOps.fit(img, size, method=method, centering=(0.5, 0.5))
    else:
        # Distort to exact size (not recommended)
        return img.resize(size, resample=method)


def save_image(img, dest_path, orig_ext, srgb_bytes):
    ext = orig_ext.lower()
    fmt = None
    params = {}

    if OUTPUT_FORMAT == 'preserve':
        if ext == '.png':
            fmt = 'PNG'
            params = {
                'optimize': True,
                'compress_level': PNG_COMPRESS_LEVEL,
            }
            # PNG can embed ICC profile in newer Pillow; if fails, ignore
            if srgb_bytes:
                params['icc_profile'] = srgb_bytes
        else:
            fmt = 'JPEG'
            # Ensure no alpha in JPEG
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            params = {
                'quality': JPEG_QUALITY,
                'subsampling': JPEG_SUBSAMPLING,
                'optimize': True,
                'progressive': True,
            }
            if srgb_bytes:
                params['icc_profile'] = srgb_bytes
    elif OUTPUT_FORMAT.upper() == 'PNG':
        fmt = 'PNG'
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
        params = {
            'optimize': True,
            'compress_level': PNG_COMPRESS_LEVEL,
        }
        if srgb_bytes:
            params['icc_profile'] = srgb_bytes
    else:
        fmt = 'JPEG'
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        params = {
            'quality': JPEG_QUALITY,
            'subsampling': JPEG_SUBSAMPLING,
            'optimize': True,
            'progressive': True,
        }
        if srgb_bytes:
            params['icc_profile'] = srgb_bytes

    img.save(dest_path, format=fmt, **params)
    return fmt


def process_file(path, rel):
    name = os.path.basename(path)
    root, ext = os.path.splitext(name)

    # Skip backups and metadata files explicitly
    if rel.startswith('_backup_originals') or name.lower() in {'metadata.json'}:
        return None

    # Backup original
    backup_path = os.path.join(BACKUP_DIR, name)
    if not os.path.exists(backup_path):
        shutil.copy2(path, backup_path)

    # Load, convert color, resize
    img = load_image(path)
    img, icc_bytes = convert_to_srgb(img)
    resized = resize_exact(img)

    # Save back to original path (preserving extension)
    fmt = save_image(resized, path, ext, icc_bytes or SRGB_BYTES)

    # Validation
    valid = True
    issues = []
    try:
        chk = load_image(path)
        w, h = chk.size
        if (w, h) != (TARGET_WIDTH, TARGET_HEIGHT):
            valid = False
            issues.append(f'Dimension mismatch: got {w}x{h}')
        # Format check
        if fmt == 'PNG' and chk.format != 'PNG':
            valid = False
            issues.append(f'Format mismatch: expected PNG, got {chk.format}')
        if fmt == 'JPEG' and chk.format != 'JPEG':
            valid = False
            issues.append(f'Format mismatch: expected JPEG, got {chk.format}')
        # Color profile presence (best-effort)
        icc_present = bool(chk.info.get('icc_profile'))
    except Exception as e:
        valid = False
        issues.append(f'Validation error: {e}')
        w = h = None
        icc_present = False

    return {
        'file': rel,
        'original_ext': ext,
        'format_saved': fmt,
        'width': w,
        'height': h,
        'icc_profile_embedded': icc_present,
        'validation_passed': valid,
        'issues': issues,
        'size_bytes': os.path.getsize(path),
    }


def main():
    ensure_dirs()
    report = {
        'run_at': datetime.utcnow().isoformat() + 'Z',
        'target': {
            'width': TARGET_WIDTH,
            'height': TARGET_HEIGHT,
            'maintain_aspect': MAINTAIN_ASPECT,
            'output_format': OUTPUT_FORMAT,
            'jpeg_quality': JPEG_QUALITY,
            'png_compress_level': PNG_COMPRESS_LEVEL,
            'convert_to_srgb': CONVERT_TO_SRGB,
        },
        'results': [],
    }

    for root, dirs, files in os.walk(COVERS_DIR):
        # Skip backup directories
        if os.path.basename(root) in {'_backup_originals', '_backup_resized_originals'}:
            continue
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in VALID_EXTS:
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, COVERS_DIR)
                res = process_file(full, rel)
                if res:
                    report['results'].append(res)

    # Aggregate validation status
    report['summary'] = {
        'total': len(report['results']),
        'passed': sum(1 for r in report['results'] if r['validation_passed']),
        'failed': sum(1 for r in report['results'] if not r['validation_passed']),
    }

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Resize completed. Report written to: {REPORT_PATH}")
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()