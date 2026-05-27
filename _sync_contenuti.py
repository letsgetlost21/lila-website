#!/usr/bin/env python3
"""
Sync immagini da 'contenuti sito Lila' verso 'assets/' del sito.
- Center crop al rapporto target
- Resize al lato lungo target
- Salva come PNG ottimizzato
"""
from pathlib import Path
from PIL import Image

CONTENT_DIR = Path("/Users/letsgetlost/Downloads/contenuti sito Lila")
SITE_DIR = Path("/Users/letsgetlost/Downloads/Lila Website (1)")
ASSETS_DIR = SITE_DIR / "assets"

# (source_folder, target_file, aspect_ratio (w,h), long_edge_px)
MAPPING = {
    "01_label_design/aman_bangkok":              ("p04_1.png", (5, 7), 1680),
    "01_label_design/rosewood_chancery":         ("p05_1.png", (5, 7), 1680),
    "01_label_design/aeromexico_label":          ("p06_1.png", (5, 7), 1680),
    "01_label_design/belmond_casole":            ("p07_1.png", (5, 7), 1680),
    "01_label_design/castiglion_bosco":          ("p08_1.png", (5, 7), 1680),
    "01_label_design/bocktailed_lattine":        ("p09_1.png", (5, 7), 1680),
    "02_advertising/Coqtail":                    ("p11_1.png", (5, 4), 2400),
    "03_creative_direction/seibellissimi_doc":   ("p13_1.png", (5, 4), 2400),
    "03_creative_direction/seibellissimi_com":   ("p14_1.png", (5, 4), 2400),
    "03_creative_direction/bocktailed_shoot":    ("p15_1.png", (1, 1), 1800),
    "03_creative_direction/ratafia_shoot":       ("p17_1.png", (1, 1), 1800),
    "03_creative_direction/seibellissimi_shoot": ("p19_1.png", (1, 1), 1800),
    "03_creative_direction/mancino_shoot":       ("p21_1.png", (1, 1), 1800),
    "03_creative_direction/rinomato_shoot":      ("p23_1.png", (1, 1), 1800),
    "04_brand_identity/anto_singapore":          ("p27_1.png", (5, 4), 2400),
    "04_brand_identity/samset_rome":             ("p28_1.png", (5, 4), 2400),
    "05_social_media/seibellissimi_grid":        ("p30_1.png", (1, 1), 1800),
    "05_social_media/anto_grid":                 ("p30_2.png", (1, 1), 1800),
    "05_social_media/bocktailed_grid":           ("p30_3.png", (1, 1), 1800),
    "05_social_media/ratafia_grid":              ("p30_4.png", (1, 1), 1800),
    "05_social_media/mancino_grid":              ("p30_5.png", (1, 1), 1800),
}

FOUNDERS = {
    "06_founders/Michela_Mancino.png":   ("founder_michela.png",   (1, 1), 512),
    "06_founders/Cristiano_Demurtas.png": ("founder_cristiano.png", (1, 1), 512),
}

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}


def find_first_image(folder: Path):
    if not folder.exists():
        return None
    files = sorted(f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in IMG_EXTS)
    if not files:
        return None
    # Prefer file starting with "01_" if exists; otherwise first
    main = next((f for f in files if f.name.startswith("01_")), files[0])
    return main


def crop_to_aspect(img: Image.Image, ratio):
    tw, th = ratio
    target = tw / th
    cur = img.width / img.height
    if abs(cur - target) < 0.001:
        return img
    if cur > target:
        new_w = int(round(img.height * target))
        left = (img.width - new_w) // 2
        return img.crop((left, 0, left + new_w, img.height))
    else:
        new_h = int(round(img.width / target))
        top = (img.height - new_h) // 2
        return img.crop((0, top, img.width, top + new_h))


def resize_long_edge(img: Image.Image, long_edge: int):
    if max(img.width, img.height) <= long_edge:
        return img
    if img.width >= img.height:
        nw = long_edge
        nh = int(round(img.height * long_edge / img.width))
    else:
        nh = long_edge
        nw = int(round(img.width * long_edge / img.height))
    return img.resize((nw, nh), Image.LANCZOS)


def process(src: Path, dst: Path, ratio, long_edge):
    img = Image.open(src)
    if img.mode == "P":
        img = img.convert("RGBA")
    elif img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    cropped = crop_to_aspect(img, ratio)
    final = resize_long_edge(cropped, long_edge)
    dst.parent.mkdir(parents=True, exist_ok=True)
    final.save(dst, "PNG", optimize=True)
    print(f"  ✓ {src.name:<50s} → {dst.name:<22s} ({final.width}×{final.height})")


def main():
    print("=" * 80)
    print(f"Source: {CONTENT_DIR}")
    print(f"Target: {ASSETS_DIR}")
    print("=" * 80)
    processed = skipped = 0
    for src_folder, (target_name, ratio, long_edge) in MAPPING.items():
        src_dir = CONTENT_DIR / src_folder
        img = find_first_image(src_dir)
        if not img:
            print(f"⚠ SKIP {src_folder}: nessuna immagine trovata")
            skipped += 1
            continue
        process(img, ASSETS_DIR / target_name, ratio, long_edge)
        processed += 1
    print("-" * 80)
    for src_file, (target_name, ratio, long_edge) in FOUNDERS.items():
        src_path = CONTENT_DIR / src_file
        if not src_path.exists():
            print(f"⚠ SKIP {src_file}: file mancante")
            skipped += 1
            continue
        process(src_path, ASSETS_DIR / target_name, ratio, long_edge)
        processed += 1
    print("=" * 80)
    print(f"Fatto. Processati: {processed}  Saltati: {skipped}")


if __name__ == "__main__":
    main()
