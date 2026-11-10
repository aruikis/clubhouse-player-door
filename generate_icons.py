#!/usr/bin/env python3
"""Generate the Clubhouse Player Door icons.

Midnight Brass: near-black #0c0c0e field, an elegant double brass
ring, and a club motif in layered brass tones. No text — at icon
sizes, lettering would only smudge. Run: python3 generate_icons.py
"""
from PIL import Image, ImageDraw
import os

BG = (12, 12, 14)          # #0c0c0e
BRASS = (201, 164, 92)     # #c9a45c
BRASS_BRIGHT = (236, 210, 141)  # #ecd28d
BRASS_DIM = (138, 109, 51)      # #8a6d33

HERE = os.path.dirname(os.path.abspath(__file__))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_icon(size, motif_scale):
    """motif_scale < 1 leaves safe padding (maskable icons)."""
    img = Image.new("RGB", (size, size), BG)
    d = ImageDraw.Draw(img, "RGBA")
    cx = cy = size / 2.0
    R = (size / 2.0) * motif_scale

    # Soft warm glow rising from the bottom (the Door's signature hue).
    glow_steps = 48
    for i in range(glow_steps):
        t = i / glow_steps
        y = size - (size * 0.55) * t
        alpha = int(26 * (1 - t))
        if alpha <= 0:
            continue
        d.line([(0, y), (size, y)], fill=(201, 140, 60, alpha), width=max(1, int(size / glow_steps) + 1))

    # Double brass ring, drawn in stacked passes for a gentle sheen.
    def ring(radius, width, color):
        d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=color, width=width)

    outer_r = R * 0.94
    ring(outer_r, max(2, int(size * 0.016)), BRASS_DIM)
    ring(outer_r - size * 0.012, max(2, int(size * 0.030)), BRASS)
    ring(outer_r - size * 0.030, max(1, int(size * 0.010)), BRASS_BRIGHT)
    inner_r = outer_r - size * 0.062
    ring(inner_r, max(1, int(size * 0.008)), BRASS_DIM)

    # Club motif: three circles + a stem, solid brass with a soft
    # light from the upper left.
    cr = R * 0.29  # circle radius of the club's lobes
    base = cy + R * 0.04
    lobes = [(cx, base - cr * 1.02), (cx - cr * 0.94, base + cr * 0.44), (cx + cr * 0.94, base + cr * 0.44)]
    stem_top = base + cr * 0.55
    stem_bot = base + cr * 1.52
    stem_half = cr * 0.28
    d.polygon([(cx - stem_half, stem_top), (cx + stem_half, stem_top),
               (cx + stem_half * 1.8, stem_bot), (cx - stem_half * 1.8, stem_bot)], fill=BRASS_DIM)
    for (x, y) in lobes:
        d.ellipse([x - cr, y - cr, x + cr, y + cr], fill=BRASS)
    # Sheen: one soft translucent highlight per lobe, upper left.
    hl = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    for (x, y) in lobes:
        r2 = cr * 0.52
        ox, oy = x - cr * 0.30, y - cr * 0.34
        hd.ellipse([ox - r2, oy - r2, ox + r2, oy + r2], fill=(236, 210, 141, 72))
    img.paste(Image.alpha_composite(img.convert("RGBA"), hl).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    return img


def main():
    targets = [
        ("icon-192.png", 192, 0.96),
        ("icon-512.png", 512, 0.96),
        ("icon-maskable-512.png", 512, 0.78),  # safe-zone padding for maskable
        ("apple-touch-icon.png", 180, 0.94),
    ]
    for name, size, scale in targets:
        img = draw_icon(size, scale)
        img.save(os.path.join(HERE, name), "PNG")
        print("wrote", name, img.size)


if __name__ == "__main__":
    main()
