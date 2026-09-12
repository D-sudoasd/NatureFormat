"""Write a 32x32 PNG App icon (Nature red plate + N)."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "origin_app" / "NatureFormat" / "AppIcon.png"

RED = (155, 27, 27, 255)
WHITE = (255, 252, 247, 255)
INK = (28, 25, 23, 255)
CLEAR = (0, 0, 0, 0)


def _chunk(tag: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(tag + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)


def write_png(path: Path, pixels: list[list[tuple[int, int, int, int]]]) -> None:
    height = len(pixels)
    width = len(pixels[0])
    raw = b"".join(b"\x00" + b"".join(bytes(px) for px in row) for row in pixels)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", zlib.compress(raw, 9)) + _chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def make_icon(size: int = 32) -> list[list[tuple[int, int, int, int]]]:
    px = [[CLEAR for _ in range(size)] for _ in range(size)]
    margin = 2
    radius = 5
    for y in range(size):
        for x in range(size):
            if x < margin or y < margin or x >= size - margin or y >= size - margin:
                continue
            dx = min(x - margin, size - 1 - margin - x)
            dy = min(y - margin, size - 1 - margin - y)
            if (dx < radius and dy < radius) and (radius - dx) ** 2 + (radius - dy) ** 2 > radius * radius:
                continue
            px[y][x] = RED
    # simple "N" in white
    for y in range(8, 24):
        px[y][9] = WHITE
        px[y][10] = WHITE
        px[y][21] = WHITE
        px[y][22] = WHITE
        t = (y - 8) / 16
        x = int(10 + t * 11)
        px[y][x] = WHITE
        px[y][min(size - 1, x + 1)] = WHITE
    return px


if __name__ == "__main__":
    write_png(OUT, make_icon())
    print(OUT, OUT.stat().st_size)
