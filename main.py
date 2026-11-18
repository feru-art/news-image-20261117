#!/usr/bin/env python3
"""news-image-20261117 — carry the day's front page to the output slot.

The entry image is a finished JPEG (made with Milku's Generate Image) held
in this repository as image.jpg. This program only validates it and copies
its bytes to /output/entry.png. The rules allow a JPEG at that path: the
file is told apart by its first bytes, not by its name.

Standard library only, no network, no clock, no randomness: two runs write
the same bytes.
"""

import os
import sys

SOURCE_NAME = "image.jpg"
OUTPUT_NAME = "entry.png"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"


def repo_dir():
    return os.path.dirname(os.path.abspath(__file__))


def output_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def jpeg_dimensions(data):
    """Read width and height from the first SOF marker (stdlib-only parse).

    Walks the JPEG segments by their declared lengths, so it never mistakes
    entropy-coded data past the scan start for a header.
    """
    pos = 2  # skip the SOI marker
    while pos + 9 <= len(data):
        if data[pos] != 0xFF:
            raise ValueError("bad JPEG marker at offset %d" % pos)
        marker = data[pos + 1]
        if marker in (0xC0, 0xC1, 0xC2):  # SOF0, SOF1, SOF2
            height = int.from_bytes(data[pos + 5:pos + 7], "big")
            width = int.from_bytes(data[pos + 7:pos + 9], "big")
            return width, height
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            pos += 2  # standalone markers carry no length field
            continue
        size = int.from_bytes(data[pos + 2:pos + 4], "big")
        pos += 2 + size
    raise ValueError("no SOF marker found in the JPEG")


def validate(data):
    """Check the image against the competition's gate, return (width, height)."""
    if len(data) > MAX_BYTES:
        raise ValueError("image is %d bytes, over the 1 MiB cap" % len(data))
    if not data.startswith(JPEG_SOI):
        raise ValueError("image does not start with the JPEG SOI marker")
    if not data.endswith(JPEG_EOI):
        raise ValueError("image is truncated: no JPEG end marker")
    width, height = jpeg_dimensions(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("image is %dx%d, over the 1024x1024 cap"
                         % (width, height))
    return width, height


def main():
    source = os.path.join(repo_dir(), SOURCE_NAME)
    with open(source, "rb") as handle:
        data = handle.read()
    width, height = validate(data)
    target_dir = output_dir()
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, OUTPUT_NAME)
    with open(target, "wb") as handle:
        handle.write(data)
    with open(target, "rb") as handle:
        written = handle.read()
    if written != data:
        raise ValueError("written file does not match the source image")
    print("wrote %s (%d bytes, %dx%d JPEG, verified)"
          % (target, len(data), width, height))
    return 0


if __name__ == "__main__":
    sys.exit(main())
