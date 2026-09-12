"""
Annotate the LEGO train photo with component labels.

Run this script to regenerate lego_train_annotated.png:

    python scripts/annotate_train.py

Coordinates below are pixel coordinates measured on the original
lego_train.jpg (1376 x 1033) and are rescaled automatically if the
source photo is ever replaced by a differently sized one.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---
HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_IMAGE = os.path.join(HERE, "..", "lego_train.jpg")
OUTPUT_IMAGE = os.path.join(HERE, "..", "lego_train_annotated.png")

# Size of the photo the coordinates below were measured on.
REF_WIDTH, REF_HEIGHT = 1376, 1033

# Each annotation has:
#   rect    - box around the component itself (x0, y0, x1, y1)
#   anchor  - point on the component the leader line points at
#   label   - (x, y) corner of the text box, plus align: "left" or "right"
#             ("right" means x is the *right* edge of the text box)
ANNOTATIONS = [
    {
        "n": "1",
        "title": "Power bank",
        "subtitle": "roof of carriage 1 - 5V supply for the Pi",
        "color": (255, 176, 32),
        "rect": (444, 124, 794, 248),
        "anchor": (452, 170),
        "label": (20, 16),
        "align": "left",
    },
    {
        "n": "2",
        "title": "Raspberry Pi Camera",
        "subtitle": "nose of carriage 1 - looks down the track",
        "color": (0, 194, 255),
        "rect": (324, 416, 376, 484),
        "anchor": (348, 486),
        "label": (24, 566),
        "align": "left",
    },
    {
        "n": "3",
        "title": "Raspberry Pi",
        "subtitle": "inside carriage 1 - brain of the train",
        "color": (255, 72, 120),
        "rect": (568, 356, 708, 460),
        "anchor": (640, 462),
        "label": (440, 706),
        "align": "left",
    },
    {
        "n": "4",
        "title": "LEGO train motor",
        "subtitle": "front of carriage 2 - driven over Bluetooth",
        "color": (64, 222, 128),
        "rect": (948, 232, 1086, 482),
        "anchor": (1012, 484),
        "label": (1352, 566),
        "align": "right",
    },
]

BOX_FILL = (22, 25, 30, 232)
PAD_X, PAD_Y = 18, 14
GAP = 6  # gap between title and subtitle


def load_fonts(scale):
    """Return (title_font, subtitle_font, badge_font), falling back gracefully."""

    def pick(names, size):
        for name in names:
            try:
                return ImageFont.truetype(name, size)
            except (OSError, IOError):
                continue
        return ImageFont.load_default()

    bold = ["arialbd.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf"]
    regular = ["arial.ttf", "DejaVuSans.ttf", "Arial.ttf"]
    return (
        pick(bold, max(12, int(28 * scale))),
        pick(regular, max(10, int(21 * scale))),
        pick(bold, max(11, int(24 * scale))),
    )


def create_annotated_image():
    image = Image.open(INPUT_IMAGE).convert("RGBA")
    width, height = image.size
    sx, sy = width / REF_WIDTH, height / REF_HEIGHT
    scale = min(sx, sy)

    title_font, sub_font, badge_font = load_fonts(scale)

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    line_w = max(2, int(4 * scale))
    badge_r = max(10, int(19 * scale))

    for ann in ANNOTATIONS:
        color = ann["color"]
        opaque = color + (255,)

        x0, y0, x1, y1 = ann["rect"]
        x0, x1 = x0 * sx, x1 * sx
        y0, y1 = y0 * sy, y1 * sy

        # Highlight the component: tinted fill + bright outline.
        draw.rounded_rectangle(
            [x0, y0, x1, y1],
            radius=max(4, int(10 * scale)),
            fill=color + (20,),
            outline=opaque,
            width=line_w,
        )

        # --- Measure the label box ---
        t_bbox = draw.textbbox((0, 0), ann["title"], font=title_font)
        s_bbox = draw.textbbox((0, 0), ann["subtitle"], font=sub_font)
        title_h = t_bbox[3] - t_bbox[1]
        sub_h = s_bbox[3] - s_bbox[1]
        text_w = max(t_bbox[2] - t_bbox[0], s_bbox[2] - s_bbox[0])

        pad_x, pad_y = PAD_X * scale, PAD_Y * scale
        badge_gap = badge_r * 2 + 12 * scale
        box_w = text_w + badge_gap + pad_x * 2
        box_h = title_h + sub_h + GAP * scale + pad_y * 2

        lx, ly = ann["label"][0] * sx, ann["label"][1] * sy
        bx0 = lx - box_w if ann["align"] == "right" else lx
        by0 = ly
        bx1, by1 = bx0 + box_w, by0 + box_h

        # --- Leader line: from the closest edge/corner of the label box ---
        ax, ay = ann["anchor"][0] * sx, ann["anchor"][1] * sy
        start_x = min(max(ax, bx0 + badge_gap), bx1 - pad_x)
        start_y = by1 if ay > by1 else by0 if ay < by0 else (by0 + by1) / 2
        if by0 <= ay <= by1:
            start_x = bx1 if ax > bx1 else bx0

        draw.line([(start_x, start_y), (ax, ay)], fill=opaque, width=line_w)
        dot = max(3, int(6 * scale))
        draw.ellipse([ax - dot, ay - dot, ax + dot, ay + dot], fill=opaque)

        # --- Label box ---
        draw.rounded_rectangle(
            [bx0, by0, bx1, by1],
            radius=max(5, int(12 * scale)),
            fill=BOX_FILL,
            outline=opaque,
            width=max(2, int(3 * scale)),
        )

        # Numbered badge, inside the label box and on the component box.
        for cx, cy in ((bx0 + pad_x + badge_r, (by0 + by1) / 2), (x0, y0)):
            draw.ellipse(
                [cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r],
                fill=opaque,
                outline=(255, 255, 255, 235),
                width=max(1, int(2 * scale)),
            )
            draw.text(
                (cx, cy - badge_r * 0.08),
                ann["n"],
                font=badge_font,
                fill=(20, 20, 20, 255),
                anchor="mm",
            )

        # Text
        tx = bx0 + pad_x + badge_gap
        draw.text((tx, by0 + pad_y - t_bbox[1]), ann["title"], font=title_font, fill=(255, 255, 255, 255))
        draw.text(
            (tx, by0 + pad_y + title_h + GAP * scale - s_bbox[1]),
            ann["subtitle"],
            font=sub_font,
            fill=(214, 218, 224, 255),
        )

    annotated = Image.alpha_composite(image, overlay).convert("RGB")
    annotated.save(OUTPUT_IMAGE, "PNG")
    print(f"Annotated image saved to: {os.path.normpath(OUTPUT_IMAGE)}")


if __name__ == "__main__":
    create_annotated_image()
