#!/usr/bin/env python3
"""news-image-20261126: draw a 1024x1024 newspaper front page, "THE WORLD
TODAY", summing up Thursday 26 November 2026 in six stories, using only the
Python 3 standard library. The program rasterises its own 5x7 bitmap font,
draws every picture from shapes, and encodes the PNG by hand, so two runs
write byte-identical output. No network, no external files.

Stories (all first reported on 26 Nov 2026, or developments of 25 Nov
stories that continued into 26 Nov; see README.md):
  1. Kim Jong Un calls for tactical nuclear weapons to be used across many
     missions (KCNA report, Thursday 26 Nov; the inspection was Wednesday).
  2. A third tanker, an LNG carrier, hits a mine in the Strait of Hormuz
     after two oil tankers did the same on Wednesday; reported overnight
     into 26 Nov.
  3. Macy's 100th Thanksgiving Day Parade postponed to Saturday over a
     nor'easter; announced Wednesday evening in New York, already
     Thursday in Asia, with the storm hitting on Thanksgiving Day itself.
  4. Nearly 2,000 migrants reach Spain's Canary Islands in a record
     single day.
  5. Yemen's Houthis threaten Saudi ports after a coalition strike on
     the port city of Hodeidah.
  6. Thanksgiving travel: long airport lines and bad weather across the US.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
PAPER = (253, 253, 246)
INK = (17, 17, 17)
RED = (185, 28, 28)
BLUE = (29, 78, 216)
SKY = (191, 219, 254)
SEA = (37, 99, 235)
GREY = (107, 114, 128)
LIGHTGREY = (229, 231, 235)
ORANGE = (234, 88, 12)
YELLOW = (250, 204, 21)
GREEN = (22, 163, 74)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ---------------------------------------------------------------------------
# 5x7 bitmap font, designed in this session. Each glyph is 7 rows of 5 bits.
# '#' is on, '.' is off. Only the characters the page needs are defined.
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "####.", "#...#", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", "#..##", ".####", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "&": (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.#.#", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}

# ---------------------------------------------------------------------------
# Canvas: a flat RGB bytearray, drawn with filled rectangles, lines,
# triangles, circles and the bitmap font above.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        # Filled circle, scanline by scanline.
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            for dx in range(-half, half + 1):
                self.set(cx + dx, cy + dy, color)

    def ring(self, cx, cy, r, color):
        # Circle outline, one pixel thick.
        steps = max(8, r * 8)
        for i in range(steps):
            import math
            a = 2 * math.pi * i / steps
            self.set(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Filled triangle via scanline fill between the two edge walks.
        import math
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        def interp(y, p, q):
            if q[1] == p[1]:
                return p[0]
            return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])
        for y in range(ay, cy + 1):
            if y < by:
                xa = interp(y, (ax, ay), (bx, by))
            else:
                xa = interp(y, (bx, by), (cx, cy))
            xb = interp(y, (ax, ay), (cx, cy))
            lo, hi = (xa, xb) if xa <= xb else (xb, xa)
            for x in range(int(math.ceil(lo)), int(math.floor(hi)) + 1):
                self.set(x, y, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            half = int(rx * (1 - (dy / ry) ** 2) ** 0.5)
            for dx in range(-half, half + 1):
                self.set(cx + dx, cy + dy, color)

    def burst(self, cx, cy, r, color):
        # Starburst: 12 spikes, used for explosions.
        import math
        pts = []
        for i in range(24):
            a = 2 * math.pi * i / 24
            rr = r if i % 2 == 0 else r * 0.45
            pts.append((cx + int(rr * math.cos(a)), cy + int(rr * math.sin(a))))
        for i in range(24):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % 24]
            self.triangle(cx, cy, x0, y0, x1, y1, color)

# ---------------------------------------------------------------------------
# Text: measure, wrap and draw with the bitmap font.
# A character is 5*scale wide plus 1*scale of spacing; glyphs are 7*scale tall.
# ---------------------------------------------------------------------------
def text_width(text, scale):
    return len(text) * 6 * scale - scale if text else 0


def draw_text(cv, x, y, scale, text, color):
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            cx += 6 * scale
            continue
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "#":
                    cv.rect(cx + col * scale, y + row * scale,
                            scale, scale, color)
        cx += 6 * scale
    return cx - x


def draw_text_centred(cv, cx, y, scale, text, color):
    w = text_width(text, scale)
    draw_text(cv, cx - w // 2, y, scale, text, color)


def wrap_text(text, scale, max_w):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, scale, text, color, max_w, line_h=None):
    if line_h is None:
        line_h = 8 * scale
    yy = y
    for line in wrap_text(text, scale, max_w):
        draw_text(cv, x, yy, scale, line, color)
        yy += line_h
    return yy


# ---------------------------------------------------------------------------
# PNG encoder: 8-bit RGB, no filtering, zlib level 9. Fully deterministic.
# ---------------------------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png

# ---------------------------------------------------------------------------
# Illustrations, all drawn from shapes.
# ---------------------------------------------------------------------------
def draw_missile_panel(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    cv.rect(x, y, w, 2, INK)
    cv.rect(x, y + h - 2, w, 2, INK)
    cv.rect(x, y, 2, h, INK)
    cv.rect(x + w - 2, y, 2, h, INK)
    # Clouds.
    cv.ellipse(x + 104, y + 46, 34, 12, WHITE)
    cv.ellipse(x + w - 70, y + 80, 30, 11, WHITE)
    # Red star, top left.
    cv.burst(x + 44, y + 46, 16, RED)
    # Missile, centre.
    cx = x + w // 2
    cv.triangle(cx - 15, y + 62, cx + 15, y + 62, cx, y + 26, RED)
    cv.rect(cx - 15, y + 62, 30, 150, LIGHTGREY)
    cv.rect(cx - 15, y + 62, 30, 6, GREY)
    cv.rect(cx - 15, y + 150, 30, 8, GREY)
    cv.triangle(cx - 15, y + 212, cx - 38, y + 236, cx - 15, y + 236, GREY)
    cv.triangle(cx + 15, y + 212, cx + 38, y + 236, cx + 15, y + 236, GREY)
    cv.triangle(cx - 12, y + 236, cx + 12, y + 236, cx, y + 268, ORANGE)
    cv.triangle(cx - 6, y + 236, cx + 6, y + 236, cx, y + 256, YELLOW)
    # Three small warhead cones standing on the ground.
    for i, ox in enumerate((x + 52, x + 112, x + w - 140)):
        cv.triangle(ox, y + h - 62, ox + 22, y + h - 62, ox + 11, y + h - 84, GREY)
        cv.rect(ox, y + h - 62, 22, 26, LIGHTGREY)
    # Ground.
    cv.rect(x, y + h - 24, w, 24, (74, 74, 74))


def draw_tanker_strip(cv, x, y, w, h):
    cv.rect(x, y, w, h // 2, SKY)
    cv.rect(x, y + h // 2, w, h - h // 2, SEA)
    # Tanker hull and containers, left.
    cv.rect(x + 18, y + h - 26, 210, 16, BLACK)
    cv.triangle(x + 228, y + h - 26, x + 262, y + h - 26, x + 228, y + h - 10, BLACK)
    for i, col in enumerate((RED, YELLOW, GREEN, BLUE)):
        cv.rect(x + 30 + i * 46, y + h - 48, 40, 22, col)
    cv.rect(x + 210, y + h - 52, 14, 26, WHITE)
    # Explosion burst above the tanker.
    cv.burst(x + 300, y + 20, 18, ORANGE)
    cv.burst(x + 300, y + 20, 10, YELLOW)
    cv.circle(x + 330, y + 12, 7, GREY)
    cv.circle(x + 342, y + 22, 9, GREY)
    # Naval mine, right, on the water.
    mx, my = x + w - 60, y + h - 12
    for dx, dy in ((-12, 0), (12, 0), (0, -12), (-9, -9), (9, -9), (-9, 9), (9, 9)):
        cv.line(mx, my, mx + dx, my + dy, BLACK)
    cv.circle(mx, my, 9, BLACK)
    # Wave lines.
    cv.hline(x + 10, y + h - 8, 60, WHITE)
    cv.hline(x + 300, y + h - 6, 70, WHITE)


def draw_parade_strip(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    # Giant balloon, centre left.
    bx, by = x + 110, y + h // 2 - 6
    cv.ellipse(bx, by, 64, 34, RED)
    cv.ellipse(bx, by, 22, 34, WHITE)
    cv.ellipse(bx, by, 8, 34, RED)
    cv.line(bx, by + 34, bx, y + h - 14, INK)
    # Rain, diagonal.
    for i in range(9):
        rx = x + 220 + i * 26
        cv.line(rx, y + 6, rx - 12, y + h - 16, BLUE)
    # Street.
    cv.rect(x, y + h - 14, w, 14, GREY)
    # Small deflated balloon on the ground, right.
    cv.ellipse(x + w - 60, y + h - 22, 26, 8, RED)


def draw_boat_strip(cv, x, y, w, h):
    cv.rect(x, y, w, h // 2, SKY)
    cv.rect(x, y + h // 2, w, h - h // 2, SEA)
    # Boat with people.
    bx = x + 60
    cv.rect(bx, y + h - 30, 240, 16, (120, 72, 20))
    cv.triangle(bx + 240, y + h - 30, bx + 268, y + h - 30, bx + 240, y + h - 14, (120, 72, 20))
    cv.vline(bx + 150, y + 8, h - 38, INK)
    cv.triangle(bx + 152, y + 10, bx + 152, y + 44, bx + 196, y + 44, WHITE)
    for i in range(5):
        px = bx + 30 + i * 38
        cv.circle(px, y + h - 44, 7, INK)
        cv.rect(px - 8, y + h - 38, 16, 10, RED if i % 2 else BLUE)
    # Waves.
    cv.hline(x + 320, y + h - 10, 70, WHITE)
    cv.hline(x + 20, y + h - 6, 60, WHITE)


def draw_port_strip(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    # Two port cranes.
    for cx in (x + 90, x + 300):
        cv.rect(cx, y + 10, 10, h - 24, GREY)
        cv.rect(cx - 40, y + 10, 120, 8, GREY)
        cv.line(cx + 5, y + 18, cx + 70, y + h - 14, GREY)
        cv.line(cx + 5, y + 18, cx + 70, y + 30, INK)
    # Explosion at the far crane.
    cv.burst(x + 380, y + 26, 16, ORANGE)
    cv.burst(x + 380, y + 26, 9, YELLOW)
    cv.circle(x + 410, y + 16, 8, GREY)
    # Ground and containers.
    cv.rect(x, y + h - 14, w, 14, GREY)
    cv.rect(x + 180, y + h - 34, 44, 20, RED)
    cv.rect(x + 228, y + h - 34, 44, 20, BLUE)


def draw_plane(cv, x, y, s):
    # Small plane silhouette, s is the pixel scale of the drawing.
    cv.ellipse(x + 22 * s, y + 6 * s, 20 * s, 4 * s, BLUE)
    cv.triangle(x + 38 * s, y + 2 * s, x + 44 * s, y + 2 * s, x + 42 * s, y + 10 * s, BLUE)
    cv.triangle(x + 14 * s, y + 6 * s, x + 26 * s, y + 6 * s, x + 20 * s, y + 14 * s, BLUE)
    cv.triangle(x + 4 * s, y + 4 * s, x + 10 * s, y + 4 * s, x + 6 * s, y + 10 * s, BLUE)

# ---------------------------------------------------------------------------
# Layout: masthead, dateline, ticker, lead story, two rows of two stories,
# and a bottom travel strip with a sources footer.
# ---------------------------------------------------------------------------
def build_page():
    cv = Canvas(W, H, PAPER)

    # Masthead.
    draw_text_centred(cv, W // 2, 20, 7, "THE WORLD TODAY", INK)
    cv.rect(24, 78, 976, 2, INK)
    draw_text_centred(cv, W // 2, 88, 2, "THURSDAY 26 NOVEMBER 2026", INK)
    cv.rect(24, 110, 976, 1, INK)

    # Ticker.
    cv.rect(24, 118, 976, 30, RED)
    draw_text_centred(cv, W // 2, 126, 2,
                      "UN: 5 WOMEN AN HOUR KILLED BY PARTNER OR KIN  //  "
                      "NATO BOOSTS EASTERN AIR WATCH", WHITE)

    # ---- Lead story: Kim and tactical nuclear weapons -------------------
    draw_text(cv, 24, 160, 2, "PYONGYANG - KCNA REPORT, NOV 26", RED)
    draw_text(cv, 24, 182, 4, "KIM: TACTICAL NUKES", INK)
    draw_text(cv, 24, 214, 4, "FOR EVERY MISSION", INK)
    draw_para(cv, 24, 254, 2,
              "NORTH KOREA'S KIM JONG UN TOLD ARMS CHIEFS TO DEPLOY "
              "TACTICAL NUCLEAR WEAPONS ACROSS MANY MISSIONS, STATE MEDIA "
              "SAID THURSDAY, AFTER HE TOURED NUCLEAR MATERIAL PLANTS. "
              "KIM DECLARED THE NORTH'S NUCLEAR STATUS 'ABSOLUTELY "
              "INVIOLABLE'.",
              INK, 576)
    cv.rect(24, 348, 576, 2, RED)
    draw_text(cv, 24, 362, 2, '"OUR NUCLEAR CAPABILITY IS NOW A REALITY"', INK)
    draw_text(cv, 24, 384, 2, "KIM JONG UN, VIA KCNA", GREY)
    draw_missile_panel(cv, 624, 158, 376, 304)

    cv.rect(24, 472, 976, 2, INK)

    # ---- Row 2: Hormuz tankers | Macy's parade ---------------------------
    # Left: Hormuz.
    draw_text(cv, 24, 484, 2, "STRAIT OF HORMUZ", RED)
    draw_text(cv, 24, 506, 3, "THIRD TANKER HITS", INK)
    draw_text(cv, 24, 530, 3, "MINE IN HORMUZ", INK)
    draw_para(cv, 24, 558, 2,
              "AN LNG CARRIER CAUGHT FIRE AFTER STRIKING A NAVAL MINE, "
              "IRAN SAID, HOURS AFTER TWO OIL TANKERS HIT MINES IN THE "
              "SAME WATERS. TEHRAN WARNS SHIPS TO COORDINATE PASSAGE.",
              INK, 476)
    draw_tanker_strip(cv, 24, 644, 476, 56)
    # Right: Macy's parade.
    draw_text(cv, 524, 484, 2, "NEW YORK", RED)
    draw_text(cv, 524, 506, 3, "MACY'S PARADE OFF", INK)
    draw_text(cv, 524, 530, 3, "- A FIRST IN 100 YEARS", INK)
    draw_para(cv, 524, 558, 2,
              "NEW YORK'S 100TH THANKSGIVING PARADE WAS POSTPONED TO "
              "SATURDAY AS A NOR'EASTER BROUGHT GUSTS TO 60 MPH. IT IS "
              "THE FIRST TIME WEATHER HAS EVER MOVED THE PARADE.",
              INK, 476)
    draw_parade_strip(cv, 524, 644, 476, 56)
    cv.vline(512, 484, 216, LIGHTGREY)

    cv.rect(24, 710, 976, 2, INK)

    # ---- Row 3: Canary Islands | Houthis ---------------------------------
    # Left: Canary Islands.
    draw_text(cv, 24, 722, 2, "SPAIN", RED)
    draw_text(cv, 24, 744, 3, "RECORD DAY FOR", INK)
    draw_text(cv, 24, 768, 3, "CANARY ARRIVALS", INK)
    draw_para(cv, 24, 796, 2,
              "NEARLY 2,000 MIGRANTS REACHED SPAIN'S CANARY ISLANDS IN A "
              "SINGLE DAY, THE LARGEST ONE-DAY ARRIVAL ON RECORD, "
              "OFFICIALS SAID.",
              INK, 476)
    draw_boat_strip(cv, 24, 864, 476, 74)
    # Right: Houthis.
    draw_text(cv, 524, 722, 2, "YEMEN", RED)
    draw_text(cv, 524, 744, 3, "HOUTHIS VOW REVENGE", INK)
    draw_text(cv, 524, 768, 3, "AFTER PORT HIT", INK)
    draw_para(cv, 524, 796, 2,
              "YEMEN'S HOUTHIS THREATENED SAUDI PORTS AFTER A COALITION "
              "STRIKE ON THE PORT CITY OF HODEIDAH, AS THE GULF "
              "ESCALATION SPREADS.",
              INK, 476)
    draw_port_strip(cv, 524, 864, 476, 74)
    cv.vline(512, 722, 216, LIGHTGREY)

    cv.rect(24, 948, 976, 2, INK)

    # ---- Bottom strip: Thanksgiving travel + sources ----------------------
    draw_plane(cv, 24, 958, 1)
    draw_text(cv, 84, 958, 2,
              "THANKSGIVING TRAVEL: LONG AIRPORT LINES AND BAD WEATHER", INK)
    draw_text(cv, 84, 976, 2,
              "GRIP THE U.S. AS MILLIONS FLY HOME FOR THE HOLIDAY.", INK)
    draw_text_centred(cv, W // 2, 1002, 1,
                      "SOURCES: KCNA VIA REUTERS AND YONHAP - IRAN STATE "
                      "MEDIA - MACY'S AND NEW YORK CITY - AP - 26 NOV 2026",
                      GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = build_page()
    data = encode_png(cv)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
