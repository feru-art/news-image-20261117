#!/usr/bin/env python3
"""The World — 17 November 2026 (V6 Dense).

Deterministic entry for news-image-20261117: copies the finished front-page
image — a dense newspaper summary of the day's world news (hero photo of
the burning Kerch bridge, a numbered map strip, six headline cards and an
"18 more stories" list) — to the output path the grader reads.

Standard library only, no network. The picture is copied byte for byte, so
every run writes exactly the same file.
"""

import hashlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PICTURE = HERE / "image.jpg"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024


def jpeg_dimensions(blob: bytes) -> tuple[int, int]:
    """Read width and height from the first SOF marker of a JPEG byte string."""
    pos = 2  # skip the SOI marker
    while pos + 9 <= len(blob):
        if blob[pos] != 0xFF:
            raise ValueError("not a JPEG: marker prefix missing")
        marker = blob[pos + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height = int.from_bytes(blob[pos + 5:pos + 7], "big")
            width = int.from_bytes(blob[pos + 7:pos + 9], "big")
            return width, height
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        length = int.from_bytes(blob[pos + 2:pos + 4], "big")
        pos += 2 + length
    raise ValueError("not a JPEG: no SOF marker found")


def check_picture(blob: bytes) -> tuple[int, int]:
    """Validate the picture against the competition gate; return its size."""
    if len(blob) > MAX_BYTES:
        raise ValueError(f"picture too large: {len(blob)} bytes")
    if not blob.startswith(b"\xff\xd8"):
        raise ValueError("picture lacks the JPEG SOI marker")
    if blob[-2:] != b"\xff\xd9":
        raise ValueError("picture lacks the JPEG EOI end marker")
    width, height = jpeg_dimensions(blob)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"picture too big: {width}x{height}")
    return width, height


def output_path() -> Path:
    base = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    folder = Path(base)
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "entry.png"


def main() -> int:
    blob = PICTURE.read_bytes()
    width, height = check_picture(blob)
    target = output_path()
    target.write_bytes(blob)
    written = target.read_bytes()
    if written != blob:
        raise ValueError("output differs from the picture after writing")
    digest = hashlib.sha256(blob).hexdigest()
    print(f"wrote {target} ({width}x{height}, {len(blob)} bytes, sha256 {digest[:16]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
