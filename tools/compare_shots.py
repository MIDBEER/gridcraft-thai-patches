"""Put two screenshots side by side, captioned, for a before/after look.

    python compare_shots.py before.png after.png out.png [crop=left,top,right,bottom]

The optional crop (pixels, applied to both inputs) zooms into the cells. Needs Pillow.
"""
import sys

from PIL import Image, ImageDraw


def main(argv):
    if len(argv) not in (4, 5):
        print(__doc__)
        return 2
    before_path, after_path, out_path = argv[1:4]
    crop = None
    if len(argv) == 5:
        key, _, value = argv[4].partition("=")
        if key != "crop":
            print(__doc__)
            return 2
        crop = tuple(int(v) for v in value.split(","))
        if len(crop) != 4:
            print(__doc__)
            return 2

    images = []
    for path in (before_path, after_path):
        img = Image.open(path).convert("RGB")
        images.append(img.crop(crop) if crop else img)

    gap, band = 16, 28
    width = sum(i.width for i in images) + gap * 3
    height = max(i.height for i in images) + band + gap * 2
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    x = gap
    for caption, img in zip(("upstream (before)", "patched (after)"), images):
        draw.text((x, gap // 2), caption, fill="black")
        canvas.paste(img, (x, band + gap // 2))
        x += img.width + gap
    canvas.save(out_path)
    print(f"saved {out_path} {canvas.width}x{canvas.height}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
